from qgis.utils import iface
from qgis.core import QgsProject, QgsVectorLayer
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from qgis.core import Qgis, QgsField, QgsFeatureRequest, QgsVectorLayer
from qgis import processing
from qgis.PyQt.QtCore import QVariant
from datetime import datetime

# Se instancia el proyecto
project = QgsProject.instance()

    # Reglas de validacion del Ing Miguel Idrobo
    # Segun las reglas establecidas en el modelo LADM COL V1.2

#Esta funcion se llama como una libreria desde el plugin principal  
def regla1(self):

    #Para generar un aviso en la parte superior de la ventana grafica que indique se estan corriendo las regla de validacion
    iface.messageBar().pushMessage("Regla1",'En ejecición por favor espere', level=Qgis.Info, duration=10)
    now = datetime.now()
    hoy = now.strftime('%Y/%m/%d %H:%M')

    #Esta varaiable va a ir concatenando los mensajes que sean necesarios
    global mensajes
    mensajes=""

    #Funcion para cargar las capas al contenido de Qgis
    def cargar_capa(geopackage_path, layer_name):
        """
        Carga una capa desde un GeoPackage.
        """
        uri = f"{geopackage_path}|layername={layer_name}"
        layer = QgsVectorLayer(uri, layer_name, "ogr")
        if not layer.isValid():
            #print(f"Error al cargar la capa {layer_name}")
            #return None
            #Para hacer que los textos se puedan concatenar, tienes la opcion de ponerlos en una variable y concatenar las salidas 
            mens ="Geometria invalida\n"
        else:
            mens ="Geometria valida\n"
        QgsProject.instance().addMapLayer(layer)
        return layer, mens

    """
    Evalúa si los polígonos de dos capas coinciden plenamente.
    """
    def evaluar_coincidencia(layer1, layer2):
        for feature1 in layer1.getFeatures():
            geom1 = feature1.geometry()
            for feature2 in layer2.getFeatures():
                geom2 = feature2.geometry()
                if geom1.equals(geom2):
                    #print("Ambos límites coinciden plenamente")
                    mens ="Ambos límites coinciden plenamente\n"
                    return mens
                else:
                    #print("Los límites no coinciden plenamente: Operador debe corregir este caso de inconsistencia.")
                    mens ="Los límites no coinciden plenamente: Operador debe corregir este caso de inconsistencia.\n"
                    return mens
                        

    # Ejemplo de uso
    #path_capas = "C:/Users/USUARIO/Desktop/Catastro-Multiproposito/Capas Ejemplo/"
    path_capas = "F:/Universidad/Proyecto UV/Prueba/"
    Purb = path_capas + "CC_Perimetrourbano.gpkg"
    POT = path_capas + "Perimetro Urbano POT B.gpkg"
    capa1, mens = cargar_capa(Purb, "CC_Perimetrourbano")
    mensajes += mens
    capa2, mens = cargar_capa(POT, "Perimetro Urbano POT B")
    mensajes += mens


    #En caso que las capas ya esten cargas en el Qgis se pueden es buscar por nombre.
    #capa1 = project.mapLayersByName('CC_Perimetrourbano')[0]
    #capa2 = project.mapLayersByName('Perimetro Urbano POT B')[0]

    if capa1 and capa2:
        mens = evaluar_coincidencia(capa1, capa2)
        mensajes += mens

    #El label_3 es un objeto en la ventana grafica en la pestaña 3 que se creo en el QtDesing
    self.label_3.setText(mensajes)    