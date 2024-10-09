"""
El siguiente script tendrá funciones relacionadas con reglas sobre contención entre capas.

Última Actualización: Septiembre 26 del 2024
Juan Camilo Navia Castrillón ; juan.navia.castrillon@correounivalle.edu.co
"""
from qgis.core import QgsProject, QgsSpatialIndex, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField
from qgis import processing
from PyQt5.QtCore import QVariant
import geopandas as gpd

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

def contains_by_2_layers_2(name_container:str, name_verify:str):
    """
    Asigna un indice espacial a la capa contenedora y obtiene los indices de la capa que intersectan con las
    geometrias de la capa a verificar, luego se observa si estas están completamente contenidas o no, en caso
    de no estarlo, se añaden a una nueva capa y esta se carga de forma temporal en qgis.
    
    Args:
        name_container  (str): Nombre de la capa contenedora.
        name_verify     (str): Nombre de la capa a verificar
    """
    # Obtener las capas por su nombre
    container_layer = QgsProject.instance().mapLayersByName(name_container)[0]
    verify_layer    = QgsProject.instance().mapLayersByName(name_verify)[0]

    # Crear un índice espacial para la capa contenedora
    index = QgsSpatialIndex()
    for feature1 in container_layer.getFeatures():
        index.insertFeature(feature1)

    # Crea una capa de memoria temporal para almacenar las geometrías no contenidas
    output_layer = QgsVectorLayer('Polygon?crs=' + verify_layer.crs().authid(), 'No Contenidas', 'memory')
    provider = output_layer.dataProvider()
    
    # Copiar los campos (atributos) de la capa original
    provider.addAttributes(verify_layer.fields())
    output_layer.updateFields()

    # Recorre las características de la capa que quieres verificar
    for feature2 in verify_layer.getFeatures():
        geom2 = feature2.geometry()  # Geometría de la capa 2
        
        # Obtiene las características potenciales del índice espacial
        candidate_ids = index.intersects(geom2.boundingBox())
        
        # Verificar si geom2 está completamente contenida en alguna de las geometrías candidatas
        contained = False
        for feature_id in candidate_ids:
            candidate_feature = container_layer.getFeature(feature_id)
            geom1 = candidate_feature.geometry()
            
            if geom1.contains(geom2):
                contained = True
                break  # Si está contenida, no necesitamos revisar más geometrías
        
        # Si no está contenida, añadirla a la nueva capa
        if not contained:
            # Agregar la característica a la capa de salida si no está contenida
            provider.addFeature(feature2)
    
    # Añade la nueva capa al proyecto de QGIS como capa temporal
    QgsProject.instance().addMapLayer(output_layer)

def contains_by_2_layers_gpd(name_container: str, name_verify: str):
    """
    Verifica si las geometrías de una capa están completamente contenidas en otra.
    Aquellas que no están contenidas se almacenan en una nueva capa y se cargan en QGIS.

    Args:
        name_container (str): Nombre de la capa contenedora.
        name_verify    (str): Nombre de la capa a verificar.
    """
    # Obtener las capas por su nombre desde QGIS
    container_layer = QgsProject.instance().mapLayersByName(name_container)[0]
    verify_layer    = QgsProject.instance().mapLayersByName(name_verify)[0]

    # Obtiene las rutas de las capas
    container_path  = container_layer.dataProvider().dataSourceUri().split('|')[0]
    verify_path     = verify_layer.dataProvider().dataSourceUri().split('|')[0]
    
    # Convertir las capas a GeoDataFrames
    container_gdf   = gpd.read_file(container_path)
    verify_gdf      = gpd.read_file(verify_path)

    # Asegurarse de que ambas capas tengan el mismo CRS
    if container_gdf.crs != verify_gdf.crs:
        verify_gdf = verify_gdf.to_crs(container_gdf.crs)

    # Crear un índice espacial usando Rtree
    container_sindex = container_gdf.sindex
    
    # Lista para almacenar geometrías no contenidas
    not_contained = []

    # Recorre las características de la capa a verificar
    for idx, verify_geom in verify_gdf.iterrows():
        # Obtener los índices de las posibles geometrías que intersectan
        possible_matches_index = list(container_sindex.intersection(verify_geom.geometry.bounds))
        possible_matches = container_gdf.iloc[possible_matches_index]

        # Verificar si la geometría está contenida en alguna de las intersectadas
        contained = False
        for _, container_geom in possible_matches.iterrows():
            if container_geom.geometry.contains(verify_geom.geometry):
                contained = True
                break

        # Si no está contenida, añadirla a la lista
        if not contained:
            not_contained.append(verify_geom)

    # Crear un GeoDataFrame para las geometrías no contenidas
    not_contained_gdf = gpd.GeoDataFrame(not_contained, columns=verify_gdf.columns)

    # Crear una capa de memoria temporal para almacenar las geometrías no contenidas
    output_layer = QgsVectorLayer('Polygon?crs=' + verify_layer.crs().authid(), 'No Contenidas', 'memory')
    provider = output_layer.dataProvider()
    output_layer.startEditing()
    
    # Definir campos (atributos) en la nueva capa
    fields = [QgsField(col, QVariant.String) for col in verify_gdf.columns]
    provider.addAttributes(fields)
    output_layer.updateFields()

    # Añadir las geometrías no contenidas a la capa temporal
    for _, row in not_contained_gdf.iterrows():
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromWkt(row.geometry.wkt))  # Convertir la geometría de GeoPandas a QGIS
        feature.setAttributes(row.tolist())      # Asignar atributos
        output_layer.addFeature(feature)

    # Actualizar la capa para que refleje los cambios
    output_layer.commitChanges()

    # Añadir la capa temporal al proyecto de QGIS
    QgsProject.instance().addMapLayer(output_layer)