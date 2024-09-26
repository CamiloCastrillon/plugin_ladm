from qgis.core import (QgsProject, QgsVectorLayer, QgsField, QgsFeature, QgsGeometry)
from PyQt5.QtCore import QVariant
import processing

def identificar_huecos_lc_terreno():
    capas_requeridas = ['cc_limitemunicipio', 'cc_perimetrourbano', 'lc_terreno']
    project = QgsProject.instance()

    # Verificar la presencia de las capas en el proyecto
    capa_lc_terreno = None
    capa_limite_urbano = None
    capa_limite_municipio = None
    faltan_capas = False

    nombres_capas_cargadas = set()
    for layer in project.mapLayers().values():
        parts = layer.name().split(' — ')
        if len(parts) > 1:
            nombres_capas_cargadas.add(parts[1])

    for capa in capas_requeridas:
        if capa in nombres_capas_cargadas:
            for layer in project.mapLayers().values():
                if layer.name().endswith(capa):
                    # Corregir geometrías, 
                    result = processing.run("native:fixgeometries", {
                        'INPUT': layer,
                        'OUTPUT': 'memory:'
                    })['OUTPUT']

                    # Asignar la capa corregida a la variable correspondiente
                    if capa == 'lc_terreno':
                        capa_lc_terreno = result
                    elif capa == 'cc_perimetrourbano':
                        capa_limite_urbano = result
                    elif capa == 'cc_limitemunicipio':
                        capa_limite_municipio = result
                    break
        else:
            print(f"Falta la capa: {capa}")
            faltan_capas = True

    if faltan_capas:
        print("No se pueden cargar algunas capas requeridas o falta un campo necesario. El proceso no puede continuar.")
        return

    print("Todas las capas requeridas están cargadas correctamente. Procesando...")
    
    # Recortar LC_Terreno con CC_Perimetrourbano
    capa_terrenos_cortados = processing.run("native:clip", {
        'INPUT': capa_lc_terreno,
        'OVERLAY': capa_limite_urbano,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Calcular la diferencia para encontrar huecos dentro del límite urbano
    capa_huecos_urbanos = processing.run("native:difference", {
        'INPUT': capa_limite_urbano,
        'OVERLAY': capa_terrenos_cortados,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Calcular la diferencia para encontrar huecos fuera del límite urbano (en el límite municipal)
    capa_huecos_rurales = processing.run("native:difference", {
        'INPUT': capa_limite_municipio,
        'OVERLAY': capa_lc_terreno,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Combinar las capas de huecos urbanos y rurales en una capa temporal
    capa_huecos = processing.run("native:mergevectorlayers", {
        'LAYERS': [capa_huecos_urbanos, capa_huecos_rurales],
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Añadir un campo para categorizar los huecos
    processing.run("native:addfieldtoattributestable", {
        'INPUT': capa_huecos,
        'FIELD_NAME': 'Huecos',
        'FIELD_TYPE': 2,  # String
        'FIELD_LENGTH': 20,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })

    # Cargar la capa de huecos y añadirla al lienzo de QGIS
    if not capa_huecos.isValid():
        print("Error al cargar la capa de huecos")
        return

    capa_huecos.setName("Huecos_lc_terreno")
    QgsProject.instance().addMapLayer(capa_huecos)
    print("Capa de huecos identificados añadida al proyecto.")




identificar_huecos_lc_terreno()
