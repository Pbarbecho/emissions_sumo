import xml.etree.ElementTree as ET
import pandas as pd
import argparse

# Configurar el analizador de argumentos
parser = argparse.ArgumentParser(description="Extraer datos de un archivo XML y guardarlos en un archivo Excel.")
parser.add_argument('input_xml', type=str, help="Ruta del archivo XML de entrada.")
parser.add_argument('output_excel', type=str, help="Ruta del archivo Excel de salida.")

# Parsear los argumentos
args = parser.parse_args()

# Parsear el archivo XML
tree = ET.parse(args.input_xml)
root = tree.getroot()

# Listas para almacenar los datos extraídos
ids = []
durations = []
route_lengths = []
vtypes = []
co_abs = []
co2_abs = []
hc_abs = []
pmx_abs = []
nox_abs = []

# Iterar sobre cada elemento <tripinfo>
for tripinfo in root.findall('tripinfo'):
    # Extraer los atributos necesarios
    id_vehiculo = tripinfo.attrib['id']
    duration = tripinfo.attrib['duration']
    route_length = tripinfo.attrib['routeLength']
    vtype = tripinfo.attrib['vType']

    # Encontrar el subelemento <emissions>
    emissions = tripinfo.find('emissions')
    co = emissions.attrib['CO_abs']
    co2 = emissions.attrib['CO2_abs']
    hc = emissions.attrib['HC_abs']
    pmx = emissions.attrib['PMx_abs']
    nox = emissions.attrib['NOx_abs']

    # Añadir los datos a las listas
    ids.append(id_vehiculo)
    durations.append(duration)
    route_lengths.append(route_length)
    vtypes.append(vtype)
    co_abs.append(co)
    co2_abs.append(co2)
    hc_abs.append(hc)
    pmx_abs.append(pmx)
    nox_abs.append(nox)

# Crear un DataFrame de pandas con los datos
df = pd.DataFrame({
    'ID': ids,
    'Duration': durations,
    'RouteLength': route_lengths,
    'VType': vtypes,
    'CO_abs': co_abs,
    'CO2_abs': co2_abs,
    'HC_abs': hc_abs,
    'PMx_abs': pmx_abs,
    'NOx_abs': nox_abs
})

# Guardar el DataFrame en un archivo Excel
df.to_excel(args.output_excel, index=False)

print(f"Datos exportados a '{args.output_excel}'")

