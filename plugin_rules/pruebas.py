from manage_gpkg import gpkg_descriptor, gpkg_show

# Define las rutas
gpkg_file   = r'C:\camilo\Monitoria\monitoria_harold\info_geografica\ili\1.2\Submodelo_Cartografia_Catastral_V1_2.gpkg'
csv_folder  = r'C:\camilo\Monitoria\monitoria_harold\info_geografica\csv'

gpkg_diccionario = gpkg_descriptor(gpkg_file)
gpkg_show(gpkg_diccionario, csv_folder)








