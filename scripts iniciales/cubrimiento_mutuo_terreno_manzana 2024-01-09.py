from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry
import processing

def cubrimiento_mutuo_terreno_manzana():
    project = QgsProject.instance()

    # Buscar capas requeridas
    capa_terreno = None
    capa_manzana = None
    capa_sector_urbano = None

    for layer in project.mapLayers().values():
        parts = layer.name().split(' — ')
        if len(parts) > 1:
            if parts[1] == 'lc_terreno':
                capa_terreno = layer
            elif parts[1] == 'cc_manzana':
                capa_manzana = layer
            elif parts[1] == 'cc_sectorurbano':
                capa_sector_urbano = layer

    # Verificar si las capas requeridas están cargadas
    if not capa_terreno or not capa_manzana or not capa_sector_urbano:
        print("Falta alguna de las capas requeridas. El proceso no puede continuar.")
        return

    # Corregir geometrías
    capa_terreno_corregida = processing.run("native:fixgeometries", {'INPUT': capa_terreno, 'OUTPUT': 'memory:'})['OUTPUT']
    capa_manzana_corregida = processing.run("native:fixgeometries", {'INPUT': capa_manzana, 'OUTPUT': 'memory:'})['OUTPUT']
    capa_sector_urbano_corregida = processing.run("native:fixgeometries", {'INPUT': capa_sector_urbano, 'OUTPUT': 'memory:'})['OUTPUT']

    # Recortar 'lc_terreno' con 'cc_sectorurbano'
    capa_terreno_recortada = processing.run("native:clip", {
        'INPUT': capa_terreno_corregida,
        'OVERLAY': capa_sector_urbano_corregida,
        'OUTPUT': 'memory:'
    })['OUTPUT']

    # Encontrar huecos en 'cc_manzana' no cubiertos por 'lc_terreno'
    huecos_no_cubiertos = processing.run("native:difference", {
        'INPUT': capa_manzana_corregida,
        'OVERLAY': capa_terreno_recortada,
        'OUTPUT': 'memory:'
    })['OUTPUT']

    # Encontrar áreas de 'lc_terreno' fuera de 'cc_manzana'
    terreno_fuera_manzana = processing.run("native:difference", {
        'INPUT': capa_terreno_recortada,
        'OVERLAY': capa_manzana_corregida,
        'OUTPUT': 'memory:'
    })['OUTPUT']

    # Combinar los resultados en una capa
    resultado_final = processing.run("native:mergevectorlayers", {
        'LAYERS': [huecos_no_cubiertos, terreno_fuera_manzana],
        'OUTPUT': 'memory:'
    })['OUTPUT']

    resultado_final.setName("cubrimiento_mutuo_terreno_manzana")
    QgsProject.instance().addMapLayer(resultado_final)
    print("Capa de cubrimiento mutuo creada y añadida al proyecto.")

cubrimiento_mutuo_terreno_manzana()