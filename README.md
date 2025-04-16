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



## Archivos Python

### matriz.py

Crea la matriz O/D de tráfico en el formato V (VISUM/VISSIM) entendible para SUMO. Este script toma los datos de un archivo excel en el cual la primera columna y fila contienen nombres (TAZ) y los valores de la tabla representan la cantidad de vehículos circulando entre esos TAZ específicos. La estructura del documento de excel puede visualizarse en la siguiente figura. 

![image](https://github.com/user-attachments/assets/f64c3f8f-eee5-43cb-8872-8f80f1690b85)

#### Ejecutar matriz.py

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

### modificar_vtype.py

Este script modifica el archivo de rutas generado para incluir diferentes tipos de vehículos basados en porcentajes predefinidos. Los parámetros de entrada son:
1. El archivo original con un solo tipo de vehículo.
2. El nombre del archivo de salida modificado.
3. La carpeta de destino para los gráficos.

Los parámetros que define el tipo de vehículo que se encontrará en la simulación viene dado en el diccionario percentages, en este se encuentra el nombre del tipo de vehículo, junto con el valor del porcentaje bajo el cual serán actualizados los datos en el archivo marouter_modificado.rou.xml de análisis.

```python
# Definir los porcentajes para cada tipo de vehículo
percentages = {
    "Chevrolet_-1000cc":0.0162,
    "Chevrolet_1000-1600cc":0.0766,
    "Chevrolet_1600-2000cc":0.2474,
    "Chevrolet_2000cc+":0.1117,
    "Hyundai_-1000cc":0.0025,
    "Hyundai_1000-1600cc":0.0100,
    "Hyundai_1600-2000cc":0.0693
}
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


Su ejecución viene dada del siguiente modo:
```bash
python3 modificar_vtype.py <archivo_marouter_original.rou.xml> <archivo_salida_marouter_modificado.rou.xml> <carpeta_salida_figuras_resultados_cambios>
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

### plot_net_dump.py

Este script genera un mapa de calor basado en las emisiones de CO2 generadas por SUMO. Utiliza los datos de la simulación y genera gráficos de emisiones en función del mapa utilizado para las simulaciones de tráfico. Los parámetros de entrada son:
1. Archivos a analizar.
2. Archivos de configuración de la red.
3. Otros parámetros de visualización.



### genConteoVeh.py

Este script genera un gráfico de línea que incluye el conteo de vehículos del archivo original vs los vehículos simulados. Utiliza como entradas /reportes_m/summary.xml, /reportes_m/vehroute.xml outputs de SUMO y xxxx.od matrix. Se llama directamente del script emissions.py o se puede usar desde la terminal: 

Su ejecución viene dada del siguiente modo:
```bash
python3 genConteoVeh.py <archivo_marouter_original.rou.xml> <archivo_salida_marouter_modificado.rou.xml> <carpeta_salida_figuras_resultados_cambios>
```
