from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *

import processing


def base_forms(project_crs, point_crs, width, height, extent, form_id, feedback):
    """
    processing.run("native:creategrid",
    {
    'TYPE':4,
    'EXTENT':'795984.835800000,1316329.681200000,5023390.099900000,5374384.907900000 [EPSG:3857]',
    'HSPACING':1,
    'VSPACING':1,
    'HOVERLAY':0,
    'VOVERLAY':0,
    'CRS':QgsCoordinateReferenceSystem('EPSG:3857'),
    'OUTPUT':'TEMPORARY_OUTPUT'}
    )
    """

    return processing.run("native:creategrid", {
        'TYPE': form_id,
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
        'VOVERLAY': 0,
        'CRS': project_crs,
        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
    }, feedback=feedback)['OUTPUT']
