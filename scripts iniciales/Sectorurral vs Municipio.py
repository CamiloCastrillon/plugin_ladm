from processing.tools import dataobjects
layer1=QgsProject.instance().mapLayersByName("lc_terreno")[0]
layer2=QgsProject.instance().mapLayersByName("cc_limitemunicipio")[0]
context = dataobjects.createContext()
int=processing.run("native:intersection", {'INPUT':layer1,'OVERLAY':layer2,'INPUT_FIELDS':[],'OVERLAY_FIELDS':[],'OVERLAY_FIELDS_PREFIX':'','OUTPUT':'TEMPORARY_OUTPUT','GRID_SIZE':None},context.setInvalidGeometryCheck(QgsFeatureRequest.GeometryNoCheck))

list_id=dict()
for x in int['OUTPUT'].getFeatures():
    list_id[x['fid']]=x.geometry().area()

id_comdentro=list()
id_pardentro=list()
id_parfuera=list()
id_comfuera=list()
for x in layer1.getFeatures():
    area=x.geometry().area()
    if x['fid'] in list_id:
        if round(area,0)==round(list_id[x['fid']],0):
            id_comdentro.append(x['fid'])
        else:
            if round(area/2,0)>round(list_id[x['fid']],0):
                id_parfuera.append(x['fid'])
            else:
                id_pardentro.append(x['fid'])
    else:
        id_comfuera.append(x['fid'])
        
print(f"completamente dentro {str(id_comdentro)}")
print(f"parcialmente dentro {str(id_pardentro)}")
print(f"parcialmente fuera {str(id_parfuera)}")
print(f"complemente fuera {str(id_comfuera)}")
