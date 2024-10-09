from osgeo import gdal, ogr
import pandas as pd

def open_gpkg(gpkg_path:str):
    """
    Abre un archivo .gpkg usando gdal y devuelve el objeto dataset si este tiene información
    
    Args:
        gpkg_path   (str): Ruta al archivo gpkg.
        
    Returns:
        dataset: Variable GDAL con el dataset cargado.
    """
    # Abrir el GeoPackage
    driver  = ogr.GetDriverByName('GPKG')   # Define el formato del archivo a manejar
    dataset =  driver.Open(gpkg_path)       # Abre el gpkg y lo almacena en dataset
    
    if dataset is None:                     # Verifica la existencia de información en gpkg
        print('El dataset está vacío')
    else:
        return dataset

def gpkg_descriptor(gpkg_path:str):
    """
    Obtiene la información de la estructura de un archivo gpkg, capturando los
    nombres de las capas, tipos de geometría, y datos de los campos como sus
    nombres, tipos de dato y longitud. Estos datos se guardan en un diccionario 
    con la siguiente extructura:
    
    {
    'nombre de las capas'   : [nombres de las capas],
    'tipos de geometrias'   : [tipos de geometría de las capas],
    'campos'                :{
                                'nombres'       : [nombres de los campos],
                                'tipos'         : [tipo de dato de cada campo],
                                'longitudes'    : [longitud de cada campo]
    }
    
    Args:
        gpkg_path   (str): Ruta al archivo gpkg.
        
    Returns:
        gpkg_dic    (dict): Diccionario con los datos del GeoPackage.
    """
    
    gpkg        = open_gpkg(gpkg_path)  # Abre el gpkg y lo almacena en la variable 'gpkg'
    layer_count = gpkg.GetLayerCount()  # Obtiene el número total de capas en el gpkg
    
    # Almacena los nombres de los tipos de geometrías en gdal y su equivalente en qgis
    equivalent_geometries ={
    '3D Compound Curve' : 'CompoundCurveZ',
    '3D Curve Polygon'  : 'CurvePolygonZ',
    '3D Multi Surface'  : 'MultiSurfaceZ',
    '3D Multi Curve'    : 'MultiCurveZ',
    'None'              : 'NoGeometry'
    }
    
    gpkg_dic        = {}    # Almacenará toda la información del gpkg
    layer_names     = []    # Almacenará los nombres de las capas
    geometry_types  = []    # Almacenará los tipos de geometría de cada capa
    field_data      = []    # Almacenará los datos de los campos de cada capa
    
    for i in range(layer_count):                    # Itera sobre cada capa

        # Obtiene los nombres de las capas
        layer       = gpkg.GetLayerByIndex(i)   # Obtiene la capa por el índice
        layer_name  = layer.GetName()           # Obtiene el nómbre de la capa
        layer_names.append(layer_name)          # Añade el nombre a la lista
    
        # Obtiene el nombre del el tipo de geometría
        geometry_type = layer.GetGeomType()                             # Obtiene el tipo de geometría GDAL
        geom_type_name = ogr.GeometryTypeToName(geometry_type)          # Obtiene el nombre del tipo de geometría GDAL
        geometry_types.append(equivalent_geometries[geom_type_name])    # Añade el tipo de geometría QGIS a la lista
        
        # Obtiene la información de los campos
        field_information   = {}                        # Almacenará la información de los campos
        field_names         = []                        # Almacenará los nombres de los campos
        field_types         = []                        # Almacenará los typos de datos de cada campo
        field_lengths       = []                        # Almacenará la longitud de cada campo
        layer_def           = layer.GetLayerDefn()      # Obtiene la definición de la capa (información)
        for j in range(layer_def.GetFieldCount()):      # Itera sobre la información de esta definición
            field_def       = layer_def.GetFieldDefn(j) # Obtiene la definición del campo sobre el que se itera
            field_names.append(field_def.GetName())     # Obtiene y añade el nombre del capo
            field_types.append(field_def.GetTypeName()) # Obtiene y añade el tipo de dato en el campo
            field_lengths.append(field_def.GetWidth())  # Obtiene y añade la longitud del campo
        
        # Añade la información del campo
        field_information['nombres']        = field_names   # Añade la información de nombres al diccionario
        field_information['tipos']          = field_types   # Añade la información de tipos al diccionario
        field_information['longitudes']     = field_lengths # Añade la información de longitudes al diccionario
        field_data.append(field_information)                # Añade el diccionario a la lista de fiel data
        
    # Añade los datos al diccionario
    gpkg_dic['nombres de capas']        = layer_names       # Añade los nombres de las capas
    gpkg_dic['tipos de geometrias']     = geometry_types    # Añade los tipos de geometrías
    gpkg_dic['campos']                  = field_data        # Añade la información de los campos de cada capa
    
    return gpkg_dic

def gpkg_show(gpkg_diccionario:dict, csv_folder:str):
    """
    Accede a la información del diccionario creado por la función gpkg_descriptor,
    organizandola en data frames de pandas para su exportación en archivos csv en
    la carpeta que designa el usuario, se exporta un archivo con el resumen del
    nombre de las capas y sus tipos de geometrías, también, un archivo por cada
    capa describiendo sus campos (nombres, tipo de dato y longitud).
    
    Args:
        gpkg_path   (str): Ruta al archivo gpkg.
        csv_folder  (str): Ruta a la carpeta donde se guardarán los archivos csv.
        
    Returns:
        None:   La función no devuelve ningún argumento.
    """
    # Define las listas con los datos a insertar en los dataframes
    list_names  = gpkg_diccionario['nombres de capas']       # Nombres de las capas
    list_types  = gpkg_diccionario['tipos de geometrias']    # Tipos de geometrías
    list_fields = gpkg_diccionario['campos']                 # Datos de los campos

    # Crea el diccionario con los datos de la tabla de capas y tipos de geometria
    dicc_layers_types = {
        'Nombres de las capas'  : list_names,
        'Tipo de geometria'     : list_types}
    
    # Exporta la tabla
    df_layers_types = pd.DataFrame(dicc_layers_types)               # Crear un DataFrame con los datos de capas y tipos de geometría
    df_layers_types.to_csv(f'{csv_folder}/Resumen_de_capas.csv')   # Exporta un csv con los datos del dataframe creado
    
    index = 0               # Inicializa un contador para saber el índice de la capa que se está iterando
    for name in list_names: # Itera sobre los nombres de las capas
        
        # Con el indice, accede a los datos de los campos de la capa
        list_field_names    = list_fields[index]['nombres']      # Almacena los datos de nombre
        list_field_types    = list_fields[index]['tipos']        # Almacena los datos de tipos
        list_field_length   = list_fields[index]['longitudes']   # Almacena los datos de longitud
        
        # Crea un diccionario con los datos de los campos para cada capa
        dicc_field_data = {
            'Nombre del campo'  : list_field_names,
            'Tipo de dato'      : list_field_types,
            'Longitud'          : list_field_length}
        
        # Exporta la tabla
        df_field_data = pd.DataFrame(dicc_field_data)           # Crear un DataFrame con los datos de los campos de la capa
        df_field_data.to_csv(f'{csv_folder}/Campos_{name}.csv') # Exporta un csv con los datos del dataframe creado
        
        index += 1  # Actualiza el index para la siguiente capabilities