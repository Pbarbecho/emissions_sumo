'''import xml.etree.ElementTree as ET

# Cargar y parsear el archivo XML
tree = ET.parse('reportes/tripinfo.xml')
root = tree.getroot()

# Crear una lista para almacenar los datos
data = []

# Iterar sobre todos los elementos 'tripinfo' y extraer los atributos deseados
for tripinfo in root.findall('tripinfo'):
    departLane = tripinfo.get('departLane').split('_')[0]
    arrivalLane = tripinfo.get('arrivalLane').split('_')[0]
    data.append([departLane, arrivalLane])

# Imprimir los datos extraídos
for row in data:
    print(row)

#print(data)'''


'''
archivo_tripinfos = 'reportes/tripinfo.xml'
archivo_taz = 'districts.taz.xml'
archivo_texto = 'saturno_7.00_8.00/saturno_7.00_8.00.od'
'''

'''import xml.etree.ElementTree as ET
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd

# Función para extraer IDs de tripinfos.xml
def extraer_ids_tripinfos(archivo_tripinfos):
    tree = ET.parse(archivo_tripinfos)
    root = tree.getroot()
    ids = []

    for tripinfo in root.findall('tripinfo'):
        departLane = tripinfo.get('departLane').split('_')[0]
        arrivalLane = tripinfo.get('arrivalLane').split('_')[0]
        ids.append((departLane, arrivalLane))

    return ids

# Función para mapear IDs a TAZs
def mapear_ids_a_taz(archivo_taz):
    id_to_taz = {}

    tree = ET.parse(archivo_taz)
    root = tree.getroot()

    for taz in root.findall('taz'):
        taz_id = taz.get('id')
        taz_edges = taz.get('edges').split()
        
        for edge in taz_edges:
            id_to_taz[edge] = taz_id

    return id_to_taz

# Función para reemplazar IDs por TAZs y contar apariciones de pares TAZ
def contar_pares_taz(ids, id_to_taz):
    taz_pair_count = defaultdict(int)

    for departLane, arrivalLane in ids:
        origen_taz = id_to_taz.get(departLane, None)
        destino_taz = id_to_taz.get(arrivalLane, None)
        
        if origen_taz and destino_taz:
            taz_pair_count[(origen_taz, destino_taz)] += 1

    return taz_pair_count

# Función para leer y procesar el archivo de texto adicional
def leer_datos_adicionales(archivo_texto):
    datos = []
    with open(archivo_texto, 'r') as file:
        lines = file.readlines()[5:]  # Omitir las primeras 5 líneas
        for line in lines:
            if len(line.split()) == 3:  # Asegurarse de que la línea tenga exactamente 3 campos
                datos.append(line.split())

    return pd.DataFrame(datos, columns=['TAZ_Origen', 'TAZ_Destino', 'Count'])

# Archivos
archivo_tripinfos = 'reportes/tripinfo.xml'
archivo_taz = 'districts.taz.xml'
archivo_texto = 'simple_07_08/simple_07_08.od'

# Extraer IDs del archivo tripinfos.xml
ids = extraer_ids_tripinfos(archivo_tripinfos)

# Crear el mapeo de IDs a TAZs
id_to_taz = mapear_ids_a_taz(archivo_taz)

# Contar apariciones de pares TAZ (origen, destino)
taz_pair_counts = contar_pares_taz(ids, id_to_taz)

# Leer y procesar los datos adicionales
datos_adicionales = leer_datos_adicionales(archivo_texto)

# Convertir la columna 'Count' a entero
datos_adicionales['Count'] = datos_adicionales['Count'].astype(int)

# Organizar los datos por TAZ de origen
origen_destino_dict = defaultdict(list)
for (origen_taz, destino_taz), count in taz_pair_counts.items():
    origen_destino_dict[origen_taz].append((destino_taz, count))

# Conjunto de TAZ de origen en los datos adicionales
taz_adicionales_origen = set(datos_adicionales['TAZ_Origen'].unique())

# Crear gráficos de dispersión y de barras superpuestos
for origen_taz, destinos in origen_destino_dict.items():
    destinos_taz = [destino_taz for destino_taz, count in destinos]
    counts = [count for destino_taz, count in destinos]
    
    plt.figure(figsize=(12, 8))
    
    # Gráfico de dispersión
    scatter = plt.scatter(destinos_taz, counts, color='blue', label='Datos Simulacion')
    
    # Añadir etiquetas a los puntos
    for destino_taz, count in destinos:
        plt.text(destino_taz, count, str(count), fontsize=9, ha='right', color='blue')
    
    # Añadir datos adicionales como barras
    datos_origen = datos_adicionales[datos_adicionales['TAZ_Origen'] == origen_taz]
    if not datos_origen.empty:
        bar = plt.bar(datos_origen['TAZ_Destino'], datos_origen['Count'], color='orange', alpha=0.5, label='Datos Originales', width=0.3)
        for _, row in datos_origen.iterrows():
            destino_taz = row['TAZ_Destino']
            count = row['Count']
            plt.text(destino_taz, count, str(count), fontsize=9, ha='left', color='orange')

    plt.title(f'Conteo de vehículos desde TAZ Origen: {origen_taz}')
    plt.xlabel('TAZ Destino')
    plt.ylabel('Conteo de Vehículos')
    plt.xticks(rotation=45)
    
    # Añadir la leyenda
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    
    plt.tight_layout()
#plt.show()

# Crear gráficos de barras solo para los TAZ de origen que no están en los datos XML
taz_no_en_xml = taz_adicionales_origen - set(origen_destino_dict.keys())

for taz_origen in taz_no_en_xml:
    datos_origen = datos_adicionales[datos_adicionales['TAZ_Origen'] == taz_origen]
    destinos_taz = datos_origen['TAZ_Destino'].tolist()
    counts = datos_origen['Count'].tolist()

    plt.figure(figsize=(12, 8))

    # Gráfico de barras
    bar = plt.bar(destinos_taz, counts, color='orange', alpha=0.7, label='Datos Originales', width=0.3)
    for destino_taz, count in zip(destinos_taz, counts):
        plt.text(destino_taz, count, str(count), fontsize=9, ha='center', color='orange')

    plt.title(f'Conteo de vehículos desde TAZ Origen: {taz_origen}')
    plt.xlabel('TAZ Destino')
    plt.ylabel('Conteo de Vehículos')
    plt.xticks(rotation=45)
    
    # Añadir la leyenda
    plt.legend()
    
    plt.tight_layout()

plt.show()
'''



import os
import argparse
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import xml.etree.ElementTree as ET

# Función para crear la carpeta si no existe
def crear_carpeta_si_no_existe(carpeta):
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

# Función para leer el archivo XML y extraer la información de los vehículos
def leer_datos_xml(archivo_xml):
    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
        datos_vehiculos = []
        for vehicle in root.findall('vehicle'):
            from_taz = vehicle.get('fromTaz')
            to_taz = vehicle.get('toTaz')
            datos_vehiculos.append((from_taz, to_taz))
        return datos_vehiculos
    except ET.ParseError as e:
        print(f"Error al parsear el archivo XML: {e}")
        return []
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo XML: {e}")
        return []

# Función para leer el archivo de datos adicionales
def leer_datos_adicionales(archivo_texto):
    try:
        datos_adicionales = pd.read_csv(archivo_texto, sep='\s+', skiprows=8, header=None)
        datos_adicionales.columns = ['from_taz', 'to_taz', 'count']
        return datos_adicionales
    except pd.errors.ParserError as e:
        print(f"Error al leer el archivo de datos adicionales: {e}")
        return pd.DataFrame(columns=['from_taz', 'to_taz', 'count'])

# Función para contar los pares de TAZ origen y destino
def contar_taz(datos_vehiculos):
    conteo_taz = defaultdict(int)
    for from_taz, to_taz in datos_vehiculos:
        conteo_taz[(from_taz, to_taz)] += 1
    return conteo_taz

# Función para leer el valor de 'teleports' del último <step> en summary.xml
def leer_teleports_summary(archivo_summary):
    try:
        tree = ET.parse(archivo_summary)
        root = tree.getroot()
        last_step = root.findall('step')[-1]
        teleports = int(last_step.get('teleports', 0))
        return teleports
    except ET.ParseError as e:
        print(f"Error al parsear el archivo XML: {e}")
        return 0
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo XML: {e}")
        return 0

# Función para graficar los resultados
def graficar_conteo_taz(conteo_taz, datos_adicionales, teleports, carpeta):
    taz_origen_destino = defaultdict(list)
    for (from_taz, to_taz), count in conteo_taz.items():
        taz_origen_destino[from_taz].append((to_taz, count))
    
    for origen, destinos in taz_origen_destino.items():
        destinos_taz, counts = zip(*destinos)
        
        plt.figure(figsize=(12, 8))
        
        # Gráfico de dispersión
        plt.scatter(destinos_taz, counts, color='red', alpha=0.7, label='Datos simulacion', s=100)
        for destino_taz, count in zip(destinos_taz, counts):
            plt.text(destino_taz, count, str(count), fontsize=9, ha='left', color='red')
        
        # Filtrar datos adicionales para el TAZ origen actual
        datos_adicionales_origen = datos_adicionales[datos_adicionales['from_taz'] == origen]
        
        if not datos_adicionales_origen.empty:
            destinos_adicionales = datos_adicionales_origen['to_taz'].tolist()
            counts_adicionales = datos_adicionales_origen['count'].tolist()
            
            # Gráfico de barras
            bar = plt.bar(destinos_adicionales, counts_adicionales, color='black', alpha=0.7, label='Matriz OD', width=0.2)
            for destino_taz, count in zip(destinos_adicionales, counts_adicionales):
                plt.text(destino_taz, count, str(count), fontsize=9, ha='right', color='black')
        
        plt.title(f'Conteo de vehículos desde TAZ Origen: {origen}')
        plt.xlabel('TAZ Destino')
        plt.ylabel('Conteo de Vehículos')
        plt.xticks(rotation=90)
        
        # Añadir la leyenda
        plt.legend()
        
        plt.tight_layout()
        # Guardar la figura en la carpeta especificada
        ruta_figura = os.path.join(carpeta, f'conteo_{origen}.png')
        plt.savefig(ruta_figura)
        plt.close()

    # Contar el número total de vehículos en el archivo XML
    total_vehiculos_xml = sum(count for _, count in conteo_taz.items())
    print(f"Total de vehículos en la simulacion: {total_vehiculos_xml}")

    # Contar el número total de vehículos en el archivo adicional
    total_vehiculos_adicional = datos_adicionales['count'].sum()
    print(f"Total de vehículos en la matriz OD: {total_vehiculos_adicional}")

    # Gráfico de barras para el total de vehículos y teleports
    plt.figure(figsize=(8, 6))
    categorias = ['Vehículos Matriz OD', 'Vehículos Simulados', 'Teleports']
    valores = [total_vehiculos_adicional, total_vehiculos_xml, teleports]

    plt.bar(categorias, valores, color=['black', 'red', 'blue'])
    for i, valor in enumerate(valores):
        plt.text(i, valor, str(valor), ha='center', va='bottom', fontsize=12)

    plt.title('Comparación de Vehículos y Teleports')
    plt.ylabel('Conteo')

    plt.tight_layout()
    ruta_figura = os.path.join(carpeta, 'comparacion_vehiculos_teleports.png')
    plt.savefig(ruta_figura)
    plt.close()

# Función principal
def main():
    parser = argparse.ArgumentParser(description="Procesar archivos XML y datos adicionales para graficar conteos de vehículos.")
    parser.add_argument("archivo_xml", type=str, help="Ruta al archivo XML.")
    parser.add_argument("archivo_texto", type=str, help="Ruta al archivo de datos adicionales.")
    parser.add_argument("archivo_summary", type=str, help="Ruta al archivo summary.xml.")
    parser.add_argument("carpeta_figuras", type=str, help="Carpeta donde se guardarán las figuras.")
    
    args = parser.parse_args()
    
    # Crear la carpeta si no existe
    crear_carpeta_si_no_existe(args.carpeta_figuras)
    
    # Leer y procesar los datos del archivo XML y del archivo de datos adicionales
    datos_vehiculos = leer_datos_xml(args.archivo_xml)
    print("datos_vehiculos", args.archivo_xml)
    conteo_taz = contar_taz(datos_vehiculos)
    print("conteo_taz")
    datos_adicionales = leer_datos_adicionales(args.archivo_texto)
    print("datos_adicionales")
    teleports = leer_teleports_summary(args.archivo_summary)
    # Graficar los resultados
    graficar_conteo_taz(conteo_taz, datos_adicionales, teleports, args.carpeta_figuras)

if __name__ == "__main__":
    main()

