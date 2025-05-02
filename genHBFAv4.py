import sys
import xml.etree.ElementTree as ET
import random

def modificar_vclass(xml_input, xml_output, lista_vclass,valor_emission_class):
    # Cargar el archivo XML
    tree = ET.parse(xml_input)
    root = tree.getroot()
    probability = 0.5
    # Iterar sobre todos los elementos vType y asignar un vClass aleatorio
    for vtype in root.findall('vType'):
        vclass_random = random.choice(lista_vclass)
        # Agregar el atributo emissionClass
        vtype.set('vClass', valor_emission_class)
        # Modifica emission class
        vtype.set('emissionClass', vclass_random)
    # Guardar los cambios en un nuevo archivo
    tree.write(xml_output, encoding='utf-8', xml_declaration=True)
    print(f'Se han asignado valores aleatorios de vClass y guardado en "{xml_output}"')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python3 genHBFAv4.py <original_vtypes_add>" "<new_vtypes_add>" )
        sys.exit(1)

    original_vtypes_add = sys.argv[1]
    new_vtypes_add = sys.argv[2]

    # Lista de valores posibles para vClass
    valores_vclass = ['HBEFA4/PC_petrol_Euro-1', 'HBEFA4/PC_petrol_Euro-2', 'HBEFA4/PC_petrol_Euro-3', 'HBEFA4/PC_petrol_Euro-4', 'HBEFA4/PC_petrol_Euro-5', 'HBEFA4/PC_petrol_Euro-6ab', 'HBEFA4/PC_petrol_Euro-7']
    emission_class_valor = 'passenger'

    modificar_vclass(original_vtypes_add, new_vtypes_add, valores_vclass, emission_class_valor)
