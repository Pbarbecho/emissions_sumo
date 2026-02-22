import csv
import xml.etree.ElementTree as ET
from shapely.geometry import Point, Polygon, LineString
from multiprocessing import Pool, cpu_count
import itertools
import pandas as pd
from pathlib import Path

##### Selecciona la jucntion mas cercana y verifica LOS entre el veh y dicha junction
##### Utilizo el fcd output en formato cvs. Entonces considera todos los vehicles e instantes de tiempo

# --- variables globales para workers ---
POLYGONS = None
JUNCTIONS = None

# Usamos la ruta del proyecto
OUTPUT_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/outputs")
SIM_FILES_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/mapa/sim_files")


def init_worker(polygons, junctions):
    global POLYGONS, JUNCTIONS
    POLYGONS = polygons
    JUNCTIONS = junctions


def process_row(row):

    vx = float(row["vehicle_x"])
    vy = float(row["vehicle_y"])

    v_point = Point(vx, vy)
    nearest = nearest_junction(v_point, JUNCTIONS)
    j_point = nearest["point"]

    # distancia euclidiana
    distance = round(v_point.distance(j_point), 2) # 2 decimales
    los = has_los(v_point, j_point, POLYGONS)

    # arma output
    row["los"] = int(los)
    row["junt_id"] = nearest["id"]
    row["junt_x"] = j_point.x
    row["junt_y"] = j_point.y
    row["dist_to_junct"] = distance
    return row

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


# ---------- encontrar junction mas cercano ----------
def nearest_junction(point, junctions):
    return min(junctions, key=lambda j: point.distance(j["point"]))


# ---------- evaluar LoS ----------
def has_los(vehicle_point, junction_point, polygons):
    segment = LineString([vehicle_point, junction_point])
    for poly in polygons:
        if segment.intersects(poly):
            return False
    return True

def flatten_junction(j):
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

    df = pd.DataFrame([flatten_junction(j) for j in junctions])
    df.to_csv(OUTPUT_PATH / "junctions_validas.csv", index=False)

    with open(csv_fcd) as f:
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
