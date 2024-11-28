from PyQt5.QtWidgets import QInputDialog
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsWkbTypes
)
from qgis.PyQt.QtCore import QVariant

# Funktion zur Erstellung von Punkten entlang der Linien
def create_points_along_lines(line_layer, distance):
    # Neuer Punktlayer
    point_layer = QgsVectorLayer("Point?crs=" + line_layer.crs().toWkt(), "Generated Points", "memory")
    point_layer_provider = point_layer.dataProvider()
    point_layer_provider.addAttributes([QgsField("Meter", QVariant.Double)])
    point_layer.updateFields()
    
    for line_feature in line_layer.getSelectedFeatures():
        geom = line_feature.geometry()
        if geom.isMultipart():
            lines = geom.asMultiPolyline()
        else:
            lines = [geom.asPolyline()]

        # Punkte generieren
        for line in lines:
            current_distance = 0
            total_length = geom.length()

            # Punkt am Anfang der Linie
            start_point = geom.interpolate(0).asPoint()
            start_feature = QgsFeature()
            start_feature.setGeometry(QgsGeometry.fromPointXY(start_point))
            start_feature.setAttributes([0])
            point_layer_provider.addFeature(start_feature)

            # Punkte entlang der Linie
            while current_distance < total_length:
                if current_distance != 0:  # Verhindere Duplikat des Anfangspunkts
                    point = geom.interpolate(current_distance).asPoint()
                    point_feature = QgsFeature()
                    point_feature.setGeometry(QgsGeometry.fromPointXY(point))
                    point_feature.setAttributes([current_distance])
                    point_layer_provider.addFeature(point_feature)
                current_distance += distance

            # Punkt am Ende der Linie
            end_point = geom.interpolate(total_length).asPoint()
            end_feature = QgsFeature()
            end_feature.setGeometry(QgsGeometry.fromPointXY(end_point))
            end_feature.setAttributes([total_length])
            point_layer_provider.addFeature(end_feature)

    # Punktlayer zur Karte hinzufügen
    QgsProject.instance().addMapLayer(point_layer)

# Hauptskript
# Aktuellen Linienlayer auswählen
layer = iface.activeLayer()

if not layer or layer.geometryType() != QgsWkbTypes.LineGeometry:
    iface.messageBar().pushWarning("Fehler", "Bitte wähle einen Linienlayer aus.")
else:
    # Dialogfenster zur Eingabe der Punktabstände
    distance, ok = QInputDialog.getDouble(None, "Punkte generieren", "Abstand zwischen Punkten (Meter):", 10, 0.1, 10000, 1)
    
    if ok:
        create_points_along_lines(layer, distance)
        iface.messageBar().pushInfo("Erfolg", "Punkte wurden erfolgreich generiert.")
