# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TiffSlider
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
        self.action = QAction(icon, QCoreApplication.translate('TiffSlider', 'Radargram Visualization'), self.iface.mainWindow())
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
