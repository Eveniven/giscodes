from PyQt5.QtWidgets import QInputDialog
 
import processing

# Aktiven Layer abrufen
 
layer = iface.activeLayer()

# Überprüfen, ob ein Layer aktiv ist
 
if not layer:
 
    print("Kein aktiver Layer ausgewählt.")
 
else:
 
    # Ausgewählte Features abrufen
 
    selected_features = layer.selectedFeatures()

    if len(selected_features) == 0:
 
        print("Bitte wählen Sie ein Linien-Feature aus.")
 
    else:
 
        # Benutzer nach dem Versatz fragen
 
        x, ok = QInputDialog.getDouble(None, "Versatz eingeben", "Versatz in Metern:", decimals=2)

        if ok:
 
            # Temporären Layer erstellen, der nur das ausgewählte Feature enthält
 
            temp_layer = QgsVectorLayer("LineString?crs=" + layer.crs().authid(), "temp_layer", "memory")
 
            temp_layer_data = temp_layer.dataProvider()
 
            temp_layer_data.addAttributes(layer.fields())
 

            temp_layer.updateFields()
            temp_layer.startEditing()
 
            for feature in selected_features:
 
                temp_layer.addFeature(feature)
 
            temp_layer.commitChanges()

            # Liste der Versatzabstände (positiv und negativ)
 
            distances = [x, -x]

            # Prüfen, ob der Layer editierbar ist, andernfalls Bearbeitungsmodus starten
 
            if not layer.isEditable():
 
                layer.startEditing()

            for dist in distances:
 
                # Parameter für den Offset festlegen
 
                params = {
 
                    'INPUT': temp_layer,
 
                    'DISTANCE': dist,
 
                    'SEGMENTS': 8,
 
                    'JOIN_STYLE': 1,  # 0=Rund, 1=Flach, 2=Spitz
 
                    'MITER_LIMIT': 2,
 
                    'DISSOLVE': False,
 
                    'OUTPUT': 'memory:'
 
                }

                # Offset-Linie erzeugen
 
                result = processing.run("native:offsetline", params)
 
                offset_layer = result['OUTPUT']

                # Versetzte Features zum Original-Layer hinzufügen
 
                for offset_feature in offset_layer.getFeatures():
 
                    new_feature = QgsFeature()
 
                    new_feature.setGeometry(offset_feature.geometry())
 
                    new_feature.setAttributes(offset_feature.attributes())
 
                    layer.addFeature(new_feature)

            # Änderungen speichern
 
            layer.commitChanges()

            print("Neue versetzte Linien-Features wurden auf beiden Seiten hinzugefügt.")
 
 
