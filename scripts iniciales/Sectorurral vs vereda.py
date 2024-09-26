layer1=QgsProject.instance().mapLayersByName("cc_vereda")[0]
layer2=QgsProject.instance().mapLayersByName("cc_sectorrural")[0]

list_id=dict()
for x in layer2.getFeatures():
    id=x['fid']
    sel=processing.run("qgis:selectbyattribute", {'INPUT':layer2,'FIELD':'fid','OPERATOR':0,'VALUE':id,'METHOD':0})
    memory_layer = layer2.materialize(QgsFeatureRequest().setFilterFids(layer2.selectedFeatureIds()))
    int= processing.run("native:selectbylocation", {'INPUT':layer1,'PREDICATE':[5],'INTERSECT':memory_layer,'METHOD':0})
    
    list_id_v=list()
    list_id_v.clear()
    for feat in int['OUTPUT'].selectedFeatures():
        list_id_v.append(feat['fid'])
    
    list_id[id]=list_id_v

for x in range(1,len(list_id)):
    print(len(list_id[x]))
"""

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
"""