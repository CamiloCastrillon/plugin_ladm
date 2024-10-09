# Importar la clase QgsProject
from qgis.core import QgsProject
import processing

def obtain_layers_name():
    """
    Obtiene las capas que están encendidas en un ptoyecto qgis.
    """
    # Obtener la instancia del proyecto actual
    project = QgsProject.instance()
    # Obtener todas las capas cargadas en el proyecto
    layers = project.mapLayers().values()
    # Obtiene los nombres y añade en listas
    names = tuple(layer.name() for layer in layers)

    return names

def fix_geometry(layer):
    """
    Aplica la operación de corregir capas a una capa, tentativamente esta capa debe tener geometrías invalidas.
    """
    fix_layer = processing.run("native:fixgeometries", {'INPUT': layer, 'OUTPUT': 'memory:'})['OUTPUT']
    return fix_layer