#!/bin/bash

# --- VERIFICA DE VARIABLES DE ENTRADA ---
# Verificar si se han proporcionado el día y el número adicional como argumentos
if [ $# -ne 3 ]; then
  echo "Trafico de entrada"
  echo "Uso: $0 <día> <folder datos trafico> <folder outputs>"
  exit 1
fi

# Asignar los argumentos a variables
day_of_week=$1
path_datos_trafico_xlsx=$2
traffic_folder=${path_datos_trafico_xlsx}/${day_of_week}*.xlsx
traffic_weights="templates/traffic_hour_weights.xlsx"
outdir=$3
#Variables estaticas
factor=1
seed=1

# --- DEFINICIÓN DE FUNCIONES ---
# Función: Crear la carpeta raíz (si existe, borra su contenido)
crear_folder_raiz() {
    local carpeta_raiz="$1"
    if [ -d "$carpeta_raiz" ]; then
        echo "La carpeta raíz '$carpeta_raiz' ya existe. Borrando su contenido..."
        rm -rf "$carpeta_raiz"/*
    else
        echo "Creando carpeta raíz '$carpeta_raiz'..."
        mkdir -p "$carpeta_raiz"
    fi
}

# Función: Crear o limpiar una subcarpeta dentro de la raíz
preparar_subcarpeta() {
    local subcarpeta="$1"
    if [ -d "$subcarpeta" ]; then
        echo "La subcarpeta '$subcarpeta' ya existe. Borrando su contenido..."
        rm -rf "$subcarpeta"/*
    else
        echo "Creando subcarpeta '$subcarpeta'..."
        mkdir -p "$subcarpeta"
    fi
}

# --- LLAMADA A FUNCIONES ---
# Llamadas a la función crea carpetas
echo -e "\n# Crea directorios"
crear_folder_raiz "$outdir"

# Carpetas de resultados
reports_FOLDER="reports"
sumo_FOLDER="$reports_FOLDER/sumo"
imagenes_FOLDER="$reports_FOLDER/imagenes"
taz_FOLDER="$imagenes_FOLDER/taz"

# Llamadas a la función crea carpetas
crear_folder_raiz "$reports_FOLDER"
preparar_subcarpeta "$sumo_FOLDER"
preparar_subcarpeta "$imagenes_FOLDER"
preparar_subcarpeta "$taz_FOLDER"


# Buscar archivos que contengan la palabra del día especificado y tengan la extensión .xlsx
for file in ${traffic_folder} ; do
  # Verificar si el archivo existe
  if [ -e "$file" ]; then
    # Extraer las horas de inicio y fin del nombre del archivo
    base_name=$(basename "$file" .xlsx)
    IFS='_' read -r day start_time end_time <<< "${base_name}"
    # Crear el nombre del archivo de salida con extensión .od
    output_file="${base_name}.od"

    # prepara subcarpetas de procesamiento
    traffic_file_name=${base_name}
    base_name=${outdir}/${base_name}
    OD_DIR=${base_name}/OD

    preparar_subcarpeta "${base_name}"
    preparar_subcarpeta "$OD_DIR"

    #Crea resumen de comandos ejecutados exec_commands.txt
    commands_file=${base_name}/exec_commands.txt
    touch $commands_file

    #copiar archivos requeridos en OD DIR
    cp districts.taz.xml ${OD_DIR}/districts.taz.xml
    cp vtypes.add.xml ${OD_DIR}/vtypes.add.xml
    cp network.net.xml ${OD_DIR}/network.net.xml

    # Modifica el vtypes.add.xml con los modelos de emisiones de HBFAv4
    echo -e "\n1. Modifica vtypes.add con modelos de emissiones HBFAv4"
    echo "1. Modifica vtypes.add con modelos de emissiones HBFAv4" >> $commands_file
    python3 genHBFAv4.py "vtypes.add.xml" "${OD_DIR}/vtypes_m.add.xml"

    # Ejecutar el comando de Python con los parámetros correspondientes
    echo -e "\n# Crea archivos OD por hora"
    echo "# Crea archivos OD por hora" >> $commands_file

    #crea cfg duarouter
    echo -e "\n2. Crea DUA CFG\n"
    echo -e "python3 genOD_files.py $traffic_weights $file ${OD_DIR} $start_time $end_time $factor" >> $commands_file
    python3 genOD_files.py "$seed" "network.net.xml" "$traffic_weights" "$file" "${OD_DIR}" "$start_time" "$end_time" "$factor" "$sumo_FOLDER"
    #ejecuta cfg duarouter
    echo -e "\n3. Ejecuta DUA CFG\n"
    duarouter -c ${OD_DIR}/dua.cfg.xml

    # Crea el sumo cfg para la simulacion MAROUTER
    #python3 genSumocfg.py "marouter_m.rou.xml" "districts.taz.xml,vtypes_m.add.xml,edgeData.xml" "${base_name}/osm_m.sumocfg" "m" "${base_name}/edgeData.xml" "reportes_m/edgeData.xml" "$start_time" "$end_time"
    #Genera una unica matriz para las 12 horas
    #python3 genMatrizOD.py "$file" "${base_name}/$output_file" "$start_time" "$end_time" "$factor"

    # Crea vtypes duarouter - ACTUA SOBRE .ROU
    echo -e "\n4. Genera distribucion de vehiculos .rou / figure - Before Simulation\n"
    echo "# Crea vtypesDistribution Figure - Before Simulation" >> $commands_file
    python3 genVtypeDistributiondua.py "VtypeDistribution.csv" "${OD_DIR}/rutas.rou.xml" "${OD_DIR}/rutas_m.rou.xml" "$imagenes_FOLDER"

    # Vtypes distributions MAROUTER
    #echo "# Crea vtypesDistribution Figure - Before Simulation" >> $commands_file
    #python3 genVtypeDistribution.py "VtypeDistribution.csv" "${base_name}/marouter.rou.xml" "${base_name}/marouter_m.rou.xml" "${base_name}/reportes_m/figuras"

    #MAROUTER
    #marouter -n "network.net.xml" -m "${base_name}/$output_file" --max-alternatives 1 --vtype "car" --additional-files "districts.taz.xml" --output-file "${base_name}/marouter.rou.xml"

    #Ejecuta simulacion DUAROUTER
    echo -e "\n# Ejecuta simulacion  sumo -c ${OD_DIR}/sim.sumo.cfg\n"
    echo "# Ejecuta simulacion\nsumo -v -c ${OD_DIR}/sim.sumo.cfg" >> $commands_file
    sumo -v -c ${OD_DIR}/sim.sumo.cfg
    echo -e "\nSimulacion sumo -c dua realizada"

    #Ejecuta simulacion MAROUTER
    #echo "# Ejecuta simulacion - sumo cfg"
    #echo -e "sumo -c ${base_name}/osm_m.sumocfg\n"
    #sumo -c ${base_name}/osm_m.sumocfg
    #echo "simulacion sumo -c maroute realizada"

    #Plots de conteo de vehiculos
    echo -e "\n# Crea Figura Conteo de Vehiculos"
    echo "# Crea Figura Conteo de Vehiculos" >> $commands_file
    python3 genConteoVeh.py ${sumo_FOLDER} ${OD_DIR} ${imagenes_FOLDER} ${taz_FOLDER}

    #base_name=${outdir}/${base_name}
    # Obten el max co2
    max_co2=$(python3 getMaxCO2.py "${sumo_FOLDER}/edgeData.xml")
    max_co2_float=$(printf "%.2f" "$max_co2")
    echo -e "\nMax CO2 ${max_co2}"

    echo -e "\nCrea Figura mapa CO2"
    python3 plot_net_dump.py -v -n "network.net.xml" --measures CO2_abs,CO2_abs --fw 12 --fh 7 --xlabel [m] --ylabel [m] --default-width 1 -i  ${sumo_FOLDER}/edgeData.xml,${sumo_FOLDER}/edgeData.xml --xlim 3000,18000 --ylim 4000,12000 --default-width .5 --default-color "#606060" --colormap jet "#0:#0000c0,.25:#404080,.5:#808080,.75:#804040,1:#c00000" --min-color-value 0 --max-color-value "${max_co2_float}" --max-width-value "${max_co2_float}" --min-width-value 0  --max-width 5 --min-width .5 -o ${imagenes_FOLDER}/co2.svg

  fi
done


