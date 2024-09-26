from utils.ili2any import ili2gpkg

ili_path    = 'C:\camilo\Monitoria\monitoria_harold\info_geografica\ili\Submodelo_Cartografia_Catastral_V1_2.ili'
gpkg_path   = 'C:\camilo\Monitoria\monitoria_harold\info_geografica\ili\Submodelo_Cartografia_Catastral_V1_2.gpkg'
epsg        = '9377'

ili2gpkg(ili_path, gpkg_path, epsg)