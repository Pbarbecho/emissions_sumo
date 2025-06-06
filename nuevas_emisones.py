import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd
import math
from xml.dom import minidom

# Función para calcular nueva emisión basada en la velocidad y tipo
def calcular_emisiones(velocidad, marcha_prev, velo_prev, contM, umbralRPMmax, umbralRPMmin,  vemisions):
    rT = 3.7 # relacion dfif
    r= 0.0
    ralenti = 850 # minimas rpm
    rpmActual = ralenti # Ralentí
    marcha_actual = marcha_prev 
    n_e1 = vemisions["HCbajas"]
    n_e2 = vemisions["CObajas"]
    n_e3 = vemisions["FEHCbajas"]
    n_e4 = vemisions["FECObajas"]

    # rlacion de transmision, podría tambien ser parte delos archivos csv para cad vehiculo
    if marcha_actual == 1:
        r = 3.6
    elif marcha_actual == 2:
        r = 2.2
    elif marcha_actual == 3:
        r = 1.8
    elif marcha_actual == 4:
        r = 1.3
    elif marcha_actual == 5:
        r = 1.0
    elif marcha_actual == 6:
        r = 0.8

    #r*rT: relacion total
    if velocidad > 0:
        if marcha_prev == 0 or velo_prev == 0:
            marcha_actual = 1
        else:
            rpmActual = velocidad*r*rT*60/(math.pi*vemisions["drueda"])
            if contM > 2:
                if rpmActual >= umbralRPMmax:
                    marcha_actual += 1
                    marcha_actual = min(marcha_actual,6)
                elif rpmActual <= umbralRPMmin:
                    marcha_actual -= 1
                    marcha_actual = max(marcha_actual,1)
        if marcha_actual == 1:
            r = 3.6
        elif marcha_actual == 2:
            r = 2.2
        elif marcha_actual == 3:
            r = 1.8
        elif marcha_actual == 4:
            r = 1.3
        elif marcha_actual == 5:
            r = 1.0
        elif marcha_actual == 6:
            r = 0.8
        # Cálculo rpm
        rpmActual = velocidad*r*rT*60/(math.pi*vemisions["drueda"])
        rpmActual = max(rpmActual, ralenti)
        if rpmActual >= umbralRPMmax:
            n_e1 = vemisions["HCaltas"]
            n_e2 = vemisions["COaltas"]
            n_e3 = vemisions["FEHCaltas"]
            n_e4 = vemisions["FECOaltas"]   
        n_e1 *= velocidad
        n_e2 *= velocidad
        n_e3 *= velocidad
        n_e4 *= velocidad
    elif velo_prev == 0:
        marcha_actual = 0 # en caso de eque esta parado, baja a cambio neutro
    # n_e1 *= rpmActual/500
    # n_e2 *= rpmActual/500
    # n_e3 *= rpmActual/500
    # n_e4 *= rpmActual/500
    return marcha_actual, n_e1, n_e2, n_e3, n_e4, rpmActual

# Leer archivo FCD y generar nuevo archivo con nuevas emisiones
def procesar_fcd(fcd_file, salida_file):
    # Carga de archivos
    df = pd.read_csv("Factores.csv",  encoding='latin1') #archivo CSV con los factores y detalle de vehiculos
    d = df.set_index(df.columns[0]).to_dict(orient='index')#diccionado, por cada id de vehiculo

    tree = ET.parse(fcd_file)
    root = tree.getroot()


    # Estructura de historial de marcha por vehículo
    historial = defaultdict(lambda: {'marcha': 0, 'velocidad': 0.0, 'contM': 0, 'RPM': 0.0})

    # Crear root
    nuevo_root = ET.Element("fcd-export")

    for timestep in root.findall("timestep"):
        nuevo_timestep = ET.SubElement(nuevo_root, "timestep", {"time": timestep.get("time")})

        for veh in timestep.findall("vehicle"):
            vid = veh.get("id")
            velocidad = float(veh.get("speed"))
            tipo = veh.get("type")
            marcha_prev = historial[vid]['marcha']
            velo_prev = historial[vid]['velocidad']
            marcha, emi1, emi2, emi3, emi4, rpm = calcular_emisiones(velocidad, marcha_prev, velo_prev, historial[vid]['contM'], 2500, 1000, d[int(tipo)])
            if marcha_prev - marcha == 0:
                historial[vid]['contM'] += 1
            else:
                historial[vid]['contM'] = 1
            historial[vid]['marcha'] = marcha
            historial[vid]['velocidad'] = velocidad
            historial[vid]['RPM'] = rpm
            # Copio los atributos originales excepto emisiones anteriores
            nuevo_atributos = {k: v for k, v in veh.attrib.items()
                               if k not in ["CO2", "CO", "HC", "NOx", "PMx", "fuel", "electricity", "noise"]}

            # Agregar nuevas emisiones marchas y rpm
            nuevo_atributos["CO"] = f"{emi1:.2f}"
            nuevo_atributos["HC"] = f"{emi2:.2f}"
            nuevo_atributos["FECO"] = f"{emi3:.2f}"
            nuevo_atributos["FEHC"] = f"{emi4:.2f}"
            nuevo_atributos["marcha"] = str(marcha)
            nuevo_atributos["RPM"] = f"{rpm:.1f}"

            ET.SubElement(nuevo_timestep, "vehicle", nuevo_atributos)

    # Guardar archivo XML
    nuevo_arbol = ET.ElementTree(nuevo_root)
    ET.indent(nuevo_arbol, space="    ", level=0)

    # Escribir el archivo
    nuevo_arbol.write(salida_file, encoding="utf-8", xml_declaration=True)


fcd_input = "fcd_1.xml"                  # Archivo de entrada FCD
salida_output = "nuevas_emisiones.xml" # Archivo de salida

procesar_fcd(fcd_input, salida_output)