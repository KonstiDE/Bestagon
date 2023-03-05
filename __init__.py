# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bestagon
                                 A QGIS plugin
 Form (mostly Hexagon) generator for point intensities
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-03-05
        copyright            : (C) 2023 by Konstantin Müller
        email                : konstantinfinn.mueller@gmx.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load bestagon class from file bestagon.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .bestagon import bestagon
    return bestagon(iface)
