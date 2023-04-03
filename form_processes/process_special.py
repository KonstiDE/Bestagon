from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *

from .constants import (
    ex_w_l,
    ex_w_r,
    ex_h_d,
    ex_h_u
)

import processing


def triangle(crs, width, height, extent, feedback_process):
    pre_grid = processing.run("native:creategrid", {
        'TYPE': 0,
        'EXTENT': str.format(
            '{},{},{},{} [{}]',
            extent.xMinimum() - (extent.xMinimum() * ex_w_l),
            extent.xMaximum() + (extent.xMaximum() * ex_w_r),
            extent.yMinimum() - (extent.yMinimum() * ex_h_d),
            extent.yMaximum() + (extent.yMaximum() * ex_h_u),
            crs.authid()
        ),
        'HSPACING': width,
        'VSPACING': height,
        'HOVERLAY': 0,
        'CRS': crs.authid(),
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }, feedback=feedback_process)['OUTPUT']

    return processing.run("qgis:delaunaytriangulation", {
        'INPUT': pre_grid,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }, feedback=feedback_process)['OUTPUT']


def fishers_net(crs, width, height, extent, feedback_process):
    pre_grid = processing.run("native:creategrid", {
        'TYPE': 4,
        'EXTENT': str.format(
            '{},{},{},{} [{}]',
            extent.xMinimum() - (extent.xMinimum() * ex_w_l),
            extent.xMaximum() + (extent.xMaximum() * ex_w_r),
            extent.yMinimum() - (extent.yMinimum() * ex_h_d),
            extent.yMaximum() + (extent.yMaximum() * ex_h_u),
            crs.authid()
        ),
        'HSPACING': width,
        'VSPACING': height,
        'HOVERLAY': 0,
        'CRS': crs.authid(),
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
