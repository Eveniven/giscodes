from PyQt5.QtWidgets import QSlider, QVBoxLayout, QDialog, QLabel
from PyQt5.QtCore import Qt
from qgis.core import QgsProject, QgsRasterLayer

class TiffSlider(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Radargramme Visualisierung")
        self.resize(300, 150)
        
        # Layergruppe suchen
        self.radar_group = QgsProject.instance().layerTreeRoot().findGroup("Radargramme")
        if not self.radar_group:
            raise ValueError("Keine Layergruppe mit dem Namen 'Radargramme' gefunden!")
        
        # TIFF-Layer in der Gruppe sammeln
        self.tiff_layers = [
            layer.layer()
            for layer in self.radar_group.children()
            if isinstance(layer.layer(), QgsRasterLayer)
        ]
        
        if not self.tiff_layers:
            raise ValueError("Keine Rasterlayer (.tiff) in der Gruppe 'Radargramme' gefunden!")
        
        # Slider einrichten
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.tiff_layers) - 1)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.update_layers)

        # Labels für Anzeige
        self.label_layer_index = QLabel("Aktueller Layer: 0")
        self.label_layer_name = QLabel("Layer-Name: ---")

        # Layout erstellen
        layout = QVBoxLayout()
        layout.addWidget(self.label_layer_index)
        layout.addWidget(self.label_layer_name)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        # Layer initial einstellen
        self.update_layers(0)
    
    def update_layers(self, value):
        """Aktualisiert die Sichtbarkeit und Transparenz der Layer basierend auf dem Sliderwert."""
        current_layer = self.tiff_layers[value]
        self.label_layer_index.setText(f"Aktueller Layer: {value + 1} von {len(self.tiff_layers)}")
        self.label_layer_name.setText(f"Layer-Name: {current_layer.name()}")

        for i, layer in enumerate(self.tiff_layers):
            if i < value:
                layer.renderer().setOpacity(0.0)  # Obere Layer vollständig transparent
            elif i == value:
                layer.renderer().setOpacity(1.0)  # Aktuellen Layer vollständig sichtbar
            else:
                layer.renderer().setOpacity(0.0)  # Untere Layer vollständig transparent
            
            # Rendereränderungen anwenden
            layer.triggerRepaint()

# Dialog starten
try:
    controller = TiffSlider()
    controller.exec_()
except ValueError as e:
    iface.messageBar().pushWarning("Radargramme Tool", str(e))

