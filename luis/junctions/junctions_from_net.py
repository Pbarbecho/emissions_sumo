import xml.etree.ElementTree as ET
import csv
from pathlib import Path

# Usamos la ruta del proyecto
OUTPUT_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/outputs")
SIM_FILES_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/mapa/sim_files")


def process_net_xml(input_file, output_csv):
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()

        junctions_list = []
        stats = {
            'real': 0,
            'internal': 0
        }

        # Extraer datos
        for junction in root.findall('junction'):
            j_id = junction.get('id')
            j_type = junction.get('type')

            # Clasificación para estadísticas
            is_internal = j_id.startswith(':') or j_type == 'internal'

            if is_internal:
                stats['internal'] += 1
                # Si de quiere incluir las internas en el CSV, comenta la siguiente línea:
                continue

            stats['real'] += 1

            # Guardar datos de junctions reales
            junctions_list.append({
                'id': j_id,
                'x': junction.get('x'),
                'y': junction.get('y'),
                'type': j_type
            })

        # Crear el archivo CSV
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'x', 'y', 'type'])
            writer.writeheader()
            writer.writerows(junctions_list)

        # Imprimir estadísticas
        total = stats['real'] + stats['internal']
        print("--- ESTADÍSTICAS DE LA RED ---")
        print(f"Junctions reales filtradas:  {stats['real']}")
        print(f"Junctions internas ocultas:  {stats['internal']}")
        print(f"Total procesadas en XML:    {total}")
        print(f"------------------------------")
        print(f"Archivo guardado exitosamente como: {output_csv}")

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")


if __name__ == "__main__":

    # Configuración
    ARCHIVO_ENTRADA = SIM_FILES_PATH /'uio.net.xml'
    ARCHIVO_SALIDA =OUTPUT_PATH / 'junctions.csv'

    process_net_xml(ARCHIVO_ENTRADA, ARCHIVO_SALIDA)