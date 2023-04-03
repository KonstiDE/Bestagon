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


def base_forms(crs, width, height, extent, form_id, feedback_process):
    return processing.run("native:creategrid", {
        'TYPE': form_id,
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
