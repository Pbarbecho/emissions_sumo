import os
import subprocess
import sys
from pathlib import Path

# Usamos la ruta del proyecto
OUTPUT_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/outputs")
SIM_FILES_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/mapa/sim_files")

def ejecutar_simulacion_sumo(config_file):
    # 1. Verificar si SUMO_HOME está definido
    if 'SUMO_HOME' not in os.environ:
        print("Error: La variable de entorno 'SUMO_HOME' no está definida.")
        sys.exit(1)

    sumo_bin = "sumo"
    script_xml2csv = os.path.join(os.environ['SUMO_HOME'], 'tools', 'xml', 'xml2csv.py')

    # Asumimos que el fcd-output se llama uio_fcd.xml
    fcd_output_xml = OUTPUT_PATH / "fcd.xml"
    fcd_output_csv = OUTPUT_PATH / "fcd.csv"

    try:
        # 2. Ejecutar la simulación
        print(f"--- Iniciando simulación con {config_file} ---")
        # El comando incluye --fcd-output por si no está en el .cfg
        subprocess.run([sumo_bin, "-c", config_file], check=True)
        print("Simulación finalizada con éxito.")

        # 3. Convertir XML a CSV
        print(f"--- Convirtiendo {fcd_output_xml} a CSV ---")
        if os.path.exists(fcd_output_xml):
            subprocess.run(["python3", script_xml2csv, fcd_output_xml, "-o", fcd_output_csv], check=True)
            print(f"Archivo convertido: {fcd_output_csv}")
        else:
            print(f"Error: No se encontró el archivo de salida {fcd_output_xml}")

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar un comando: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


if __name__ == "__main__":
    # Verificar path relativo del proyecto
    mi_configuracion = SIM_FILES_PATH / "osm.sumocfg"
    ejecutar_simulacion_sumo(mi_configuracion)