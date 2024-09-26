from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsField, QgsFields, QgsWkbTypes
from PyQt5.QtCore import QVariant


#Cargar capas requeridas para esta prueba
project = QgsProject.instance()

# Buscar capas requeridas
lc_terreno = None
vereda = None
sector_urbano = None
limite_municipio = None
manzana = None
perimetro_urbano = None
sector_rural = None


#Dividir nombre y cargarlos como layers
for layer in project.mapLayers().values():
    parts = layer.name().split(' — ')
    print(parts[1])
    if len(parts) > 1:
        if parts[1] == 'lc_terreno':
            lc_terreno = layer
        elif parts[1] == 'cc_vereda':
            vereda = layer
        elif parts[1] == 'cc_sectorurbano':
            sector_urbano = layer
        elif parts[1] == 'cc_limitemunicipio':
            limite_mmunicipio = layer
        elif parts[1] == 'cc_manzana':
            manzana = layer
        elif parts[1] == 'cc_perimetrourbano':
            perimetro_urbano = layer
        elif parts[1] == 'cc_sectorrural':
            sector_rural = layer
            

#Funcion para verificar contenencia, layer 1 contenido totalmente o no dentro de layer 2
def verificar_contenencia(layer_1, layer_2):
    # Extraer nombres de las capas para el nombre de la capa de resultados
    nombre_layer_1 = layer_1.name().split(' — ')[-1]  # Asumiendo el formato "Algo — Nombre"
    nombre_layer_2 = layer_2.name().split(' — ')[-1]

    # Verificar contenencia
    resultado = processing.run("native:difference", {
        'INPUT': layer_1,
        'OVERLAY': layer_2,
        'OUTPUT': 'TEMPORARY_OUTPUT'
    })
    no_contenidos_layer = resultado['OUTPUT']

    if no_contenidos_layer.featureCount() > 0:
        # Nombrar la capa de resultados
        nombre_resultado = f"NC_{nombre_layer_1}_{nombre_layer_2}"
        no_contenidos_layer.setName(nombre_resultado)

        # Añadir la capa al proyecto para mostrar elementos no contenidos
        QgsProject.instance().addMapLayer(no_contenidos_layer)
        return False, no_contenidos_layer
    else:
        return True, None


# Ejemplo de como se aplica en las capas de perimetro urbano dentro de sector urbano
resultado_contenencia_1, capa_no_contenida_1 = verificar_contenencia(perimetro_urbano, sector_urbano)
if resultado_contenencia_1:
    print("cc_perimetrourbano está completamente contenida en cc_sectorurbano")
else:
    print("cc_perimetrourbano no está completamente contenida en cc_sectorurbano. Ver la capa no_contenidos.")

# Ejemplo de como se aplica en las capas de vereda dentro de sector rural
resultado_contenencia_2, capa_no_contenida_2 = verificar_contenencia(vereda, sector_rural)
if resultado_contenencia_2:
    print("cc_vereda está completamente contenida en cc_sectorrural")
else:
    print("cc_vereda no está completamente contenida en cc_sectorrural. Ver la capa no_contenidos.")

#y Asi se puede hacer con todas las capas disponible
#Perimetro urbano dentro de corregimiento
#Construccion dentro de terreno