#!/bin/bash

# Verificar si se han proporcionado el día y el número adicional como argumentos
if [ $# -ne 3 ]; then

  echo "Trafico de entrada"
  echo "Uso: $0 <día> <folder datos trafico> <folder outputs>"

  exit 1
fi

# Asignar los argumentos a variables
day_of_week=$1
additional_number=1
path_datos_trafico_xlsx=$2
traffic_folder=${path_datos_trafico_xlsx}/${day_of_week}*.xlsx
outdir=$3


# Buscar archivos que contengan la palabra del día especificado y tengan la extensión .xlsx
for file in ${traffic_folder} ; do
  # Verificar si el archivo existe
  if [ -e "$file" ]; then
    # Extraer las horas de inicio y fin del nombre del archivo
    base_name=$(basename "$file" .xlsx)
     
    IFS='_' read -r day start_time end_time <<< "${base_name}"
    
    # Crear el nombre del archivo de salida con extensión .od
    output_file="${base_name}.od"

#: <<'FIN_COMENTARIO'

    # borra el contenido del folder outputs
     # Verifica si la carpeta existe
    if [ -d "$outdir" ]; then
       # Borra todo el contenido dentro de la carpeta
       rm -rf "${outdir:?}"/*
       echo "Se ha eliminado todo el contenido de: $outdir"
    else
	echo "La carpeta $outdir no existe."
    fi
	
    traffic_file_name=${base_name}
    base_name=${outdir}/${base_name}
    
    mkdir ${base_name}
    OD_DIR=${base_name}/OD
    mkdir $OD_DIR

    #Crea resumen de comandos ejecutados exec_commands.txt
    commands_file=${base_name}/exec_commands.txt
    touch $commands_file

    # Ejecutar el comando de Python con los parámetros correspondientes
    echo "Crea archivos OD"
    echo "# Crea archivos OD" >> $commands_file
    echo -e "python3 genMatrizOD.py $file ${base_name}/$output_file $start_time $end_time $additional_number\n" >> $commands_file
    python3 genMatrizOD.py "$file" "${base_name}/$output_file" "$start_time" "$end_time" "$additional_number"


    cp districts.taz.xml ${OD_DIR}/districts.taz.xml

    python3 genOD_files.py "$file" "${OD_DIR}" "$start_time" "$end_time" "$additional_number"

   : <<'FIN_COMENTARIO'


    echo "Crea archivo de rutas"
    echo "# Crea archivo de rutas" >> $commands_file
    #echo -e "marouter -n network.net.xml -m ${base_name}/$output_file --vtypeDistribution  --max-alternatives 1 --vtype car --additional-files districts.taz.xml --output-file ${base_name}/marouter.rou.xml\n" >> $commands_file
    #marouter -n "network.net.xml" -m "${base_name}/$output_file" --max-alternatives 1 --vtype "car" --additional-files "districts.taz.xml" --output-file "${base_name}/marouter.rou.xml"
    duarouter -n "network.net.xml" -m "${base_name}/$output_file" --max-alternatives 1 --vtype "car" --additional-files "districts.taz.xml" --output-file "${base_name}/marouter.rou.xml"


    echo "Archivo procesado"
    
    # Crea folder de outputs
    mkdir "${base_name}/reportes_m"
    echo "# Crea vtypesDistribution Figure - Before Simulation" >> $commands_file
    echo -e "python3 genVtypeDistribution.py ${base_name}/marouter.rou.xml ${base_name}/marouter_m.rou.xml ${base_name}/reportes_m/figuras\n" >> $commands_file
    python3 genVtypeDistribution.py "VtypeDistribution.csv" "${base_name}/marouter.rou.xml" "${base_name}/marouter_m.rou.xml" "${base_name}/reportes_m/figuras"

    # Modifica el vtypes.add.xml con los modelos de emisiones de HBFAv4
    echo "# Modifica vtypes.add" >> $commands_file
    echo "python3 genHBFAv4.py vtypes.add.xml ${base_name}/vtypes_m.add.xml"
    python3 genHBFAv4.py "vtypes.add.xml" "${base_name}/vtypes_m.add.xml"

    # Crea el sumo cfg para la simulacion
    echo "# Crea SUMO cfg" >> $commands_file
    echo -e "python3 genSumocfg.py marouter_m.rou.xml districts.taz.xml,vtypes.add.xml,edgeData_m.xml ${base_name}/osm_m.sumocfg m ${base_name}/edgeData_m.xml" "reportes_m/edgeData.xml ${start_time} ${end_time}\n" >> $commands_file
    python3 genSumocfg.py "marouter_m.rou.xml" "districts.taz.xml,vtypes_m.add.xml,edgeData_m.xml" "${base_name}/osm_m.sumocfg" "m" "${base_name}/edgeData_m.xml" "reportes_m/edgeData.xml" "$start_time" "$end_time"

    cp districts.taz.xml ${base_name}/districts.taz.xml
    cp network.net.xml ${base_name}/network.net.xml

    #Ejecuta simulacion
    echo "# Ejecuta simulacion - sumo cfg"
    echo -e "sumo -c ${base_name}/osm_m.sumocfg\n"
    sumo -c ${base_name}/osm_m.sumocfg

    echo "simulacion sumo -c maroute realizada"

    #Plots de conteo de vehiculos
    echo "# Crea Figura Conteo de Vehiculos" >> $commands_file
    echo -e "python3 genConteoVeh.py ${base_name}/reportes_m/vehroute.xml ${base_name}/${output_file} ${base_name}/reportes_m/summary.xml ${base_name}/reportes_m/figuras\n" >> $commands_file
    python3 genConteoVeh.py ${base_name}/reportes_m/vehroute.xml ${base_name}/${traffic_file_name}.od ${base_name}/reportes_m/summary.xml ${base_name}/reportes_m/figuras


#base_name=${outdir}/${base_name}
    # Obten el max co2
    max_co2=$(python3 getMaxCO2.py "${base_name}/reportes_m/edgeData.xml")
    max_co2_float=$(printf "%.2f" "$max_co2")
    echo "Max CO2 ${max_co2}"

    echo "# Crea Figura mapa CO2"
    #echo -e "python3 plot_net_dump.py -v -n network.net.xml --measures CO2_abs,CO2_abs --fw 12 --fh 7 --xlabel [m] --ylabel [m]  --default-width 1 -i ${base_name}/reportes_m/edgeData.xml,${base_name}/reportes_m/edgeData.xml  --xlim 3000,18000 --ylim 4000,12000 --default-width .5 --default-color #606060 --colormap #0:#00c000,.25:#408040,.5:#ffff00,.75:#804040,1:#c00000 -o ${base_name}/reportes_m/figuras/co2.pdf\n" >> $commands_file
    python3 plot_net_dump.py -v -n ${base_name}/network.net.xml --measures CO2_abs,CO2_abs --fw 12 --fh 7 --xlabel [m] --ylabel [m] --default-width 1 -i  ${base_name}/reportes_m/edgeData.xml,${base_name}/reportes_m/edgeData.xml --xlim 3000,18000 --ylim 4000,12000 --default-width .5 --default-color "#606060" --colormap jet "#0:#0000c0,.25:#404080,.5:#808080,.75:#804040,1:#c00000" --min-color-value 0 --max-color-value "${max_co2_float}" --max-width-value "${max_co2_float}" --min-width-value 0  --max-width 5 --min-width .5 -o ${base_name}/reportes_m/figuras/co2.svg
FIN_COMENTARIO
  fi

done
