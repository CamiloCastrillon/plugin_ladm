"""
Contiene funciones para transformar archivos ili en otros formatos de bases de datos, usando las herramientas de interlist:
    Consultar para descarga en: https://www.interlis.ch/en/downloads/ili2db
    Contultar para documentación en: https://github.com/claeis/ili2db/blob/master/docs/ili2db_es.rst

Última Actualización: Octubre 2 de 2024
Juan Camilo Navia Castrillón ; juan.navia.castrillon@correounivalle.edu.co
"""
import subprocess
import os
import shutil

def ili2gpkg(ili_path:str, gpkg_path:str, epsg:str):
    """
    Convierte un archivo en formato ili (interlis) a gpkg, usando la herramienta ili2gpkg.
    
    Args:
        ili_path    (str): Ruta donde se encuentra el archivo ili a convertir.
        gpkg_path   (str): Ruta donde se desea guardar el archivo gpkg
        epsg        (str): Código del sistema de referencia al que se desea proyectar la base de datos (se recomienda 9377 para Colombia)
    
    Returns:
        str: Texto de confirmación de importación o error.
    """

    # Obtener la ruta del archivo script.py
    current_folder  = os.path.dirname(os.path.abspath(__file__))
    # Obtiene la ruta con los recursos java para hacer la conversión de archivos
    ili2gpkg_path   = os.path.join(current_folder, 'ili2gpkg', 'ili2gpkg-5.1.1.jar')
    # Obtiene la ruta de java
    java_path       = os.path.join(current_folder, 'jre-1.8', 'bin', 'java.exe')
    # Verifica la existencia del archivo ISO19107_PLANAS_V3_0.ili en el path de archivo ili, sino, lo instala
    folder_path     = os.path.dirname(ili_path)                                 # Obtiene la carpeta donde se encuentra el ili a convertir
    files_folder    = os.listdir(folder_path)                                   # Obtiene la lista de archivos dentro de la carpeta
    iso_path        = os.path.join(current_folder, 'ISO19107_PLANAS_V3_0.ili')  # Obtiene la ruta del archivo ili a copiar
    if 'ISO19107_PLANAS_V3_0.ili' in files_folder:                              # Itera sobre los archivos, si no encuentra ISO19107_PLANAS_V3_0.ili, crea un copia y la añade
        pass
    else:
        shutil.copy(iso_path, folder_path)
    # Construye el comando a ejecutar
    command= f'"{java_path}" -jar "{ili2gpkg_path}" --schemaimport --dbfile "{gpkg_path}" --defaultSrsCode "{epsg}" "{ili_path}"'
    # Ejecutar el comando
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    # Verificar el resultado
    if result.returncode == 0:
        print(f'La importación fue exitosa en: {gpkg_path}.')
        return print(result.stdout)
    else:
        print('Error en la importación.')
        return print(result.stderr)