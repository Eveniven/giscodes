#_init_.py

from .tiff_slider import TiffSlider
from .resources import *

def classFactory(iface):
    return TiffSlider(iface)

#plugin.py

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from .tiff_slider_dialog import TiffSliderDialog
from qgis.core import QgsMessageLog
from qgis.PyQt.QtCore import QCoreApplication

class TiffSlider:
    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        # Correct path to icon using embedded resources
        icon_path = ":/plugins/tiff_slider/icon.png"  # Use the correct resource path
    
        # Create the QIcon using the correct path
        icon = QIcon(icon_path)
    
        # Create the QAction and associate it with the icon and a label
        self.action = QAction(icon, QCoreApplication.translate('TiffSlider', 'Radargramme Visualisierung'), self.iface.mainWindow())
        self.action.triggered.connect(self.run)  # Connect the action to the run method
 
        # Add the icon to the toolbar
        self.iface.addToolBarIcon(self.action)
 
        # Add the action to the plugin menu
        self.iface.addPluginToMenu("&TiffSlider", self.action)

    def unload(self):
        # Remove the action from the plugin menu
        self.iface.removePluginMenu("&TiffSlider", self.action)

    def run(self):
        # Create and execute the dialog
        dialog = TiffSliderDialog(self.iface)
        dialog.exec_()


#plugin_dialog.py

import os

from PyQt5.QtWidgets import QDialog, QSlider, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from qgis.core import QgsProject, QgsRasterLayer

class TiffSliderDialog(QDialog):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.iface = iface
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

