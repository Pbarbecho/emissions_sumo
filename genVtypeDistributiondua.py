import xml.etree.ElementTree as ET
import random
import matplotlib.pyplot as plt
import sys
import os
import pandas as pd
import uuid
from xml.dom import minidom

# Función para leer la distribucion de los tipos de vehiculos
def read_vtypes_distribution(vtypesDistribution):
    df = pd.read_csv(vtypesDistribution, index_col=1)  # Asegúrate que el archivo esté en el mismo directorio o da la ruta completa
    df = df.drop("No", axis=1)
    # Convertir a diccionario
    return df["Valor"].to_dict()

# Función para crear la carpeta si no existe
def crear_carpeta_si_no_existe(carpeta):
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

# Función para leer el archivo XML y modificar el tipo de vehículo
def modify_vehicle_types(input_xml, output_xml):
    tree = ET.parse(input_xml)
    root = tree.getroot()

    partes = input_xml.split('/')
    nombre_archivo = partes[-1]
    # Si quieres eliminar la extensión .xml, puedes hacer esto
    nombre = nombre_archivo.split('.')[0]
    print("El nombre del archivo es:", nombre)	    

    
    #vehicles = root.findall('flow')
    if(nombre=='duarouter'):
      #print(nombre)
      vehicles = root.findall('vehicle')
    if(nombre=='marouter'):
      vehicles = root.findall('flow')
      print("Ingreso a al funcion",nombre)
      	
#    print("El valor de vehiculo es",vehicles)	
#    vehicles = root.findall('vehicle')
    total_vehicles = len(vehicles)
    print(f'Total vehicles found: {total_vehicles}')

    # Generar una lista de tipos de vehículos basada en los porcentajes
    vehicle_types = []
    for vehicle_type, percentage in percentages.items():
        count = int(percentage * total_vehicles)
        vehicle_types.extend([vehicle_type] * count)

    # Asegurarnos de que la lista de tipos tenga la longitud correcta
    while len(vehicle_types) < total_vehicles:
        vehicle_types.append("chevrolet_aveo")  # Por si acaso hay algún remanente

    # Asignar aleatoriamente los tipos de vehículo a cada <vehicle>
    random.shuffle(vehicle_types)
    for i, vehicle in enumerate(vehicles):
        new_type = vehicle_types[i]
        vehicle.set('type', new_type)

    # Guardar el archivo modificado
    tree.write(output_xml)

    print(f'Modification complete. Modified XML saved as "{output_xml}".')

    return vehicle_types, total_vehicles


def plot_vtypes_distr(expected_distribution , total_vehicles,  conteo_por_tipo , carpeta):

    # 1. Convertir diccionario en DataFrame
    df_expected = pd.DataFrame(list(expected_distribution.items()), columns=["type", "expected_prob"])

    # 2. Suponiendo que ya tienes este DataFrame de conteos reales
    # conteo_por_tipo: columnas = ["type", "cantidad"]
    df_real = conteo_por_tipo.copy()

    # 3. Unir los DataFrames por "type"
    df_comparado = pd.merge(df_expected, df_real, on="type", how="left")
    df_comparado["cantidad"] = df_comparado["cantidad"].fillna(0)

    # 4. Calcular proporción real (observada)
    total = df_comparado["cantidad"].sum()
    df_comparado["observed_prob"] = df_comparado["cantidad"] / total

    # 5. Plot comparativo
    plt.figure(figsize=(12, 6))
    x = range(len(df_comparado))

    plt.bar(x, df_comparado["expected_prob"], width=0.4, label="Esperado", align="center")
    plt.bar([i + 0.4 for i in x], df_comparado["observed_prob"], width=0.4, label="Generada", align="center")

    plt.xticks([i + 0.2 for i in x], df_comparado["type"], rotation=90)
    plt.ylabel("Porcentaje")
    plt.title(f"Distribución de Vehículos esperada vs generados. Total generado {total_vehicles}")
    plt.legend()
    plt.tight_layout()

    # Guardar la figura en la carpeta especificada
    ruta_figura = os.path.join(carpeta, 'distri_veh_vs_dua_rou.png')
    plt.savefig(ruta_figura)
    plt.close()


def modify_vtypes_dua(tipos, rutas, output):
    # Extraer listas de tipos y probabilidades

    nombres = list(tipos.keys())  # ['chevrolet_aveo', 'chevrolet_spark', ...]
    probabilidades = list(tipos.values())  # [0.08, 0.06, 0.06, 0.05]

    # Cargar el archivo XML
    tree = ET.parse(rutas)  # Cambia por la ruta real del archivo
    root = tree.getroot()

    # Recorrer los elementos <vehicle> y asignar un nuevo tipo aleatorio
    for vehiculo in root.findall("vehicle"):
        nuevo_tipo = random.choices(nombres, weights=probabilidades, k=1)[0]
        vehiculo.set("type", nuevo_tipo)

    # Guardar el resultado
    tree.write(output, encoding="utf-8", xml_declaration=True)


def count_rutas_rou(rutas_xml):
    # Cargar el archivo XML
    tree = ET.parse(rutas_xml)  # ← Cambia por el nombre de tu archivo
    root = tree.getroot()

    # Inicializar lista para tipos
    tipos = []

    # Recorrer todos los elementos <vehicle>
    for vehiculo in root.findall("vehicle"):
        tipo = vehiculo.get("type")
        if tipo:
            tipos.append(tipo)

    # 1. Total de vehículos
    total_vehiculos = len(tipos)
    print(f"Total de vehículos: {total_vehiculos}")

    # 2. Crear DataFrame con conteo por tipo
    df = pd.DataFrame(tipos, columns=["type"])
    conteo_por_tipo = df["type"].value_counts().reset_index()
    conteo_por_tipo.columns = ["type", "cantidad"]
    return total_vehiculos, conteo_por_tipo


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Uso: python genVtypesDistributiondua.py <vtypes csv> <rutas.dua.xml> <rutas_m.dua.xml> <plots_dir>")
        sys.exit(1)

    vtypesdist = sys.argv[1]
    input_xml = sys.argv[2]
    output_xml = sys.argv[3]
    carpeta=sys.argv[4]

    # leer el archivo donde se indica la distribucion de cada tipo de vehiculo
    percentages_real = read_vtypes_distribution(vtypesdist)

    # asigna nuevo vtype tomando en cuentra la probaibilidaddel vtypedistribution.csv
    modify_vtypes_dua(percentages_real, input_xml, output_xml)

    # cuenta el resutlado de modificar el rutas.rou con ladistribucion real
    total_veh_rou , per_vehicle_rou = count_rutas_rou(output_xml)

    # Genera plot de vtypes ditribution
    crear_carpeta_si_no_existe(carpeta)
    plot_vtypes_distr(percentages_real , total_veh_rou, per_vehicle_rou, carpeta)



