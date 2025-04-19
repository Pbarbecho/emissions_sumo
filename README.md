# Proyecto de Simulación de Tráfico
## Modelo de tráfico Cuenca-Ecuador ##

Este repositorio contiene scripts y configuraciones para la simulación de tráfico utilizando SUMO (Simulation of Urban MObility). A continuación se describe cada uno de los componentes y scripts incluidos en este repositorio.


## emissions.sh

Este script bash permite ejecutar una serie de instrucciones para procesar archivos de simulación de tráfico y ejecutar simulaciones en SUMO. Los pasos principales que realiza son:

1. Verifica que se han proporcionado dos argumentos: el día y un número adicional denominado como factor.
2. Busca archivos con la extensión `.xlsx` que contengan la palabra del día especificado.
3. Extrae las horas de inicio y fin del nombre del archivo.
4. Crea un archivo de salida en formato VISUM (OD).
5. Ejecuta varios scripts en Python y comandos de SUMO para procesar los datos y realizar simulaciones.

### Parámetros de Entrada:
- **Día:** El día de la semana especificado.
- **Factor:** Un valor numérico adicional utilizado en los cálculos.

Su ejecución viene dada del siguiente modo:
```bash
./emissions.sh <día> <factor>
```

Este script asume que los archivos de tráfico en formato Excel se encuentran en su misma ubicación y que su nombre sigue el siguiente formato:
```bash
martes_7.00_10.00.xlsx
lunes_7.00_10.00.xlsx
```
El script filtra el día especificado en el parámetro de entrada y busca coincidencias con los nombres de archivos en formato .xlsx, teniendo en cuenta la diferencia de tiempo entre hora de inicio y hora final indicadas en el nombre del archivo excel. En el ejemplo de 7-10 se genera automáticamente el sumo.cfg con un tiempo de 10800s (3hr) de simulación. 

Para realizar el plot de las calles se requiere que el script de SUMO/visualization/tools/**plot_net_dump.py** se encuentre en el mismo directorio del script emissions.sh

A continuación se presenta de manera más detallada el conjunto de scripts desarollados en python, presentando como realizar la ejecución y modificaciones que se le pueden implementar.


[Procesos del Script emissions][https://lucid.app/lucidspark/4d55310a-2b69-4934-86c6-c45e0790fee1/edit?invitationId=inv_cc1d10d6-1744-4c77-9684-47151d570e6b]


## Herramientas desarrolladas

### genMatrizOD.py

Crea la matriz O/D de tráfico en el formato V (VISUM/VISSIM) entendible para SUMO. Este script toma los datos de un archivo excel en el cual la primera columna y fila contienen nombres (TAZ) y los valores de la tabla representan la cantidad de vehículos circulando entre esos TAZ específicos. La estructura del documento de excel puede visualizarse en la siguiente figura. 

<img src="https://github.com/user-attachments/assets/f64c3f8f-eee5-43cb-8872-8f80f1690b85" alt="trafico" width="300"/>

Para ejecutar el script tenemos los siguientes parámetros:

```bash
python3 matriz.py <archivo_excel.xlxs> <archivo_salida.od> <tiempo_inicio_simulacion> <tiempo_final_simulacion> <factor>
```

Los parámetros de entrada para la ejecución de este script viene dado por lo siguiente:
1. Nombre del archivo Excel (<archivo_excel.xlxs>).
2. Nombre del archivo de salida en formato V (.od) (<archivo_salida.od>).
3. Tiempo de inicio **formato 24hr**. (<tiempo_inicio_simulacion>).
4. Tiempo de final **formato 24hr**(<tiempo_final_simulacion>).
5. Un número adicional (factor de escalamiento).

**Ejemplo**: Su ejecución viene dada del siguiente modo. Ejemplo 12hr de generación de tráfico:

```bash
python3 matriz.py ~/lunes_7.00_19.00.xlsx output_matriz.od 7 19 1
```
Nota: Genera un solo archivo convirtiendo los datos en el excel en formato V. No toma encuenta las horas de inicio y fin. **Pendiente**: generar un file .od por cada hora, depende de la lectura del excel. 


### Genera Rutas con MARouter

Dentro del script emissions.sh se llama a la herramienta  MARouter para generar rutas de los vehículos en formato .rou. Como archivos de entrada se requiere el archivo de distritos TAZ (districts.taz.xml), la red de carreteras (network.net.xml), y el archivo de demanda de tráfico generado con el script genMatrizOD.py. 

Su ejecución viene dada del siguiente modo:

```python
marouter -n "network.net.xml" -m "output_matriz.od" --max-alternatives 1 --vtype "car" --additional-files "districts.taz.xml" --output-file "marouter.rou.xml"
```


### generate_sumocfg.py

Este script genera archivos de configuración para SUMO, utilizando varios archivos de entrada y parámetros. Los parámetros de entrada son:
1. El archivo de rutas.
2. Archivos adicionales necesarios para la simulación.
3. El nombre del archivo de salida.
4. El tipo de formato (duarouter o marouter).
5. Archivos de reporte.

Su ejecución viene dada del siguiente modo:
```bash
python3 generate_sumocfg.py <archivo_marouter.rou.xml> <archivos_adicionales> <archivo_sumocfg> <archivo_entrada_edgeData.xml> <archivo_salida_edgeData.xml> <tiempo_inicio_simulacion> <tiempo_final_simulacion>
```

### edges.py

Este script genera gráficos basados en los datos obtenidos de la simulación. Analiza los archivos generados por la simulación para contar la cantidad de vehículos entre diferentes TAZ y genera gráficos que se guardan en una carpeta específica. Los parámetros de entrada son:
1. Los archivos a analizar.
2. La carpeta de destino para los gráficos.

Su ejecución viene dada del siguiente modo:
```bash
python3 edges.py <archivo_vehroute.xml> <archivo_matriz.od> <archivo_summary.xml> <carpeta_salida_de_resutados_graficos>
```

### genVtypeDistribution.py

Este script genera el gráfico de la distribución total (todas las rutas generadas entre distritos) de los diferentes tipos de vehículos. Se ejecuta antes de la simulación; directamente extrae la dsitribución de tipos de vehículos del archivo de rutas (marouter.rou). Requiere del archivo VtypeDistribution.csv que contiene la distribución de los vehículos y debe ser consistente con los tipos de vehículos declarados en el vtypes.add.xml. Se ejecuta desde el emissions.sh o se puede ejecutar de la siguiente manera en la terminal: 


```bash
python3 genVtypeDistribution.py <VtypeDistribution.csv> <marouter.rou.xml>  <marouter_m.rou.xml>  <summary.xml>  <path_folder_figuras/>
```

Ejemplo:
```bash
python3 genVtypeDistribution.py outputs/lunes_7.00_8.00/marouter.rou.xml outputs/lunes_7.00_8.00/marouter_m.rou.xml outputs/lunes_7.00_8.00/reportes_m/figuras
```


Esta información tiene que encontrarse presente además en el archivo vtypes.add.xml, que es en donde se extrae la información necesaria para la simulación mediante la instrucción marouter de sumo, la estructura de este archivo se encuentra presente a continuación.

```xml
<routes>

    <vTypeDistribution id="typedist1">
		<vType id="Chevrolet_-1000cc" accel="0.645161290322581" decel="2.1326164874552" emergencyDecel="4.26523297491039" length="3.495" maxSpeed="43.0555555555556" width="1.495" height="1.5" probability="0.0162854613388376" color="0,0,255"/>
		<vType id="Chevrolet_1000-1600cc" accel="1.48014723157647" decel="3.16587046753857" emergencyDecel="6.33174093507714" length="4.235" maxSpeed="52.5" width="1.67" height="1.495" probability="0.0787258360485693" color="0,0,255"/>
		<vType id="Chevrolet_1600-2000cc" accel="3.359375" decel="4.10590277777778" emergencyDecel="8.21180555555556" length="4.51" maxSpeed="59.7222222222222" width="1.73" height="1.45" probability="0.244703426140746" color="0,0,255"/>
    </vTypeDistribution>
</routes>
```

La siguiente imagen muestra el resultado de genVtypeDistribution.py:

<img src="https://github.com/user-attachments/assets/a7846c86-685d-4d19-b203-036a0faf9206" alt="cDistribución de Tipos de Vehículos Asignados 2903" width="500"/>



### genHBFAv4.py

Este script asigna aleatoriamente un modelo de emisiones del [Handbook de Emisiones][ https://sumo.dlr.de/docs/Models/Emissions/HBEFA4-based.html] disponible en SUMO. Se utiliza los modelos HBEFA4:

['HBEFA4/PC_petrol_Euro-1', 'HBEFA4/PC_petrol_Euro-2', 'HBEFA4/PC_petrol_Euro-3', 'HBEFA4/PC_petrol_Euro-4', 'HBEFA4/PC_petrol_Euro-5', 'HBEFA4/PC_petrol_Euro-6ab', 'HBEFA4/PC_petrol_Euro-7']


```bash
python3 genHBFAv4.py <original_vtypes_add> <new_vtypes_add>
```



### genConteoVeh.py

Este script genera un gráfico que compara el conteo de vehículos real (xls) vs los vehículos simulados por cada distrito (TAZ). Además grafica la cantidad de teleportings en la simulación. Se ejecuta una vez terminada la simulación ya que utiliza outputs de SUMO. Utiliza 3 entradas: /reportes_m/summary.xml, /reportes_m/vehroute.xml outputs de SUMO y xxxx.od orgen destino file. Se ejecuta desde el script emissions.py o se puede usar desde la terminal de la siguiente manera: 

```bash
python3 genConteoVeh.py <vehroute.xml>  <TAZ.od>  <summary.xml>  <figuras/>
```


Ejemplo: 

```bash
python3 genConteoVeh.py outputs/lunes_7.00_8.00/reportes_m/vehroute.xml outputs/lunes_7.00_8.00/lunes_7.00_8.00.od outputs/lunes_7.00_8.00/reportes_m/summary.xml outputs/lunes_7.00_8.00/reportes_m/figuras
```

La siguiente imagen muestra el resultado de genConteoVeh.py:

<img src="https://github.com/user-attachments/assets/68abceb2-f8e7-4abd-bca0-4e42106f9f7b" alt="conteo_Bellavista" width="500"/>


Los teleportings se muestran en la siguiente figura: 

<img src="https://github.com/user-attachments/assets/cb9b404d-9ef7-448f-be15-121cdc22c997" alt="comparacion_vehiculos_teleports" width="500"/>


### plot_net_dump.py

Esta es una herramienta visual de SUMO que genera un mapa de calor basado en las emisiones de CO2 generadas por SUMO. Utiliza los datos de la simulación y genera gráficos de emisiones en función del mapa utilizado para las simulaciones de tráfico. Se ejecuta luego de la simulación directo desde el emissions.sh. Los archivos de entrada son edgeData.xml output de SUMO, el archivo de red de carreteras (network.net.xml) y el nombre del plot de salida. 

Se ejecuta desde el script emissions.py o se puede usar desde la terminal de la siguiente manera: 

```bash
python3 genConteoVeh.py outputs/lunes_7.00_8.00/reportes_m/vehroute.xml outputs/lunes_7.00_8.00/lunes_7.00_8.00.od outputs/lunes_7.00_8.00/reportes_m/summary.xml outputs/lunes_7.00_8.00/reportes_m/figuras
```
