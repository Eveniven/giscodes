from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsGeometry,
    QgsPointXY,
    QgsWkbTypes,
    QgsField
)
from qgis.PyQt.QtCore import QVariant

# Aktuellen Layer abrufen
layer = iface.activeLayer()

# Überprüfen, ob ein Layer geladen ist
if not layer:
    print("Bitte wähle einen Layer aus.")
elif layer.geometryType() != QgsWkbTypes.LineGeometry:
    print("Der aktive Layer muss ein Linien-Layer sein.")
else:
    # Liste für Knoten sammeln
    nodes = {}

    # Alle Features durchgehen
    for feature in layer.getSelectedFeatures():
        geom = feature.geometry()

        if not geom.isMultipart():
            # Start- und Endpunkte für Singlepart-Linien
            line_points = geom.asPolyline()  # Alle Punkte der Linie abrufen
            if len(line_points) >= 2:
                start_point = QgsPointXY(line_points[0])
                end_point = QgsPointXY(line_points[-1])
            else:
                print(f"Feature-ID {feature.id()} hat keine gültigen Punkte.")
                continue
        else:
            print(f"Mehrteilige Geometrien werden aktuell nicht unterstützt (Feature-ID: {feature.id()}).")
            continue

        # Punkte zu den Nodes hinzufügen
        for point in [start_point, end_point]:
            key = f"{point.x():.6f},{point.y():.6f}"
            if key not in nodes:
                nodes[key] = []
            nodes[key].append(feature.id())

    # Fehlerhafte Knoten identifizieren
    error_points = []
    for node, feature_ids in nodes.items():
        if len(feature_ids) == 1:  # Nur ein Feature an diesem Knoten => Fehlerhaft
            coords = node.split(",")
            error_points.append(QgsPointXY(float(coords[0]), float(coords[1])))

    # Punktlayer erstellen
    if error_points:
        # Neuer Punktlayer
        point_layer = QgsVectorLayer("Point?crs=" + layer.crs().authid(), "Fehlerhafte Punkte", "memory")
        data_provider = point_layer.dataProvider()
        data_provider.addAttributes([QgsField("id", QVariant.Int)])
        point_layer.updateFields()

        # Punkte hinzufügen
        for idx, point in enumerate(error_points):
            point_feature = QgsFeature()
            point_feature.setGeometry(QgsGeometry.fromPointXY(point))
            point_feature.setAttributes([idx + 1])  # ID zuweisen
            data_provider.addFeature(point_feature)

        # Layer hinzufügen
        QgsProject.instance().addMapLayer(point_layer)
        print(f"{len(error_points)} fehlerhafte Punkte wurden im neuen Layer 'Fehlerhafte Punkte' erstellt.")
    else:
        print("Keine fehlerhaften Verbindungen gefunden.")
