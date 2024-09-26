import psycopg2
host="localhost"
user="postgres"
passw="12345"
port="5432"
nom_db= "harold_mercado"
conexion=psycopg2.connect(host=host, user="postgres", password="postgres", port="5432", database= "harold_mercado")	
cur = conexion.cursor()
nom_esq="hmll"
cur.execute(f"select * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{nom_esq}'")
tab_esq = cur.fetchall()

uri = QgsDataSourceUri()
uri.setConnection(host, port, nom_db, user, passw)

tab_esq_list=list()
tab_esq_list.clear()
for n in tab_esq:
    tab_esq_list.append(n)
    print(str(n))
    uri.setDataSource(nom_esq, n[2], 'geom')
    vlayer = QgsVectorLayer(uri.uri(), n[2], "postgres")
    print(vlayer)
    print(vlayer.fields().toList())