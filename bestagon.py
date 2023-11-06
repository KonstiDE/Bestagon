# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtWebKit import *

from qgis.core import *
from qgis import processing

from .resources import *

from .bestagon_dialog import bestagonDialog

from .form_processes.process_base import base_forms
from .form_processes.process_special import (
    triangle,
    fishers_net
)

from time import sleep
from datetime import datetime
import os.path
import random


forms = {
    "Rectangle": 2,
    "Diamond": 3,
    "Hexagon": 4
}
special_forms = {
    "Triangle",
    "Fishernet",
    "Bubbles / Heatmap"
}
colors_keys = [
    "Greys", "Blues", "Greens", "Reds", "Purples", "Magma", "Inferno", "Viridis", "Spectral", "Plasma", "BrBG",
    "BuGn", "BuPu", "GnBu", "OrRd", "PiYG", "PRGn", "PuBu", "PuBuGn", "PuOr", "PuRd", "RdBu", "RdGy", "RdGy",
    "RdPu", "RdYlBu", "RdYlGn"
]

default_style =  QgsStyle().defaultStyle()


class Worker(QThread):
    finished = pyqtSignal(object)
    progress = pyqtSignal(int)

    def __init__(self, log, context, params):
        super().__init__()

        self.result = None
        self.feedback = None
        self.stopworker = False
        self.log = log
        self.context = context

        self.params = params

        self.point_layer = params["point_layer"]
        self.form = params["form"]
        self.width = params["width"]
        self.height = params["height"]
        self.shape_layer = params["shape_layer"]
        self.mask = params["mask"]
        self.keep_form = params["keep_form"]
        self.color_ramp = params["color_ramp"]
        self.number_of_classes = params["number_of_classes"]
        self.render_quality = params["render_quality"]

    def progress_changed(self, progress):
        self.progress.emit(progress)

    def run(self):
        self.progress.emit(0)
        self.feedback = QgsProcessingFeedback()
        self.feedback.progressChanged.connect(self.progress_changed)

        self.feedback.setProgressText("Running processing algorithm...")

        self.log.append("I am here!")
        self.progress.emit(10)

        try:
            # Additionaly objects needed
            project_crs = QgsProject.instance().crs()
            point_crs = self.point_layer.crs()
            extent = self.shape_layer.extent()

            # Main routine
            if self.point_layer is not None:
                if self.form in forms.keys() or self.form in special_forms:
                    self.log.append("Selected form: " + self.form)
                    self.log.append("")

                    if not self.form == "Bubbles / Heatmap":

                        # Fetch form size
                        try:
                            self.log.append("Found width to be: " + str(self.width) + " m")
                            self.log.append("Found height to be: " + str(self.height) + " m")
                            self.log.append("")
                            self.log.append("")

                            try:
                                if self.form in special_forms:
                                    if self.form.startswith("Triangle"):
                                        grid = triangle(project_crs=project_crs, point_crs=point_crs, width=self.width,
                                                        height=self.height, extent=extent,
                                                        feedback=self.feedback)
                                    elif self.form.startswith("Fishernet"):
                                        grid = fishers_net(project_crs=project_crs, point_crs=point_crs,
                                                           width=self.width, height=self.height, extent=extent,
                                                           feedback_process=self.feedback)
                                else:
                                    grid = base_forms(project_crs=project_crs, point_crs=point_crs, width=self.width,
                                                      height=self.height, extent=extent, form_id=forms[self.form],
                                                      feedback=self.feedback)

                                intensities = processing.run("native:countpointsinpolygon", {
                                    'POLYGONS': grid,
                                    'POINTS': self.point_layer,
                                    'WEIGHT': '',
                                    'CLASSFIELD': '',
                                    'FIELD': 'NUMPOINTS',
                                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                                }, feedback=self.feedback)['OUTPUT']

                                self.log.append("Successfully build intensity-grid.")

                                if self.mask:
                                    if self.shape_layer is not None:
                                        if not self.keep_form:
                                            intensities = processing.run("native:clip", {
                                                'INPUT': intensities,
                                                'OVERLAY': self.shape_layer,
                                                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                                            }, feedback=self.feedback)['OUTPUT']
                                        else:
                                            intensities = processing.run("native:extractbylocation", {
                                                'INPUT': intensities,
                                                'PREDICATE': [0],
                                                'INTERSECT': self.shape_layer,
                                                'OUTPUT': 'TEMPORARY_OUTPUT'
                                            }, feedback=self.feedback)['OUTPUT']

                                        self.log.append(
                                            "Successfully cutted to shapefile (Softcut: " + str(self.keep_form) + ").")
                                        self.log.append("")
                                    else:
                                        self.log.insertHtml(
                                            "<p style=\"color:#FF0000\";><b>Error processing shape layer</b></p><br>")
                                        self.log.insertHtml(
                                            "<p style=\"color:#FF0000\";>Please select a valid shape to cut your form layer to.</p><br>")

                                classification_method = QgsClassificationJenks()

                                if self.number_of_classes <= 0:
                                    self.number_of_classes = 10
                                    self.log.insertHtml(
                                        "<p style=\"color:#f2b202\";>Number of classes was smaller than one. Selecting "
                                        "10 as default.</p><br>")

                                ramp_format = QgsRendererRangeLabelFormat()
                                ramp_format.setFormat("%1 - %2")
                                ramp_format.setPrecision(2)
                                ramp_format.setTrimTrailingZeroes(True)

                                renderer = QgsGraduatedSymbolRenderer()
                                renderer.setClassAttribute('NUMPOINTS')
                                renderer.setClassificationMethod(classification_method)
                                renderer.setLabelFormat(ramp_format)
                                renderer.updateClasses(intensities, self.number_of_classes)
                                renderer.updateColorRamp(
                                    default_style.colorRamp(colors_keys[self.color_ramp.currentIndex()]))

                                intensities.setRenderer(renderer)
                                intensities.triggerRepaint()

                                intensities.setName('Intensity')

                                self.result = intensities

                                self.log.append("Successfully styled. Adding layer...")
                                self.log.append("")

                                self.log.insertHtml(
                                    "<span style=\"color:#1bb343\";>---------------------------</span><br>")
                                self.log.insertHtml(
                                    "<span style=\"color:#1bb343\";>| Finished processing. |</span><br>")
                                self.log.insertHtml(
                                    "<span style=\"color:#1bb343\";>---------------------------</span><br>")

                            except QgsProcessingException as qpe:
                                self.log.insertHtml(
                                    "<p style=\"color:#FF0000\";><b>Error fetching form size...</b></p><br>")
                                self.log.insertHtml(
                                    "<p style=\"color:#FF0000\";>The given width and/or height was to large</p><br>")
                                self.log.append(str(qpe))

                        except ValueError:
                            self.log.insertHtml(
                                "<p style=\"color:#FF0000\";><b>Error fetching form size...</b></p><br>")
                            self.log.insertHtml(
                                "<p style=\"color:#FF0000\";>Please provide valid numbers in kilometer.</p><br>")

                    else:
                        # No grid to create, only do heatmap styling so copy the layer to not alter the og one
                        self.point_layer.selectAll()
                        points_copy = processing.run("native:saveselectedfeatures", {
                            'INPUT': self.point_layer,
                            'OUTPUT': 'memory:'
                        }, feedback=self.feedback)['OUTPUT']
                        self.point_layer.removeSelection()

                        renderer = QgsHeatmapRenderer()
                        color_ramp = default_style.colorRamp(colors_keys[self.color_ramp.currentIndex()])
                        color_ramp.setColor1(QColor(43, 131, 186, 0))
                        renderer.setColorRamp(color_ramp)
                        renderer.setRenderQuality(self.render_quality)

                        self.log.append("Successfully styled. Adding layer...")
                        self.log.append("")

                        points_copy.setRenderer(renderer)
                        points_copy.triggerRepaint()
                        points_copy.setName("Agglomerations")

                        self.result = points_copy

                        self.log.insertHtml("<span style=\"color:#1bb343\";>---------------------------</span><br>")
                        self.log.insertHtml("<span style=\"color:#1bb343\";>| Finished processing. |</span><br>")
                        self.log.insertHtml("<span style=\"color:#1bb343\";>---------------------------</span><br>")

                else:
                    self.log.insertHtml("<p style=\"color:#FF0000\";><b>Error selecting a form...</b></p><br>")
                    self.log.insertHtml("<p style=\"color:#FF0000\";>Please select a valid form.</p><br>")

            else:
                self.log.insertHtml("<p style=\"color:#FF0000\";><b>Error fetching point layer...</b></p><br>")
                self.log.insertHtml(
                    "<p style=\"color:#FF0000\";>Please provide valid layer containing only points.</p><br>")


            self.progress.emit(100)
            self.finished.emit(self.result)
        except Exception as e:
            self.log.insertHtml("<p style=\"color=#FF0000\";><b>" + str(e) + "</b></p><br>")
            self.progress.emit(0)
            self.finished.emit(None)

    def stop(self):
        self.stopworker = True
        self.log.insertHtml("<p style=\"color:#FF0000\";><b>Worker killed manually</b></p><br>")
        self.feedback.cancel()


class Bestagon:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Bestagon_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Bestagon')

        self.first_start = None

    # noinspection PyMethodMayBeStatic

    def tr(self, message):
        return QCoreApplication.translate('Bestagon', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True,
                   status_tip=None, whats_this=None, parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        icon_path = ':/plugins/bestagon/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Bestagon'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Bestagon'), action)
            self.iface.removeToolBarIcon(action)

    def startWorker(self, log, context, params):
        self.thread = QThread()
        self.worker = Worker(log=log, context=context, params=params)

        self.worker.moveToThread(self.thread)
        # Connect signals and slots:
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.worker.finished.connect(self.grapple_worker_output)
        self.thread.start()

        self.dlg.button_box.buttons()[0].setEnabled(False)
        self.thread.finished.connect(lambda: self.dlg.button_box.buttons()[0].setEnabled(True))

    def killWorker(self):
        self.worker.stop()

    def reportProgress(self, n):
        self.dlg.progressBar.setValue(n)

    @staticmethod
    def grapple_worker_output(qgis_output):
        if qgis_output is not None:
            QgsProject.instance().addMapLayer(qgis_output)

    def run(self):
        ui_params = {
            "point_layer": None,
            "form": None,
            "width": 100,
            "height": 100,
            "shape_layer": None,
            "mask": True,
            "keep_form": False,
            "color_ramp": None,
            "number_of_classes": 0,
            "render_quality": 0
        }

        if self.first_start:
            self.first_start = False
            self.dlg = bestagonDialog()

            self.dlg.button_box.accepted.disconnect()

            self.main_buttons = self.dlg.button_box.buttons()
            self.main_buttons[0].clicked.connect(lambda: self.trigger(
                log=self.dlg.log_entry, ui_params=ui_params, context=QgsProcessingContext()
            ))

            self.dlg.btn_cancel.clicked.connect(lambda: self.killWorker())

            # disable functionalities
            self.dlg.label_6.setEnabled(False)
            self.dlg.label_7.setEnabled(False)
            self.dlg.label_8.setEnabled(False)

            for color_key in colors_keys:
                self.dlg.comboBox_ramps.addItem(
                    QgsSymbolLayerUtils.colorRampPreviewIcon(default_style.colorRamp(color_key), QSize(16, 16)),
                    color_key)

            # init values
            self.dlg.comboBox_form.addItems(forms.keys())
            self.dlg.comboBox_form.addItems(special_forms)

        # init filters
        self.dlg.mMapLayerComboBox_points.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.dlg.mMapLayerComboBox_shape.setFilters(QgsMapLayerProxyModel.PolygonLayer)

        # disable functionalities
        def form_combobox_changed(value):
            if value == "Bubbles / Heatmap":
                self.dlg.lineEdit_width.setEnabled(False)
                self.dlg.lineEdit_height.setEnabled(False)
                self.dlg.label_numberclasses.setText("Radius (in km)")
                self.dlg.label_6.setEnabled(True)
                self.dlg.label_7.setEnabled(True)
                self.dlg.label_8.setEnabled(True)
            else:
                self.dlg.lineEdit_width.setEnabled(True)
                self.dlg.lineEdit_height.setEnabled(True)
                self.dlg.label_numberclasses.setText("Number of classes")
                self.dlg.label_6.setEnabled(False)
                self.dlg.label_7.setEnabled(False)
                self.dlg.label_8.setEnabled(False)

        self.dlg.comboBox_form.currentTextChanged.connect(form_combobox_changed)

        if self.dlg.comboBox_form.currentText == "Bubbles / Heatmap":
            self.dlg.render_slider.setEnabled(True)
        else:
            self.dlg.render_slider.setEnabled(False)


        self.dlg.show()


    def trigger(self, ui_params, log, context):

        try:
            ui_params["width"] = float(self.dlg.lineEdit_width.text()) * 1000
            ui_params["height"] = float(self.dlg.lineEdit_height.text()) * 1000
        except ValueError:
            ui_params["width"] = 99
            ui_params["height"] = 99

        # Modify params
        ui_params["point_layer"] = self.dlg.mMapLayerComboBox_points.currentLayer()
        ui_params["form"] = self.dlg.comboBox_form.currentText()
        ui_params["shape_layer"] = self.dlg.mMapLayerComboBox_shape.currentLayer()
        ui_params["mask"] = self.dlg.checkBox_cut.isChecked()
        ui_params["keep_form"] = self.dlg.checkBox_soft.isChecked()
        ui_params["color_ramp"] = self.dlg.comboBox_ramps
        ui_params["render_quality"] = self.dlg.render_slider.value()

        self.startWorker(
            log=log, params=ui_params, context=context
        )

