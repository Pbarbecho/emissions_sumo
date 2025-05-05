import sys
import xml.etree.ElementTree as ET

def get_max_co2_abs(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    max_co2 = None
    max_edge_id = None

    # Buscar todos los elementos <edge> dentro de <interval>
    for edge in root.findall('.//edge'):
        co2_abs = edge.get('CO2_abs')
        if co2_abs:
            value = float(co2_abs)
            if max_co2 is None or value > max_co2:
                max_co2 = value
                #max_edge_id = edge.get('id')
    return max_co2

if __name__ == "__main__":
    xml_file = sys.argv[1]
    max_value = get_max_co2_abs(xml_file)
    print(max_value)
