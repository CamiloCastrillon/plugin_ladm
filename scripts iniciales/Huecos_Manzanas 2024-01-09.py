from qgis.core import QgsProject, QgsVectorLayer
import processing

def encontrar_huecos_manzana():
    project = QgsProject.instance()

    # Buscar capas requeridas
    capa_manzana = None
    capa_sector_urbano = None

    for layer in project.mapLayers().values():
        parts = layer.name().split(' — ')
        if len(parts) > 1:
            if parts[1] == 'cc_manzana':
                capa_manzana = layer
            elif parts[1] == 'cc_sectorurbano':
                capa_sector_urbano = layer

    # Verificar si las capas requeridas están cargadas
    if not capa_manzana or not capa_sector_urbano:
        print("Falta alguna de las capas requeridas. El proceso no puede continuar.")
        return

    # Corregir geometrías
    capa_manzana_corregida = processing.run("native:fixgeometries", {
        'INPUT': capa_manzana,
        'OUTPUT': 'memory:'
    })['OUTPUT']

    capa_sector_urbano_corregida = processing.run("native:fixgeometries", {
        'INPUT': capa_sector_urbano,
        'OUTPUT': 'memory:'
    })['OUTPUT']

    # Realizar la operación de diferencia para encontrar huecos
    resultado = processing.run("native:difference", {
        'INPUT': capa_sector_urbano_corregida,
        'OVERLAY': capa_manzana_corregida,
        'OUTPUT': 'memory:'
    })

    # Crear la capa de huecos
    capa_huecos = resultado['OUTPUT']
    capa_huecos.setName('huecos_cc_manzana')
    QgsProject.instance().addMapLayer(capa_huecos)

    print("Capa de huecos creada y añadida al proyecto.")

encontrar_huecos_manzana()