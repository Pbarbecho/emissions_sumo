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


def plot_vtypes_distr(percentages, carpeta):
    # Contar la cantidad de cada tipo de vehículo asignado
    counts = {t: assigned_types.count(t) for t in percentages.keys()}

    # Preparar datos para la gráfica de barras
    types = list(percentages.keys())
    values = [counts[t] for t in types]

    # Crear la gráfica de barras
    plt.figure(figsize=(10, 6))
    bars = plt.bar(types, values, color='skyblue')

    # Añadir leyendas con los valores numéricos a cada barra
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), value,
                 ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.xlabel('Tipo de Vehículo')
    plt.ylabel('Cantidad Asignada')
    plt.xticks(rotation=90)
    plt.title(f'Distribución de Tipos de Vehículos Asignados {total_vehicles}')
    plt.grid(True)
    plt.tight_layout()
    # Guardar la figura en la carpeta especificada
    ruta_figura = os.path.join(carpeta, f'Distribución de Tipos de Vehículos Asignados {total_vehicles}.png')
    plt.savefig(ruta_figura)
    plt.close()
    # Mostrar la gráfica
    # plt.show()

def duplicate_flows(marouter_file, marouter_file_m):
    # Archivo generado por marouter
    tree = ET.parse(marouter_file)
    root = tree.getroot()

    # Lista de tipos de vehículos que quieres asignar
    vehicle_types = ["car", "truck", "bus"]
    new_flows = []

    for flow in root.findall("flow"):
        original_id = flow.get("id")
        begin = flow.get("begin")
        end = flow.get("end")
        from_edge = flow.get("fromTaz")
        to_edge = flow.get("toTaz")
        depart_pos = flow.get("departPos", "random")
        depart_speed = flow.get("departSpeed", "max")
        depart_lane = flow.get("departLane", "best")

        try:
            total = int(flow.get("number"))
        except:
            continue

        # Crear tantos <flow> como indique 'number', cada uno con type aleatorio y number=1
        for i in range(total):
            new_flow = ET.Element("flow")
            new_flow.set("id", f"{original_id}_{i}_{uuid.uuid4().hex[:4]}")
            new_flow.set("type", random.choice(vehicle_types))
            new_flow.set("number", "1")
            new_flow.set("begin", begin)
            new_flow.set("end", end)
            new_flow.set("fromTaz", from_edge)
            new_flow.set("toTaz", to_edge)
            new_flow.set("departPos", depart_pos)
            new_flow.set("departSpeed", depart_speed)
            new_flow.set("departLane", depart_lane)

            new_flows.append(new_flow)

        # Eliminar el flujo original
        root.remove(flow)

    # Agregar los nuevos flows
    for f in new_flows:
        root.append(f)

    # Pretty print con líneas en blanco entre flows
    rough_string = ET.tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    pretty_xml = pretty_xml.replace("</flow>\n  <flow", "</flow>\n\n  <flow")

    # Guardar el resultado
    with open(marouter_file_m, "w") as f:
        f.write(pretty_xml)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Uso: python script.py <vtypes csv> <archivo_entrada_xml> <archivo_salida_xml>")
        sys.exit(1)

    vtypesdist = sys.argv[1]
    input_xml = sys.argv[2]
    output_xml = sys.argv[3]
    carpeta=sys.argv[4]

    # leer el archivo donde se indica la distribucion de cada tipo de vehiculo
    percentages = read_vtypes_distribution(vtypesdist)

    # modifica marouter para duplicar flujos
    duplicate_flows(input_xml, output_xml)

    # modifica el marouter.rou para agregar la vtype distribution
    #assigned_types, total_vehicles = modify_vehicle_types(input_xml, output_xml)

    # Genera plot de vtypes ditribution
    crear_carpeta_si_no_existe(carpeta)
    plot_vtypes_distr(percentages, carpeta)



