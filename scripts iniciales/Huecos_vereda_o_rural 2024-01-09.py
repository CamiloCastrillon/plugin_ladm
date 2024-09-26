from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry
import processing

def encontrar_huecos(vereda_o_rural):
    project = QgsProject.instance()

    # Buscar capas requeridas
    capa_objetivo = None
    capa_sector_urbano = None
    capa_limite_municipio = None

    for layer in project.mapLayers().values():
        parts = layer.name().split(' — ')
        print (parts)
        if len(parts) > 1:
            if parts[1] == vereda_o_rural:
                capa_objetivo = layer
                print("aui")
            elif parts[1] == 'cc_sectorurbano':
                capa_sector_urbano = layer
            elif parts[1] == 'cc_limitemunicipio':
                capa_limite_municipio = layer

    # Verificar si las capas requeridas están cargadas
    if not capa_objetivo or not capa_sector_urbano or not capa_limite_municipio:
        print(f"Falta alguna de las capas requeridas para {vereda_o_rural}. El proceso no puede continuar.")
        return

    # Corregir geometrías
    capa_objetivo_corregida = processing.run("native:fixgeometries", {'INPUT': capa_objetivo, 'OUTPUT': 'memory:'})['OUTPUT']
    capa_sector_urbano_corregida = processing.run("native:fixgeometries", {'INPUT': capa_sector_urbano, 'OUTPUT': 'memory:'})['OUTPUT']
    capa_limite_municipio_corregida = processing.run("native:fixgeometries", {'INPUT': capa_limite_municipio, 'OUTPUT': 'memory:'})['OUTPUT']

    # Realizar operaciones de diferencia para encontrar huecos
    temp_difference = processing.run("native:difference", {'INPUT': capa_limite_municipio_corregida, 'OVERLAY': capa_sector_urbano_corregida, 'OUTPUT': 'memory:'})['OUTPUT']
    resultado = processing.run("native:difference", {'INPUT': temp_difference, 'OVERLAY': capa_objetivo_corregida, 'OUTPUT': 'memory:'})['OUTPUT']

    # Crear la capa de huecos
    capa_huecos = QgsVectorLayer("Polygon?crs=" + capa_limite_municipio.crs().authid(), f"huecos_{vereda_o_rural}", "memory")
    prov = capa_huecos.dataProvider()
    for feature in resultado.getFeatures():
        prov.addFeature(feature)

    QgsProject.instance().addMapLayer(capa_huecos)
    print(f"Capa de huecos para {vereda_o_rural} creada y añadida al proyecto.")

def identificar_huecos():
    encontrar_huecos('cc_vereda')
    encontrar_huecos('cc_sectorrural')

identificar_huecos()