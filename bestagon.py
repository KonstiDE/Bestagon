# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bestagon
                                 A QGIS plugin
 Form (mostly Hexagon) generator for point intensities
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-05
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Konstantin Müller
        email                : konstantinfinn.mueller@gmx.de
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
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *

import processing
from .resources import *

from .form_processes.process_special import (
    triangle,
    fishers_net
)

from .form_processes.process_base import (
    base_forms
)

# Initialize Qt resources from file resources.py
# Import the code for the dialog
from .bestagon_dialog import bestagonDialog
import os.path


class bestagon:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.dlg = None
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'bestagon_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Bestagon')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('bestagon', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/bestagon/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Bestagon'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Bestagon'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        forms = {
            "Rectangle": 2,
            "Diamond": 3,
            "Hexagon": 4
        }
        special_forms = {
            "Triangle",
            "Fishernet (beta)"
        }
        colors_keys = [
            "Greys", "Blues", "Greens", "Reds", "Purples", "Magma", "Inferno", "Viridis", "Spectral", "Plasma", "BrBG",
            "BuGn", "BuPu", "GnBu", "OrRd", "PiYG", "PRGn", "PuBu", "PuBuGn", "PuOr", "PuRd", "RdBu", "RdGy", "RdGy",
            "RdPu", "RdYlBu", "RdYlGn"
        ]

        default_style = QgsStyle().defaultStyle()

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = bestagonDialog()

            # init filters
            self.dlg.mMapLayerComboBox_points.setFilters(QgsMapLayerProxyModel.PointLayer)
            self.dlg.mMapLayerComboBox_shape.setFilters(QgsMapLayerProxyModel.PolygonLayer)

            # init values
            self.dlg.comboBox_form.addItems(forms.keys())
            self.dlg.comboBox_form.addItems(special_forms)
            ramp_select = self.dlg.comboBox_ramps

            for color_key in colors_keys:
                ramp_select.addItem(
                    QgsSymbolLayerUtils.colorRampPreviewIcon(default_style.colorRamp(color_key), QSize(16, 16)),
                    color_key)

        self.dlg.button_box.accepted.disconnect()
        self.dlg.button_box.accepted.connect(self.run)

        # show the dialog
        self.dlg.show()

        # init default views
        point_layer_select = self.dlg.mMapLayerComboBox_points
        shape_layer_select = self.dlg.mMapLayerComboBox_shape
        ramp_select = self.dlg.comboBox_ramps
        progress_bar = self.dlg.progressBar

        log = self.dlg.log_entry
        tab = self.dlg.tabWidget

        edit_width = self.dlg.lineEdit_width
        edit_height = self.dlg.lineEdit_height

        spin_num_classes = self.dlg.spinBox_classes

        # Processing feedback
        def progress_changed(progress):
            progress_bar.setValue(progress)

        f = QgsProcessingFeedback()
        f.progressChanged.connect(progress_changed)

        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            log.clear()

            tab.setCurrentIndex(1)

            log.insertHtml("Started formizing...<br>")
            log.insertHtml("Loading Suuiii!<br><br>")

            form = self.dlg.comboBox_form.currentText()
            cut = self.dlg.checkBox_cut.isChecked()
            cut_soft = self.dlg.checkBox_soft.isChecked()

            points = point_layer_select.currentLayer()

            if points is not None:
                if form in forms.keys() or form in special_forms:
                    log.append("Selected form: " + form)
                    log.append("")

                    # Fetch form size
                    try:
                        width = float(edit_width.text())
                        height = float(edit_height.text())

                        log.append("Found width to be: " + str(width) + "km")
                        log.append("Found height to be: " + str(height) + "km")
                        log.append("")
                        log.append("")
                        log.append("")

                        extent = points.extent()
                        crs = points.sourceCrs()

                        if form in special_forms:
                            if form.startswith("Triangle"):
                                grid = triangle(crs=crs, width=width, height=height, extent=extent, feedback_process=f)
                            elif form.startswith("Fishernet"):
                                grid = fishers_net(crs=crs, width=width, height=height, extent=extent,
                                                   feedback_process=f)
                        else:
                            grid = base_forms(crs=crs, width=width, height=height, extent=extent, form_id=forms[form],
                                              feedback_process=f)

                        intensities = processing.run("native:countpointsinpolygon", {
                            'POLYGONS': grid,
                            'POINTS': points,
                            'WEIGHT': '',
                            'CLASSFIELD': '',
                            'FIELD': 'NUMPOINTS',
                            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                        }, feedback=f)['OUTPUT']

                        log.append("Successfully build intensity-grid.")

                        if cut:
                            shape_layer = shape_layer_select.currentLayer()

                            if shape_layer is not None:
                                if not cut_soft:
                                    intensities = processing.run("native:clip", {
                                        'INPUT': intensities,
                                        'OVERLAY': shape_layer,
                                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                                    }, feedback=f)['OUTPUT']
                                else:
                                    intensities = processing.run("native:extractbylocation", {
                                        'INPUT': intensities,
                                        'PREDICATE': [0],
                                        'INTERSECT': shape_layer,
                                        'OUTPUT': 'TEMPORARY_OUTPUT'
                                    }, feedback=f)['OUTPUT']

                                log.append("Successfully cutted to shapefile (Softcut: " + str(cut_soft) + ").")
                            else:
                                log.insertHtml(
                                    "<p style=\"color:#FF0000\";><b>Error processing shape layer</b></p><br>")
                                log.insertHtml(
                                    "<p style=\"color:#FF0000\";>Please select a valid shape to cut your form layer to.</p><br>")

                        max_value = max([feat["NUMPOINTS"] for feat in intensities.getFeatures()])

                        num_classes = round(max_value / 2)
                        classification_method = QgsClassificationJenks()

                        amount_of_classes_evtl = spin_num_classes.value()

                        if amount_of_classes_evtl > 0:
                            num_classes = amount_of_classes_evtl
                        else:
                            log.insertHtml(
                                "<p style=\"color:#f2b202\";>Number of classes was smaller than one. Selecting <b>" + str(
                                    num_classes) + "</b> as default.</p><br>")

                        ramp_format = QgsRendererRangeLabelFormat()
                        ramp_format.setFormat("%1 - %2")
                        ramp_format.setPrecision(2)
                        ramp_format.setTrimTrailingZeroes(True)

                        renderer = QgsGraduatedSymbolRenderer()
                        renderer.setClassAttribute('NUMPOINTS')
                        renderer.setClassificationMethod(classification_method)
                        renderer.setLabelFormat(ramp_format)
                        renderer.updateClasses(intensities, num_classes)
                        renderer.updateColorRamp(default_style.colorRamp(colors_keys[ramp_select.currentIndex()]))

                        intensities.setRenderer(renderer)
                        intensities.triggerRepaint()

                        intensities.setName('Intensity')

                        log.append("Successfully styled. Adding layer...")
                        log.append("")

                        QgsProject.instance().addMapLayer(intensities)

                        log.insertHtml("<span style=\"color:#1bb343\";>---------------------------</span><br>")
                        log.insertHtml("<span style=\"color:#1bb343\";>| Finished processing. |</span><br>")
                        log.insertHtml("<span style=\"color:#1bb343\";>---------------------------</span><br>")

                        progress_bar.setValue(progress_bar.maximum())

                    except TypeError:
                        log.insertHtml("<p style=\"color:#FF0000\";><b>Error fetching form size...</b></p><br>")
                        log.insertHtml("<p style=\"color:#FF0000\";>Please provide valid numbers in kilometer.</p><br>")

                else:
                    log.insertHtml("<p style=\"color:#FF0000\";><b>Error selecting a form...</b></p><br>")
                    log.insertHtml("<p style=\"color:#FF0000\";>Please select a valid form.</p><br>")

            else:
                log.insertHtml("<p style=\"color:#FF0000\";><b>Error fetching point layer...</b></p><br>")
                log.insertHtml("<p style=\"color:#FF0000\";>Please provide valid layer containing only points.</p><br>")


def resolve(name, basepath=None):
    if not basepath:
        basepath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(basepath, name)
