import csv
import xml.etree.ElementTree as ET
from shapely.geometry import Point, Polygon, LineString
from multiprocessing import Pool, cpu_count
import itertools
import pandas as pd
from pathlib import Path

##### Selecciona las jucntions en un radio de covertura  y verifica LOS entre el veh y dicha junction
##### Utilizo el fcd output en formato cvs. Entonces considera todos los vehicles e instantes de tiempo

# --- variables globales para workers ---
POLYGONS = None
JUNCTIONS = None
RADIUS_DISTANCE = 100

# Usamos la ruta del proyecto
OUTPUT_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/outputs")
SIM_FILES_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/mapa/sim_files")


def init_worker(polygons, junctions):
    global POLYGONS, JUNCTIONS
    POLYGONS = polygons
    JUNCTIONS = junctions


def process_row(row):

    max_distance = RADIUS_DISTANCE ## radio de cobertura
    vx = float(row["vehicle_x"])
    vy = float(row["vehicle_y"])

    v_point = Point(vx, vy)

    # verfica el conjunto de juntions en un radio de cobertura
    junctions_in_coverage = junctions_within_radio_distance(v_point, JUNCTIONS, max_distance)

    results = []
    for j in junctions_in_coverage:
        j_point = j["point"]

        # distancia euclidiana
        distance = round(v_point.distance(j_point), 2)

        # linea de vista
        los = has_los(v_point, j_point, POLYGONS)

        # arma output
        #row["los"] = int(los)
        #row["j_id"] = j["id"]
        #row["j_x"] = j_point.x
        #row["j_y"] = j_point.y
        #row["dst_to_j"] = distance

        results.append({
            "timestep_time": row["timestep_time"],
            "vehicle_id": row["vehicle_id"],
            "junction_id": j["id"],
            "distance": distance,
            "j_x": j_point.x,
            "j_y": j_point.y,
            "los": los
        })
    print(results)
    return results


# ---------- cargar poligonos ----------
def load_polygons(poly_file):
    tree = ET.parse(poly_file)
    root = tree.getroot()
    polygons = []

    for poly in root.findall("poly"):
        shape = poly.get("shape")
        if not shape:
            continue

        coords = [
            (float(x), float(y))
            for x, y in [p.split(",") for p in shape.split()]
        ]

        # shapely necesita al menos 3 puntos únicos
        if len(coords) < 3:
            continue

        # cerrar poligono si no esta cerrado
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        try:
            polygon = Polygon(coords)

            # evitar poligonos degenerados
            if polygon.is_valid and polygon.area > 0:
                polygons.append(polygon)

        except Exception as e:
            print(f" Poligono ignorado: {e}")

    print(f"Poligonos validos cargados: {len(polygons)}")
    return polygons


# ---------- cargar junctions desde CSV ----------
def load_junctions_csv(junction_file):
    junctions = []
    with open(junction_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # filtrar solo traffic light
            if row["type"].lower() != "traffic_light":  ###### SOLO CONSIDERAMOS JUNCTIONS DEL TIPO traffic_light
                continue                                ###########################################################
            j = {
                "id": row["id"],
                "point": Point(float(row["x"]), float(row["y"])),
                "type": row["type"]
            }
            junctions.append(j)

    return junctions

# ---------- junctions dentro de un radio ----------
def junctions_within_radio_distance(point, junctions, max_distance):
    """
    point: objeto Point actual
    junctions: lista de dicts con {"id", "point", "type"}
    max_distance: distancia máxima (float)

    retorna: lista de ids de junctions dentro del radio
    """
    return [
        j
        for j in junctions
        if point.distance(j["point"]) <= max_distance
    ]


# ---------- evaluar LoS ----------
def has_los(vehicle_point, junction_point, polygons):
    segment = LineString([vehicle_point, junction_point])
    for poly in polygons:
        if segment.intersects(poly):
            return False
    return True


def flatten_junction(j):
    ## graba las junctions consideradas en e lanalisis en un csv en output
    flat = {}
    for k, v in j.items():
        if v is None:
            flat[k] = None
        elif hasattr(v, "x") and hasattr(v, "y"):
            flat[f"{k}_x"] = v.x
            flat[f"{k}_y"] = v.y
        else:
            flat[k] = v
    return flat

def process(csv_fcd, poly_file, junction_file, output_file):

    polygons = load_polygons(poly_file)
    junctions = load_junctions_csv(junction_file)

    # guardar junctions válidas
    df = pd.DataFrame([flatten_junction(j) for j in junctions])
    df.to_csv(OUTPUT_PATH / "junctions_validas.csv", index=False)

    # leer FCD
    with open(csv_fcd) as f:
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)

    # --- procesamiento secuencial ---
    results = []
    init_worker(polygons, junctions)  # si tu función usa variables globales

    for row in rows:
        result = process_row(row)
        results.append(result)

    # --- escribir resultado ---
    with open(output_file, "w", newline="") as out:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(results)



def process(csv_fcd, poly_file, junction_file, output_file):

    polygons = load_polygons(poly_file)
    junctions = load_junctions_csv(junction_file)

    df = pd.DataFrame([flatten_junction(j) for j in junctions])
    df.to_csv(OUTPUT_PATH / "junctions_validas.csv", index=False)

    with open(csv_fcd) as f: ##### CADA ENTRADA EN EL OUTPUT FCD
        reader = csv.DictReader(f, delimiter=';')
        rows = list(reader)

    with Pool(
        processes=cpu_count(),
        initializer=init_worker,
        initargs=(polygons, junctions)
    ) as pool:

        results = pool.map(process_row, rows)

    # --- escribir resultado ---
    with open(output_file, "w", newline="") as out:
        fieldnames = list(results[0].keys())
        writer = csv.DictWriter(out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":

    fcd_csv = OUTPUT_PATH / "fcd.csv"
    poly = SIM_FILES_PATH / "uio.poly.xml"
    junctions_csv = OUTPUT_PATH / "junctions.csv"
    los_output = OUTPUT_PATH / "los.csv"

    process(fcd_csv, poly , junctions_csv , los_output)
