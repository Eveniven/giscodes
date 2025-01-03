# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TiffSliderDialog
                                 A QGIS plugin
 It slides Tiffs.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-12-04
        git sha              : $Format:%H$
        copyright            : (C) 2024 by RKIW
        email                : idgaf@dimanet.de
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt5.QtWidgets import QDialog, QSlider, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt5.QtCore import Qt
from qgis.core import QgsProject, QgsRasterLayer, QgsLayerTreeGroup

class TiffSliderDialog(QDialog):
    def __init__(self, iface):
        """Initializes the dialog."""
        super().__init__()
        self.iface = iface
        self.tiff_layers = []
        self.setup_ui()
        self.populate_layer_groups()

    def setup_ui(self):
        """Sets up the user interface."""
        self.setWindowTitle("Tiff Slider")
        self.resize(300, 150)
        
        # Create widgets
        self.label_info = QLabel("Select a layer group:")
        self.combo_group = QComboBox()
        self.slider = QSlider(Qt.Horizontal)
        self.label_layer_index = QLabel("Current layer: ---")
        self.label_layer_name = QLabel("Layer name: ---")
        
        # Initialize slider
        self.slider.setMinimum(0)
        self.slider.valueChanged.connect(self.update_layers)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.label_info)
        layout.addWidget(self.combo_group)
        layout.addWidget(self.label_layer_index)
        layout.addWidget(self.label_layer_name)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        # Connect signals
        self.combo_group.currentIndexChanged.connect(self.on_group_selection)

    def populate_layer_groups(self):
        """Populates the ComboBox with all layer groups."""
        self.combo_group.clear()  # Clear previous options
        root = QgsProject.instance().layerTreeRoot()
        
        # Add all groups from the layer tree
        for group in root.children():
            if isinstance(group, QgsLayerTreeGroup):
                self.combo_group.addItem(group.name(), group)

    def on_group_selection(self, index):
        """Called when a group is selected in the ComboBox."""
        group = self.combo_group.itemData(index)
        if group:
            self.tiff_layers = [
                layer.layer()
                for layer in group.children()
                if isinstance(layer.layer(), QgsRasterLayer)
            ]
            
            if not self.tiff_layers:
                self.label_layer_index.setText("No raster layers found.")
                self.label_layer_name.setText("Layer name: ---")
                self.slider.setMaximum(0)
                return

            # Configure slider
            self.slider.setMaximum(len(self.tiff_layers) - 1)
            self.slider.setValue(0)
            self.update_layers(0)
        else:
            # Clear labels and reset the slider if no valid group is selected
            self.tiff_layers = []
            self.label_layer_index.setText("No raster layers found.")
            self.label_layer_name.setText("Layer name: ---")
            self.slider.setMaximum(0)

    def update_layers(self, value):
        """Updates the display and visibility of layers based on the slider value."""
        if not self.tiff_layers:
            return

        current_layer = self.tiff_layers[value]
        self.label_layer_index.setText(f"Current layer: {value + 1} of {len(self.tiff_layers)}")
        self.label_layer_name.setText(f"Layer name: {current_layer.name()}")

        for i, layer in enumerate(self.tiff_layers):
            if i == value:
                layer.renderer().setOpacity(1.0)  # Current layer fully visible
            else:
                layer.renderer().setOpacity(0.0)  # Other layers invisible
            
            # Apply changes
            layer.triggerRepaint()

