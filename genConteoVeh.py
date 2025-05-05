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
#import seaborn as sns

# Función para crear la carpeta si no existe
def crear_carpeta_si_no_existe(carpeta):
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)


# Función para leer el archivo XML y extraer la información de los vehículos
def leer_datos_xml(archivo_xml):
    tree = ET.parse(archivo_xml)
    root = tree.getroot()

    # Diccionario para contar vehículos por (fromTaz, toTaz)
    count_by_taz_pair = defaultdict(int)

    # Recorrer todos los vehículos
    for vehicle in root.findall('vehicle'):
        from_taz = vehicle.attrib.get('fromTaz')
        to_taz = vehicle.attrib.get('toTaz')
        if from_taz and to_taz:
            count_by_taz_pair[(from_taz, to_taz)] += 1

    # Convertir a DataFrame
    data = [
        {"fromTaz": from_taz, "toTaz": to_taz, "vehicle_count": count}
        for (from_taz, to_taz), count in count_by_taz_pair.items()
    ]
    df = pd.DataFrame(data)
    return df


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


def graficar_conteo_taz(simulado, generado, carpeta):

    # Renombrar las columnas de vehicle_count para diferenciarlas
    simulado = simulado.rename(columns={'vehicle_count': 'vehicle_count_simulado'})
    generado = generado.rename(columns={'vehicle_count': 'vehicle_count_generado'})

    # Unir los DataFrames por fromTaz y toTaz
    comparacion = pd.merge(simulado, generado, on=['fromTaz', 'toTaz'], how='outer').fillna(0)
    #print(comparacion)
    # Calcular la diferencia
    comparacion['diferencia'] = comparacion['vehicle_count_generado'] - comparacion['vehicle_count_simulado']

    # Ordenar por la mayor diferencia absoluta
    comparacion['abs_diff'] = comparacion['diferencia'].abs()
    top_diff = comparacion.sort_values(by='abs_diff', ascending=False).head(20)

    # Plot de barras
    plt.figure(figsize=(12, 8))
    bar_labels = top_diff['fromTaz'] + " ➝ " + top_diff['toTaz']
    plt.barh(bar_labels, top_diff['diferencia'], color='skyblue')
    plt.axvline(0, color='gray', linestyle='--')
    plt.xlabel('Diferencia en vehicle_count (Generado - Simulado)')
    plt.title('Top 30 diferencias en número de vehículos por par de zonas')
    plt.tight_layout()
    plt.gca().invert_yaxis()
    ruta_figura = os.path.join(carpeta, f'veh_sim_vs_gen.png')
    plt.savefig(ruta_figura, dpi=150)
    plt.close()
    #plt.savefig(f"conteo_{origin}.png", dpi=150)  # Descomenta si quieres guardar
    #plt.show()


def plot_total_veh_sim_gen(sim_df, gen_df, teleports, carpeta):
    # Total de vehículos por simulación
    total_vehicles_1 = sim_df['vehicle_count'].sum()
    total_vehicles_2 = gen_df['vehicle_count'].sum()

    # Solo un teleport total
    total_teleports = teleports

    # Datos para graficar
    labels = ['Simulados', 'Generados', 'Teleports']
    values = [total_vehicles_1, total_vehicles_2, total_teleports]
    colors = ['steelblue', 'darkorange', 'darkred']

    # Crear gráfico
    plt.figure(figsize=(8, 6))
    bars = plt.bar(labels, values, color=colors)
    plt.title('Comparación de Conteo Total')
    plt.ylabel('Cantidad')

    # Añadir etiquetas encima de cada barra
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f'{height}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom')
    plt.tight_layout()
    ruta_figura = os.path.join(carpeta, 'total_veh_count.png')
    plt.savefig(ruta_figura)
    plt.close()


def leer_rutas_m(rutas_m_xml):
    # Cargar el archivo XML (reemplaza 'rutas.xml' con tu archivo real)
    tree = ET.parse(rutas_m_xml)
    root = tree.getroot()

    # Diccionario para contar vehículos por (fromTaz, toTaz)
    count_by_taz_pair = defaultdict(int)

    # Recorrer todos los vehículos
    for vehicle in root.findall('vehicle'):
        from_taz = vehicle.attrib.get('fromTaz')
        to_taz = vehicle.attrib.get('toTaz')
        if from_taz and to_taz:
            count_by_taz_pair[(from_taz, to_taz)] += 1

    # Convertir a lista de diccionarios para el DataFrame
    data = [
        {"fromTaz": from_taz, "toTaz": to_taz, "vehicle_count": count}
        for (from_taz, to_taz), count in count_by_taz_pair.items()
    ]
    # Crear el DataFrame
    df = pd.DataFrame(data)
    return df


def time_vs_vehicles(tripinfo, trips, carpeta):
    # --- Leer depart de routes.xml (planificado) ---
    tree_routes = ET.parse(trips)
    root_routes = tree_routes.getroot()
    depart_routes = [float(trip.attrib['depart']) for trip in root_routes.findall('trip')]
    df_routes = pd.DataFrame({'depart': depart_routes})
    df_routes['interval_5min'] = (df_routes['depart'] // 300).astype(int)  # Cambiar a 5 minutos
    group_routes = df_routes.groupby('interval_5min').size().reset_index(name='planned_count')
    group_routes['time_min'] = group_routes['interval_5min'] * 5

    # --- Leer depart de tripinfos.xml (real) ---
    tree_tripinfos = ET.parse(tripinfo)
    root_tripinfos = tree_tripinfos.getroot()
    depart_tripinfos = [float(trip.attrib['depart']) for trip in root_tripinfos.findall('tripinfo')]
    df_tripinfos = pd.DataFrame({'depart': depart_tripinfos})
    df_tripinfos['interval_5min'] = (df_tripinfos['depart'] // 300).astype(int)  # Cambiar a 5 minutos
    group_tripinfos = df_tripinfos.groupby('interval_5min').size().reset_index(name='actual_count')
    group_tripinfos['time_min'] = group_tripinfos['interval_5min'] * 5

    # --- Unir ambos para comparación ---
    merged = pd.merge(group_routes, group_tripinfos, on='interval_5min', how='outer').fillna(0)
    merged['time_min'] = merged['interval_5min'] * 5

    # --- Plot ---
    plt.figure(figsize=(12, 6))
    plt.plot(merged['time_min'], merged['planned_count'], label='Planificado (trips.xml)', marker='o', linestyle='-')
    plt.plot(merged['time_min'], merged['actual_count'], label='Simulado (tripinfo.xml)', marker='s', linestyle='--')
    plt.xlabel('Tiempo (minutos)')
    plt.ylabel('Cantidad de vehículos')
    plt.title('Comparación de vehículos planificados vs simulados cada 5 minutos')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    ruta_figura = os.path.join(carpeta, 'time_vs_veh_sim.png')
    plt.savefig(ruta_figura)
    plt.close()


# Función principal
def main():
    parser = argparse.ArgumentParser(description="Procesar archivos XML y datos adicionales para graficar conteos de vehículos.")
    parser.add_argument("archivos_sumo", type=str, help="Ruta a outputs sumo")
    parser.add_argument("OD_DIR", type=str, help="Ruta a los archivos OD.")
    parser.add_argument("carpeta_figuras", type=str, help="Carpeta donde se guardarán las figuras.")
    parser.add_argument("carpeta_taz", type=str, help="Carpeta donde se guardarán las figuras taz.")
    args = parser.parse_args()

    # Leer y procesar los datos del archivo XML y del archivo output de la simulacion vehroute
    vehroute_file = f"{args.archivos_sumo}/vehroute.xml"
    df_conteo_taz_simulado  = leer_datos_xml(vehroute_file)
    #conteo_taz_simulado = contar_taz(datos_vehiculos_simulado)
    #print(df_conteo_taz_simulado.keys())
    #print(f"Simulado vehroute {df_conteo_taz_simulado}")

    rutas_m_file = f"{args.OD_DIR}/rutas_m.rou.xml"
    df_rutas_rou_count = leer_rutas_m(rutas_m_file)
    #print(df_rutas_rou_count.keys())
    #print(f"Generado rutas.rou {df_rutas_rou_count}")

    # Graficar conteo de veh simulados vs generados en el rutas.rou
    print("\nFiguras conteo vehiculos fromTaz toTaz")
    graficar_conteo_taz(df_conteo_taz_simulado, df_rutas_rou_count, args.carpeta_taz)

    summary_file = f"{args.archivos_sumo}/summary.xml"
    teleports = leer_teleports_summary(summary_file)
    print("\nFigura conteo total vehiculos")
    plot_total_veh_sim_gen(df_conteo_taz_simulado, df_rutas_rou_count, teleports, args.carpeta_figuras)

    tripinfo_file = f"{args.archivos_sumo}/tripinfo.xml"
    od2trips = f"{args.OD_DIR}/od2.trip.xml"
    print("\nFigura time vs vehicles")
    time_vs_vehicles(tripinfo_file, od2trips,  args.carpeta_figuras)


if __name__ == "__main__":
    main()

