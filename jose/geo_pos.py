import traci
import requests
from pathlib import Path


# Usamos la ruta del proyecto
OUTPUT_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/outputs")
SIM_FILES_PATH = Path("/home/pablo/Sumo/Vinculacion/SUMO_vinculacion/pablo/emissions_sumo/luis/mapa/sim_files")


# 1. Inicia SUMO (puedes usar 'sumo-gui' para verlo visualmente)
sumo_binary = "sumo-gui"
conf_file = SIM_FILES_PATH / "osm.sumocfg"  # Tu archivo de configuración


def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    response = requests.get(url).json()
    return response['results'][0]['elevation']

traci.start([sumo_binary, "-c", conf_file])

step = 0
while step < 1000:  # Simular 1000 pasos
    traci.simulationStep()
    # Obtener lista de todos los vehículos activos
    vehicle_ids = traci.vehicle.getIDList()
    for veh_id in vehicle_ids:
        # probamos para el veh A0
        if veh_id == "A0":

            #  get posición  de SUMO (x, y en metros UTM del archivo .net)
            x, y = traci.vehicle.getPosition(veh_id)

            # Convertir x,y a Longitud,Latitud
            lon, lat = traci.simulation.convertGeo(x, y)

            # consulta altitud en linea
            altitud = get_elevation(lat, lon)

            print(f"Time:{traci.simulation.getTime()} | Step: {step}  |  Vehículo: {veh_id} |x: {x}  | y={y}  | Lon: {lon:.6f} | Lat: {lat:.6f} | Altura:{altitud}")
    step += 1
traci.close()