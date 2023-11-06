from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *

import processing


def triangle(project_crs, point_crs, width, height, extent, feedback):
    pre_grid = processing.run("native:creategrid", {
        'TYPE': 0,
        'EXTENT': str.format(
            '{},{},{},{} [{}]',
            extent.xMinimum(),
            extent.xMaximum(),
            extent.yMinimum(),
            extent.yMaximum(),
            point_crs.authid()
        ),
        'HSPACING': width,
        'VSPACING': height,
        'HOVERLAY': 0,
        'CRS': project_crs,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }, feedback=feedback)['OUTPUT']

    return processing.run("qgis:delaunaytriangulation", {
        'INPUT': pre_grid,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }, feedback=feedback)['OUTPUT']


def fishers_net(project_crs, point_crs, width, height, extent, feedback_process):
    pre_grid = processing.run("native:creategrid", {
        'TYPE': 4,
        'EXTENT': str.format(
            '{},{},{},{} [{}]',
            extent.xMinimum(),
            extent.xMaximum(),
            extent.yMinimum(),
            extent.yMaximum(),
            point_crs.authid()
        ),
        'HSPACING': width,
        'VSPACING': height,
        'HOVERLAY': 0,
        'CRS': project_crs,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }, feedback=feedback_process)['OUTPUT']

    pre_grid = processing.run("native:centroids", {
        'INPUT': pre_grid,
        'ALL_PARTS': False,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }, feedback=feedback_process)['OUTPUT']

    return processing.run("qgis:delaunaytriangulation", {
        'INPUT': pre_grid,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }, feedback=feedback_process)['OUTPUT']
