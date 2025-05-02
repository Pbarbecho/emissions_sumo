import pandas as pd
import sys, os
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_backend
import math
import time
import multiprocessing
import xml.etree.ElementTree as ET
import psutil
import shutil
import numpy as np
from datetime import datetime
import openpyxl


def time_diff(from_time, to_time):
    from_time_float = float(from_time)
    to_time_float = float(to_time)

    # Calculate the time difference
    if from_time_float == to_time_float:
        time_difference = 24.0
    elif to_time_float < from_time_float:
        to_time_float += 24
        time_difference = to_time_float - from_time_float
    else:
        time_difference = to_time_float - from_time_float

    time_difference_hours = int(time_difference)  # Número de horas completas entre from_time y to_time
    return time_difference_hours
    #return f"{time_difference_hours:05.2f}"

def generate_output_file(input_excel_list, output_file, factor):
    list_OD_files = []
    for k,file in enumerate(input_excel_list):

        # Load the Excel file
        df = pd.read_excel(file, index_col=0)

        OD_output_name = f"{output_file}/{k}.od"
        with open(OD_output_name, 'w') as f:
            # Write the header
            f.write('$OR;D2\n')
            f.write(f'* From-Time  To-Time\n{k}.00 {k+1}.00\n')
            f.write('* Factor\n')
            f.write(f'{factor}\n')

            # Write the data
            for from_location, row in df.iterrows():
                for to_location, num_vehicles in row.items():
                    # adjusted_vehicles = num_vehicles * porcentaje
                    adjusted_vehicles = num_vehicles
                    # f.write(f'\t\t{from_location}          {to_location}       {num_vehicles}\n')
                    # f.write(f'\t\t\t{from_location}\t\t\t{to_location}\t\t\t{num_vehicles}\n')
                    #                f.write(f'\t\t{from_location.ljust(30)}{to_location.ljust(30)}{num_vehicles}\n')
                    f.write(f'\t\t{from_location.ljust(30)}{to_location.ljust(30)}{int(adjusted_vehicles)}\n')
        list_OD_files.append(OD_output_name)
    return list_OD_files

def gen_per_hour_traffic(archivo_entrada, archivo_salida, n, iter):
    # Cargar el archivo de entrada
    wb_entrada = openpyxl.load_workbook(archivo_entrada)
    wb_salida = openpyxl.Workbook()
    wb_salida.remove(wb_salida.active)  # Quita la hoja por defecto

    for hoja in wb_entrada.sheetnames:
        ws_entrada = wb_entrada[hoja]
        ws_salida = wb_salida.create_sheet(title=hoja)

        for fila in ws_entrada.iter_rows():
            nueva_fila = []
            for celda in fila:
                valor = celda.value
                if isinstance(valor, (int, float)):
                    nuevo_valor = round(valor / n)
                else:
                    nuevo_valor = valor  # Mantiene texto o celdas vacías igual
                nueva_fila.append(nuevo_valor)
            ws_salida.append(nueva_fila)
    # Guardar el nuevo archivo
    out_file_name = f"{archivo_salida}/{iter}.xlsx"
    wb_salida.save(out_file_name)
    return out_file_name

def create_files_per_hour(archivo_entrada, archivo_salida, hours):
    list_out_files = []
    # falta generar probabilidad por caDA HORA para el trafico en forma de camello
    for k in range(1, hours+1):
        out_file_name = gen_per_hour_traffic(archivo_entrada, archivo_salida, hours, k)
        list_out_files.append(out_file_name)
    return list_out_files

def gen_od2trips_cfg(O_list, taz_file, out_dir):

    # read O files
    O_files_list = [os.path.basename(path.rstrip("/")) for path in O_list]
    O_listToStr = ','.join([f'{elem}' for elem in O_files_list])
    TAZ = taz_file

    od2trips_conf = os.path.join('templates', 'od2trips.cfg.xml')

    # Open original file
    tree = ET.parse(od2trips_conf)

    # Update O input
    parent = tree.find('input')
    ET.SubElement(parent, 'od-matrix-files').set('value', f'{O_listToStr}')
    ET.SubElement(parent, 'taz-files').set('value', f'{TAZ}')

    # Update output
    parent = tree.find('output')
    output_name = 'od2.trip.xml'
    ET.SubElement(parent, 'output-file').set('value', output_name)

    # Update seed number
    parent = tree.find('random_number')
    ET.SubElement(parent, 'seed').set('value', f'{1}')

    # Write xml
    cfg_name = f'{out_dir}/trips.cfg.xml'
    tree.write(cfg_name)
    return cfg_name, output_name

def exec_od2trips(fname):
    print('\n OD2Trips running .............\n')
    cmd = f'od2trips -v -c {fname}'
    os.system(cmd)
    # remove fromtotaz
    #output_file = f'{tripfile}.xml'
    #rm_taz = f"sed 's/fromTaz=\"{folders.O_district}\" toTaz=\"{folders.D_district}\"//' {tripfile} > {output_file}"
    #os.system(rm_taz)
    #return output_file


if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("Usage: python3 genOD_files.py <input_excel> <output_dir> <from_time> <to_time> <factor>")
        sys.exit(1)

    input_excel = sys.argv[1]
    output_dir = sys.argv[2]
    from_time = sys.argv[3]
    to_time = sys.argv[4]
    factor = int(sys.argv[5])

    time_diff_in_file_name = time_diff(from_time, to_time)
    list_xls_files = create_files_per_hour(input_excel, output_dir, time_diff_in_file_name)
    list_OD_files = generate_output_file(list_xls_files, output_dir,1)
    od2_cfg_name, od2_result_file = gen_od2trips_cfg(list_OD_files, "districts.taz.xml", output_dir)
    exec_od2trips(od2_cfg_name)




