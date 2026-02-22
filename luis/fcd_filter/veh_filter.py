import xml.etree.ElementTree as ET
from pathlib import Path


# Usamos la ruta del proyecto
OUTPUT_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/outputs")
SIM_FILES_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/mapa/sim_files")


# -------- CONFIGURACION --------
INPUT_FCD = OUTPUT_PATH / "fcd.xml"
OUTPUT_FCD = OUTPUT_PATH / "fcd_vehicle.xml"        # archivo filtrado
VEHICLE_ID = "A0"                         # id del vehículo a filtrar
# -------------------------------


def filter_fcd_vehicle(input_file, output_file, vehicle_id):

    tree = ET.parse(input_file)
    root = tree.getroot()

    # crear nuevo root
    new_root = ET.Element(root.tag, root.attrib)

    total = 0

    for timestep in root.findall("timestep"):
        time = timestep.get("time")

        # crear timestep nuevo
        new_timestep = ET.Element("timestep", {"time": time})

        for vehicle in timestep.findall("vehicle"):
            if vehicle.get("id") == vehicle_id:
                new_timestep.append(vehicle)
                total += 1

        # solo agregar timestep si tiene el vehiculo
        if len(new_timestep):
            new_root.append(new_timestep)

    # guardar archivo
    new_tree = ET.ElementTree(new_root)
    new_tree.write(output_file, encoding="utf-8", xml_declaration=True)

    print(f"Vehículo filtrado: {vehicle_id}")
    print(f"Registros encontrados: {total}")
    print(f"Archivo guardado en: {output_file}")


if __name__ == "__main__":
    filter_fcd_vehicle(INPUT_FCD, OUTPUT_FCD, VEHICLE_ID)
