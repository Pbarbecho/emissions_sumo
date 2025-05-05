import sys

def generate_edgeData(edge,output_file2,time_difference):
	config_content= f"""<?xml version="1.0" encoding="UTF-8"?>
<additional>
    <edgeData id="1" period="{time_difference}" type="emissions" file="{edge}" excludeEmpty="true" />
</additional>
"""
	with open(output_file2, 'w') as file:
		file.write(config_content)

def generate_sumocfg(route_file, additional_files, output_file,out,time_difference):
    config_content = f"""<?xml version="1.0" encoding="UTF-8"?>

<configuration>
    <input>
        <net-file value="network.net.xml"/>
        <route-files value="{route_file}"/>
        <additional-files value="{additional_files}"/>
    </input>

<rerouting>
	<!-- Probabilidad de que un vehículo tenga un dispositivo de redireccionamiento -->
        <device.rerouting.probability value="0.5"/> 
	<!-- Período en el que se desviará el vehículo -->
        <device.rerouting.period value="300"/>
        <device.rerouting.with-taz value="true" /> 
        <!-- Enrutamiento paralelizado -->
        <device.rerouting.threads value="110"/>
        <device.rerouting.synchronize value="true"/>
    </rerouting>

    <processing>
        <ignore-route-errors value="true" />
    </processing>

    <output>
        <tripinfo-output value="reportes_{out}/tripinfo.xml"/>
        <summary-output value="reportes_{out}/summary.xml"/>
        <vehroute-output  value= "reportes_{out}/vehroute.xml"/>
    </output>

    <emissions>
        <device.emissions.probability value="1"/>
    </emissions>

    <time>
        <end value="{time_difference}"/>
    </time>
    

</configuration>
"""

    with open(output_file, 'w') as file:
        file.write(config_content)

if __name__ == '__main__':
    if len(sys.argv) != 9:
        print("Uso: python genSumocfg.py <archivo_de_rutas> <archivos_adicionales> <archivo_de_salida> <carpeta_salida_reportes> <archivo_edgedata.xml> <archivo_salida_edgedata> <tiempo_inicio> <tiempo_final>" )
        sys.exit(1)

    route_file = sys.argv[1]
    additional_files = sys.argv[2]
    output_file = sys.argv[3]
    out = sys.argv[4]
    output_file2= sys.argv[5]
    edge=sys.argv[6]
    from_time=sys.argv[7]
    to_time=sys.argv[8]
    
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
    
    time_difference=int(time_difference*3600)

    generate_sumocfg(route_file, additional_files, output_file,out,time_difference)
    print(f"Archivo {output_file} generado correctamente.")

    generate_edgeData(edge,output_file2,time_difference)
    print("Archivo edgeData.xml generado correctamente")


