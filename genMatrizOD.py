import pandas as pd
import sys

def generate_output_file(input_excel, output_file, from_time, to_time, factor):
    # Load the Excel file
    df = pd.read_excel(input_excel, index_col=0)

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

	# Inicializar variables
    total_porcentaje = 0.0
    
    # Calcular el total de porcentaje para todo el rango
    for hour in range(time_difference_hours):
        current_hour = from_time_float + hour
        next_hour = from_time_float + hour + 1

        if 6 <= current_hour < 7 and 6 < next_hour <= 7:
            porcentaje = 0.04
        elif 7 <= current_hour < 8 and 7 < next_hour <= 8:
            porcentaje = 0.11  # Incluye hora pico
        elif 8 <= current_hour < 9 and 8 < next_hour <= 9:
            porcentaje = 0.04
        elif 9 <= current_hour < 10 and 9 < next_hour <= 10:
            porcentaje = 0.05
        elif 10 <= current_hour < 11 and 10 < next_hour <= 11:
            porcentaje = 0.04
        elif 11 <= current_hour < 12 and 11 < next_hour <= 12:
            porcentaje = 0.05
        elif 12 <= current_hour < 13 and 12 < next_hour <= 13:
            porcentaje = 0.11  # Incluye hora pico
        elif 13 <= current_hour < 14 and 13 < next_hour <= 14:
            porcentaje = 0.05
        elif 14 <= current_hour < 15 and 14 < next_hour <= 15:
            porcentaje = 0.04
        elif 15 <= current_hour < 16 and 15 < next_hour <= 16:
            porcentaje = 0.03
        elif 16 <= current_hour < 17 and 16 < next_hour <= 17:
            porcentaje = 0.03
        elif 17 <= current_hour < 18 and 17 < next_hour <= 18:
            porcentaje = 0.03
        elif 18 <= current_hour < 19 and 18 < next_hour <= 19:
            porcentaje = 0.11  # Incluye hora pico
        elif 19 <= current_hour < 20 and 19 < next_hour <= 20:
            porcentaje = 0.05
        elif 20 <= current_hour < 21 and 20 < next_hour <= 21:
            porcentaje = 0.04
        elif 21 <= current_hour < 22 and 21 < next_hour <= 22:
            porcentaje = 0.04
        elif 22 <= current_hour < 23 and 22 < next_hour <= 23:
            porcentaje = 0.02
        elif 23 <= current_hour < 24 and 23 < next_hour <= 24:
            porcentaje = 0.02
        elif 1 <= current_hour < 2 and 1 < next_hour <= 2:
            porcentaje = 0.02
        elif 2 <= current_hour < 3 and 2 < next_hour <= 3:
            porcentaje = 0.02
        elif 3 <= current_hour < 4 and 3 < next_hour <= 4:
            porcentaje = 0.02
        elif 4 <= current_hour < 5 and 4 < next_hour <= 5:
            porcentaje = 0.02
        elif 5 <= current_hour < 6 and 5 < next_hour <= 6:
            porcentaje = 0.02
        else:
            porcentaje = 0.0  # Valor por defecto, puede ser ajustado según necesidad
        total_porcentaje += porcentaje



    time_difference_str = f"{time_difference:05.2f}"

    with open(output_file, 'w') as f:
        # Write the header
        f.write('$OR;D2\n')
        f.write(f'* From-Time  To-Time\n00.00 {time_difference_str}\n')
        f.write('* Factor\n')
        f.write(f'{factor}\n')
#        f.write('* some\n')
#        f.write('* additional\n')
#        f.write('* comments\n')

                # Write the data
        for from_location, row in df.iterrows():
            for to_location, num_vehicles in row.items():
                #adjusted_vehicles = num_vehicles * porcentaje
                adjusted_vehicles = num_vehicles * total_porcentaje
                #f.write(f'\t\t{from_location}          {to_location}       {num_vehicles}\n')
                #f.write(f'\t\t\t{from_location}\t\t\t{to_location}\t\t\t{num_vehicles}\n')
#                f.write(f'\t\t{from_location.ljust(30)}{to_location.ljust(30)}{num_vehicles}\n')
                f.write(f'\t\t{from_location.ljust(30)}{to_location.ljust(30)}{int(adjusted_vehicles)}\n')

if __name__ == '__main__':
    # Ensure correct usage
    if len(sys.argv) != 6:
        print("Usage: python generate_file.py <input_excel> <output_file> <from_time> <to_time> <factor>")
        sys.exit(1)

    input_excel = sys.argv[1]
    output_file = sys.argv[2]
    from_time = sys.argv[3]
    to_time = sys.argv[4]
    factor = int(sys.argv[5])

    generate_output_file(input_excel, output_file, from_time, to_time, factor)
	
