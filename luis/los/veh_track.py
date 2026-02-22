import csv
from pathlib import Path

# Usamos la ruta del proyecto
OUTPUT_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/outputs")
SIM_FILES_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/mapa/sim_files")

# -------- CONFIGURACION --------
INPUT_CSV = OUTPUT_PATH / "los.csv"
OUTPUT_CSV = OUTPUT_PATH / "veh_track.csv"
VEHICLE_ID_TO_FILTER = "A0"
DELIMITER = ';'
# -------------------------------


def filter_vehicle(input_file, output_file, vehicle_id):

    with open(input_file) as infile:
        reader = csv.DictReader(infile, delimiter=DELIMITER)

        with open(output_file, "w", newline="") as outfile:
            writer = csv.DictWriter(
                outfile,
                fieldnames=reader.fieldnames,
                delimiter=DELIMITER
            )

            writer.writeheader()

            count = 0
            for row in reader:
                if row["vehicle_id"] == vehicle_id:
                    writer.writerow(row)
                    count += 1

    print(f"Filas encontradas para {vehicle_id}: {count}")
    print(f"Archivo guardado en: {output_file}")


if __name__ == "__main__":
    filter_vehicle(INPUT_CSV, OUTPUT_CSV, VEHICLE_ID_TO_FILTER)
