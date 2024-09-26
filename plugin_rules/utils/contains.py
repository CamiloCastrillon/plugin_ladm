"""
El siguiente script tendrá funciones relacionadas con reglas sobre contención entre capas
"""
from qgis.core import QgsProject
from qgis import processing

def contains_by_2_layers(name_container:str, name_verify:str):
    """
    Crea la diferencia de una capa contenedora y otra a verificar, a partir del 
    resultado determina si hay o no contención de la segunda capa en la primera,
    contando los geometrías resultantes de la diferencia entre las capas.
    
    Si el resultado es 0, la capa está completamente contenida, de lo contrario,
    la capa tiene geometrías fuera, estas geometrías se van a cargar al mapa con
    el nombre 'NC_[nombre de la capa contenedora]_[nombre de la capa a verificar
    ]'.
    
    Args:
        name_container  (str): Nombre de la capa contenedora.
        name_verify     (str): Nombre de la capa a verificar
    """
    # Obtener las capas por su nombre
    container_layer = QgsProject.instance().mapLayersByName(name_container)[0]
    verify_layer    = QgsProject.instance().mapLayersByName(name_verify)[0]

    # Definir parámetros para la herramienta de diferencia
    params = {
        'INPUT'     : verify_layer,
        'OVERLAY'   : container_layer,
        'OUTPUT'    : 'TEMPORARY_OUTPUT'  # Guardar el resultado de forma temporal
    }

    # Ejecutar la herramienta de diferencia
    result= processing.run("native:difference", params)

    # Obtener la capa de resultado
    no_contained_layer = result['OUTPUT']

    # Comprobar si la capa de resultado está vacía
    if no_contained_layer.featureCount() == 0:
        #Imprime un aviso como salída para la función
        return print(f"Todos los polígonos de {name_verify} están contenidos dentro de {name_container}.")
    else:
        # Nombrar la capa de resultados
        name_ouput_layer = f"NC_{name_container}_{name_verify}"
        no_contained_layer.setName(name_ouput_layer)
        # Añadir la capa al proyecto para mostrar elementos no contenidos
        QgsProject.instance().addMapLayer(no_contained_layer)
        return print(f"Hay polígonos en {name_verify} que no están contenidos dentro de {name_container}.")