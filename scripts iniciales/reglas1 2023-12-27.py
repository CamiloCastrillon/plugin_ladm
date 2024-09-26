from qgis.utils import iface
from qgis.core import QgsProject, QgsVectorLayer, QgsFeature, QgsField, QgsFields, QgsWkbTypes, QgsProcessingFeedback
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from qgis.core import Qgis, QgsField, QgsFeatureRequest, QgsVectorLayer
from qgis import processing
from qgis.PyQt.QtCore import QVariant
from datetime import datetime
import csv


# Se instancia el proyecto
project = QgsProject.instance()

    # Reglas de validacion del Ing Miguel Idrobo
    # Segun las reglas establecidas en el modelo LADM COL V1.2

#Esta funcion se llama como una libreria desde el plugin principal  
def regla1(self,clases_val,nom_clase_val):

    #Para generar un aviso en la parte superior de la ventana grafica que indique se estan corriendo las regla de validacion
    iface.messageBar().pushMessage("Regla1",'En ejecición por favor espere', level=Qgis.Info, duration=10)
    now = datetime.now()
    hoy = now.strftime('%Y/%m/%d %H:%M')

    #Esta varaiable va a ir concatenando los mensajes que sean necesarios
    global mensajes
    global mens
    global informe
    mensajes=""
    mens=""
    informe=list()

    """

    #Funcion para cargar las capas al contenido de Qgis
    def cargar_capa(geopackage_path, layer_name):
        #Carga una capa desde un GeoPackage.
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
        return layer
        self.br_prog.setValue(5)


    #Evalúa si los polígonos de dos capas coinciden plenamente.

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
    """


    def verificar_y_generar_reporte(capa_terrenos, capa_limite_urbano, capa_limite_municipio, ruta_reporte):
        """
        Verifica la capa de terrenos y genera un reporte en un archivo CSV,
        y crea una nueva capa temporal con las inconsistencias.
        """
        # Verificar si la capa tiene el campo 'Numero_Predial'
        descripcion = ""

        if 'terreno_codigo' not in capa_terrenos.fields().names():
            #print("La capa no tiene el campo 'Numero_Predial'.")
            #return
            # HM:Se envia el resultado
            descripcion+=f"{capa_terreno.name()} La capa no tiene el campo 'terreno_codigo'."


        informe = []
        campos = QgsFields()
        campos.append(QgsField("codigo_catastral", QVariant.String))
        campos.append(QgsField("Inconsistencias", QVariant.String))

        # Crear una nueva capa de memoria para inconsistencias con los campos definidos
        # Tomar el sistema de coordenadas de las mismas capas que se esten trabajando
        epsg=capa_terrenos.crs().toWkt()
        capa_inconsistencias = QgsVectorLayer("Polygon?crs="+epsg, "Inconsistencias_de_Limites", "memory")
        prov = capa_inconsistencias.dataProvider()
        prov.addAttributes([QgsField("codigo_catastral", QVariant.String), QgsField("Inconsistencias", QVariant.String)])
        capa_inconsistencias.updateFields()

        cant=0
        for feature in capa_terrenos.getFeatures():
            # HM: El numero predial se llama en la capas lc_terreno como Terreno_Codigo
            numero_predial = feature["terreno_codigo"]
            geom_predio = feature.geometry()
            descripcion = ""

            # Evaluación con respecto al límite urbano
            es_urbano = numero_predial and numero_predial[5:7] == '01'
            area_total = geom_predio.area()
            area_dentro_limite = sum(geom_predio.intersection(perimetro.geometry()).area() for perimetro in capa_limite_urbano.getFeatures())
            porcentaje_dentro_limite = (area_dentro_limite / area_total) * 100

            if es_urbano and porcentaje_dentro_limite < 50:
                descripcion += "Inconsistencia o no conformidad 50% supera el límite urbano"
            elif not es_urbano and porcentaje_dentro_limite >= 50:
                descripcion += "Inconsistencia o no conformidad 50% se encuentra dentro del perímetro urbano"

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
                descripcion += "El predio se encuentra dividido entre dos municipios"
            elif esta_fuera:
                descripcion += "Predio completamente fuera del límite Municipal"

            if descripcion:
                # Añadir feature a la nueva capa de inconsistencias
                new_feature = QgsFeature(campos)
                new_feature.setGeometry(feature.geometry())
                new_feature["codigo_catastral"] = numero_predial
                new_feature["Inconsistencias"] = descripcion
                prov.addFeature(new_feature)

                # Añadir al informe
                informe.append({'codigo_catastral': numero_predial, 'descripcion': descripcion})

            cant+=1
            prog=(cant/len(capa_terrenos))*100
            self.br_prog.setValue(prog)

        # Añadir la capa de inconsistencias al proyecto QGIS
        QgsProject.instance().addMapLayer(capa_inconsistencias)

        """
        # Escribir los resultados en un archivo CSV
        with open(ruta_reporte, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['codigo_catastral', 'descripcion']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for fila in informe:
                writer.writerow(fila)
        """


    #Identifica traslape entre poligonos de terreno (genera un reporte y una capa diferencia)
    def identificar_traslapes_y_generar_reporte(capa_terrenos, ruta_reporte_traslapes):
        """
        Identifica traslapes en la capa de terrenos, genera un reporte y crea una capa con los traslapes en un archivo CSV.
        """
        informe_traslapes = []
        campos = QgsFields()
        campos.append(QgsField("codigo_catastral", QVariant.String))
        campos.append(QgsField("Inconsistencias", QVariant.String))

        # HM:Toma el SRC de la capa que se este trabajando
        epsg=capa_terrenos.crs().toWkt()
        capa_traslapes = QgsVectorLayer("Polygon?crs="+epsg, "Traslapes", "memory")
        prov = capa_traslapes.dataProvider()
        prov.addAttributes(campos.toList())
        capa_traslapes.updateFields()

        cant=0
        for feature1 in capa_terrenos.getFeatures():
            traslapes = []
            for feature2 in capa_terrenos.getFeatures():
                if feature1.id() != feature2.id() and feature1.geometry().intersects(feature2.geometry()):
                    traslapes.append(feature2["terreno_codigo"])

            if traslapes:
                new_feature = QgsFeature()
                new_feature.setGeometry(feature1.geometry())
                new_feature.setFields(campos, True)
                new_feature.setAttribute("codigo_catastral", feature1["terreno_codigo"])
                new_feature.setAttribute("Inconsistencias", ', '.join(traslapes))
                prov.addFeature(new_feature)

                informe_traslapes.append({
                    'codigo_catastral': feature1["terreno_codigo"],
                    'traslapes': ', '.join(traslapes)
                })

            prog=(cant/len(capa_terrenos))*100
            self.br_prog.setValue(prog)


        QgsProject.instance().addMapLayer(capa_traslapes)

        """
        # Escribir los resultados en un archivo CSV
        with open(ruta_reporte_traslapes, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['codigo_catastral', 'traslapes']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for fila in informe_traslapes:
                writer.writerow(fila)
        """        
            
    #Identifica los huecos entre el Limite Municipal y 
    def identificar_huecos_y_crear_capa(capa_limite_mun, capa_terrenos, ruta_salida_huecos):
        # para generar la barra de proceso
        """
        def progress_changed(progress):
            self.br_prog.setValue(progress)
        feed = QgsProcessingFeedback()
        feed.progressChanged.connect(progress_changed)
        
        usar , feedback=feed al fnal de cada proccesing.
        """

        """
        Identifica huecos dentro de 'CC_LimiteMunicipio' no cubiertos por 'LC_Terreno'
        y los muestra en el lienzo de QGIS como una capa temporal.
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
            #print("Error al cargar la capa de huecos")
            mens += "Error al cargar la capa de huecos"
            return
        QgsProject.instance().addMapLayer(capa_huecos)
    """
    #CARGUE DE CAPAS Y SALIDA DE RESULTADOS Y REPORTES
    # Rutas y nombres de las capas
    #path = "C:/Users/USUARIO/Desktop/Catastro-Multiproposito/Capas Ejemplo/"
    """
    path = "D:/"
    #geopackage = path + "LADM_COL_Palmira_06122023.gpkg"
    ruta_reporte = path + "reporte.csv"
    ruta_reporte_traslapes = path + "reporte_traslapes.csv"
    ruta_salida_huecos = path + "huecos_perimetro_urbano.shp"

    """
    # Cargar las capas
    #capa_limite_municipio = cargar_capa(geopackage, "CC_LimiteMunicipio")
    #capa_limite_urbano = cargar_capa(geopackage, "CC_Perimetrourbano")
    #capa_terrenos = cargar_capa(geopackage, "LC_Terreno")
    """

    ## Uso de la funciones
    # Los datos estan en las variables globales:
    # clases_val = variable que contiene una lista de las entidades vectoriales
    # nom_clase_val = variable que contiene una lista de los nombres de las entidades vectoriales con los mismos indices de la variable capas
    # la carga se puede hacer desde las variables anteriores

    # se consulta si las capas que se requieren estan cargadas.

    if "lc_terreno" in nom_clase_val and "cc_limitemunicipio" in nom_clase_val and "cc_perimetrourbano" in nom_clase_val:
        pos_c=nom_clase_val.index("lc_terreno")
        capa_terrenos=clases_val[pos_c]
        pos_c=nom_clase_val.index("cc_perimetrourbano")
        capa_limite_urbano=clases_val[pos_c]
        pos_c=nom_clase_val.index("cc_limitemunicipio")
        capa_limite_municipio=clases_val[pos_c]
        verificar_y_generar_reporte(capa_terrenos, capa_limite_urbano, capa_limite_municipio, ruta_reporte)

    if "lc_terreno" in nom_clase_val:
        pos_c=nom_clase_val.index("lc_terreno")
        capa_terrenos=clases_val[pos_c]
        identificar_traslapes_y_generar_reporte(capa_terrenos, ruta_reporte_traslapes)


    if "lc_terreno" in nom_clase_val and "cc_limitemunicipio" in nom_clase_val:
        pos_c=nom_clase_val.index("lc_terreno")
        capa_terrenos=clases_val[pos_c]
        pos_c=nom_clase_val.index("cc_limitemunicipio")
        capa_limite_municipio=clases_val[pos_c]
        identificar_huecos_y_crear_capa(capa_limite_municipio, capa_terrenos)
   

    # Mensaje que aparecen en la 3 pestaña del plugin
    mensajes += str(informe)
    self.tabWidget.setTabEnabled(6,True)
    self.tabWidget.setCurrentIndex(6)
    self.rep_topl.setText(mensajes)
