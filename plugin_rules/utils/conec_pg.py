"""
Este script se conecta a una base de datos PostgreSQL y extrae todas las tablas de un esquema específico (hmll). 
Luego, utiliza la interfaz de QGIS para establecer una capa vectorial (QgsVectorLayer) para cada tabla en el 
esquema, cargando sus campos.
"""
from qgis.core import QgsDataSourceUri, QgsVectorLayer
import psycopg2

# Define los parámetros de conexión a la base de datos
host        = "localhost"
user        = "postgres"
password    = "postgres"
port        = "5432"
nom_db      = "harold_mercado"

#Crea la conexión
conexion=psycopg2.connect(host=host, user=user, password=password, port=port, database= nom_db)	

# Define un cursor para ejecutar comandos con SQL
cur = conexion.cursor()

# Define el nombre del esquema dentro de la base de datos donde se desean hacer las consultas
nom_esq='hmll'
query = f"select * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{nom_esq}'"

# Ejecuta una consulta
cur.execute(query)

#Guarda el resultado de la consulta
scheme_tables = cur.fetchall()

# Se utiliza para establecer una conexión a una capa de datos de PostgreSQL.
uri = QgsDataSourceUri()

# Configura la conexión utilizando los parámetros definidos previamente
uri.setConnection(host, port, nom_db, user, password)

# Crea y carga la lista de tablas del esquema
tab_esq_list=list()
tab_esq_list.clear()
for n in scheme_tables:
    tab_esq_list.append(n)
    print(str(n))
    uri.setDataSource(nom_esq, n[2], 'geom')
    vlayer = QgsVectorLayer(uri.uri(), n[2], "postgres")
    print(vlayer)
    print(vlayer.fields().toList())