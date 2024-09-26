#Versión 2: Permite crear capas temporales y un campo con inconsistencias

from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsFields, QgsWkbTypes
import csv
from PyQt5.QtCore import QVariant
import processing


def cargar_capa(geopackage_path, layer_name):
    """
    Carga una capa desde un GeoPackage.
    """
    uri = f"{geopackage_path}|layername={layer_name}"
    layer = QgsVectorLayer(uri, layer_name, "ogr")
    if not layer.isValid():
        print(f"Error al cargar la capa {layer_name}")
        return None
    QgsProject.instance().addMapLayer(layer)
    return layer
    
def verificar_y_generar_reporte(capa_terrenos, capa_limite_urbano, capa_limite_municipio, ruta_reporte):
    """
    Verifica la capa de terrenos y genera un reporte en un archivo CSV,
    y crea una nueva capa temporal con las inconsistencias.
    """
    # Verificar si la capa tiene el campo 'Numero_Predial'
    if 'codigo' not in capa_terrenos.fields().names():
        print("La capa no tiene el campo 'Numero Predial'.")
        return
    else:
        print("La capa cumple con el campo 'Numero Predial'.")
        return

    informe = []
    campos = QgsFields()
    campos.append(QgsField("codigo_catastral", QVariant.String))
    campos.append(QgsField("Inconsistencias", QVariant.String))

    # Crear una nueva capa de memoria para inconsistencias con los campos definidos
    capa_inconsistencias = QgsVectorLayer("Polygon?crs=EPSG:3115", "Inconsistencias_de_Limites", "memory")
    prov = capa_inconsistencias.dataProvider()
    prov.addAttributes([QgsField("codigo_catastral", QVariant.String), QgsField("Inconsistencias", QVariant.String)])
    capa_inconsistencias.updateFields()

    for feature in capa_terrenos.getFeatures():
        numero_predial = feature["codigo"]
        geom_predio = feature.geometry()
        descripcion = ""

        # Evaluación con respecto al límite urbano
        es_urbano = numero_predial and numero_predial[5:7] == '01'
        area_total = geom_predio.area()
        area_dentro_limite = sum(geom_predio.intersection(perimetro.geometry()).area() for perimetro in capa_limite_urbano.getFeatures())
        porcentaje_dentro_limite = (area_dentro_limite / area_total) * 100

        if es_urbano and porcentaje_dentro_limite < 50:
            descripcion = "Inconsistencia o no conformidad 50% supera el límite urbano"
        elif not es_urbano and porcentaje_dentro_limite >= 50:
            descripcion = "Inconsistencia o no conformidad 50% se encuentra dentro del perímetro urbano"

        # Evaluación con respecto al límite municipal
        esta_dividido = False
        esta_fuera = True
        for municipio in capa_limite_municipio.getFeatures():
            if geom_predio.intersects(municipio.geometry()):
                esta_fuera = False
                if not geom_predio.within(municipio.geometry()):
                    esta_dividido = True
                    break

        if esta_dividido:
            descripcion = "El predio se encuentra dividido entre dos municipios"
        elif esta_fuera:
            descripcion = "Predio completamente fuera del límite Municipal"

        if descripcion:
            # Añadir feature a la nueva capa de inconsistencias
            new_feature = QgsFeature(campos)
            new_feature.setGeometry(feature.geometry())
            new_feature["codigo_catastral"] = numero_predial
            new_feature["Inconsistencias"] = descripcion
            prov.addFeature(new_feature)

            # Añadir al informe
            informe.append({'codigo_catastral': numero_predial, 'descripcion': descripcion})

    # Añadir la capa de inconsistencias al proyecto QGIS
    QgsProject.instance().addMapLayer(capa_inconsistencias)

    # Escribir los resultados en un archivo CSV
    with open(ruta_reporte, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['codigo_catastral', 'descripcion']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for fila in informe:
            writer.writerow(fila)

#Identifica traslape entre poligonos de terreno (genera un reporte y una capa diferencia)
def identificar_traslapes_y_generar_reporte(capa_terrenos, ruta_reporte_traslapes):
    """
    Identifica traslapes en la capa de terrenos, genera un reporte y crea una capa con los traslapes en un archivo CSV.
    """
    informe_traslapes = []
    campos = QgsFields()
    campos.append(QgsField("codigo_catastral", QVariant.String))
    campos.append(QgsField("Inconsistencias", QVariant.String))

    
    capa_traslapes = QgsVectorLayer("Polygon?crs=EPSG:4326", "Traslapes", "memory")
    prov = capa_traslapes.dataProvider()
    prov.addAttributes(campos.toList())
    capa_traslapes.updateFields()

    for feature1 in capa_terrenos.getFeatures():
        traslapes = []
        for feature2 in capa_terrenos.getFeatures():
            if feature1.id() != feature2.id() and feature1.geometry().intersects(feature2.geometry()):
                traslapes.append(feature2["codigo"])

        if traslapes:
            new_feature = QgsFeature()
            new_feature.setGeometry(feature1.geometry())
            new_feature.setFields(campos, True)
            new_feature.setAttribute("codigo_catastral", feature1["codigo"])
            new_feature.setAttribute("Inconsistencias", ', '.join(traslapes))
            prov.addFeature(new_feature)

            informe_traslapes.append({
                'codigo_catastral': feature1["codigo"],
                'traslapes': ', '.join(traslapes)
            })

    QgsProject.instance().addMapLayer(capa_traslapes)

    # Escribir los resultados en un archivo CSV
    with open(ruta_reporte_traslapes, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['codigo_catastral', 'traslapes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for fila in informe_traslapes:
            writer.writerow(fila)
            
        
#Identifica los huecos entre el Limite Municipal y 
def identificar_huecos_y_crear_capa(capa_limite_mun, capa_terrenos, ruta_salida_huecos):
    """
    Identifica huecos dentro de 'CC_LimiteMunicipio' no cubiertos por 'LC_Terreno'.
    """
    # Recortar LC_Terreno con CC_Perimetrourbano
    capa_terrenos_cortados = processing.run("native:clip", {
        'INPUT': capa_terrenos,
        'OVERLAY': capa_limite_mun,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })['OUTPUT']

    # Calcular la diferencia para encontrar huecos
    processing.run("native:difference", {
        'INPUT': capa_limite_mun,
        'OVERLAY': capa_terrenos_cortados,
        'OUTPUT': ruta_salida_huecos
    })

    # Cargar la capa de huecos como QgsVectorLayer y añadirla al lienzo de QGIS
    capa_huecos = QgsVectorLayer(ruta_salida_huecos, "Huecos", "ogr")
    if not capa_huecos.isValid():
        print("Error al cargar la capa de huecos")
        return
    QgsProject.instance().addMapLayer(capa_huecos)


#CARGUE DE CAPAS Y SALIDA DE RESULTADOS Y REPORTES
# Rutas y nombres de las capas
path = "G:/Mi unidad/Proyecto Catastro Multiproposito/Ejemplo/SantanderQ/"
geopackage = path + "Lev_Cat_V1_2.gpkg"
ruta_reporte = path + "reporte.csv"
ruta_reporte_traslapes = path + "reporte_traslapes.csv"
ruta_salida_huecos = path + "huecos_perimetro_urbano.shp"

# Cargar las capas
capa_limite_municipio = cargar_capa(geopackage, "CC_LimiteMunicipio")
capa_limite_urbano = cargar_capa(geopackage, "CC_Perimetrourbano")
capa_terrenos = cargar_capa(geopackage, "LC_Terreno")


## Uso de la funciones
#verificar_y_generar_reporte(capa_terrenos, capa_limite_urbano, capa_limite_municipio, ruta_reporte)
identificar_traslapes_y_generar_reporte(capa_terrenos, ruta_reporte_traslapes)
identificar_huecos_y_crear_capa(capa_limite_municipio, capa_terrenos, ruta_salida_huecos)