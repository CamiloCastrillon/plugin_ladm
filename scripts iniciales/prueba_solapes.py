polygon_layer=iface.activeLayer()

request = QgsFeatureRequest().setSubsetOfAttributes([])
dict_features = {feature.id(): feature for feature in polygon_layer.getFeatures(request)}
#print(dict_features)
index = QgsSpatialIndex(polygon_layer)
#print(index)

for feature in polygon_layer.getFeatures(request):
    bbox = feature.geometry().boundingBox()
    #bbox = feature.geometry()
    #bbox.scale(1.000)
    #candidates_ids = index.intersects(bbox)
    candidates_ids = index.intersects(bbox)
    print(candidates_ids)
    #print(bbox)