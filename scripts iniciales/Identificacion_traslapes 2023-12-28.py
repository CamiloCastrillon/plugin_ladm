#Importar librerias necesarias
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsFields, QgsWkbTypes
import csv
from PyQt5.QtCore import QVariant
import processing

def identificar_traslapes():
    capas_requeridas = {
        'lc_terreno': 'terreno_codigo',
        'lc_construccion': 'codigo',
        'cc_manzana': 'codigo',
        'cc_vereda': 'codigo'
    }

    project = QgsProject.instance()
    capas_cargadas = {}
    
    # Verificar si las capas requeridas están cargadas
    for capa, campo_codigo in capas_requeridas.items():
        for layer in project.mapLayers().values():
            if layer.name().endswith(capa):
                capas_cargadas[capa] = (layer, campo_codigo)
                break

    if not capas_cargadas:
        print(f"No se han cargado las capas necesarias para el análisis: {list(capas_requeridas.keys())}")
        return
    else:
        capas_faltantes = set(capas_requeridas.keys()) - set(capas_cargadas.keys())
        if capas_faltantes:
            print(f"Capas faltantes para el análisis: {capas_faltantes}")
    cant=0
    for capa, (layer, campo_codigo) in capas_cargadas.items():
        print(f"Procesando capa: {capa}")

        crs = layer.crs().authid()
        campos = QgsFields()
        campos.append(QgsField(campo_codigo, QVariant.String))
        campos.append(QgsField("Inconsistencias", QVariant.String))

        capa_traslapes = QgsVectorLayer(f"Polygon?crs={crs}", f"Traslapes_{capa}", "memory")
        prov = capa_traslapes.dataProvider()
        prov.addAttributes(campos.toList())
        capa_traslapes.updateFields()

        index = QgsSpatialIndex()
        feature_dict = {feature.id(): feature for feature in layer.getFeatures()}
        for feature in feature_dict.values():
            index.insertFeature(feature)

        traslapes_encontrados = False
        for feature in feature_dict.values():
            geom = feature.geometry()
            traslapes = []
            for id in index.intersects(geom.boundingBox()):
                other_feature = feature_dict[id]
                if feature.id() != id and geom.intersects(other_feature.geometry()):
                    traslapes.append(other_feature[campo_codigo])
                    traslape_geom = geom.intersection(other_feature.geometry())
                    
                    if not traslape_geom.isEmpty():
                        traslapes_encontrados = True
                        new_feature = QgsFeature(campos)
                        new_feature.setGeometry(traslape_geom)
                        new_feature[campo_codigo] = feature[campo_codigo]
                        new_feature["Inconsistencias"] = ', '.join(traslapes)
                        prov.addFeature(new_feature)
                        cant+=1

        if traslapes_encontrados:
            QgsProject.instance().addMapLayer(capa_traslapes)
        else:
            print(f"No se encontraron traslapes en la capa {capa}.")
    print(cant)
#Ejecutar función
#inconsistencias_terreno_municipio_urbano()
identificar_traslapes()
