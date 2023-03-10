# Bestagon QGIS Plugin

![Bestagon](readme/bestagon.png)

## Introduction
The Bestagon plugin allows fast visualization for point intensities 
represented by different forms as rectangles or hexagons. More forms 
are coming soon...

## Installation
Download the [zip file](https://github.com/KonstiDE/Bestagon/archive/refs/heads/master.zip)
of the master branch of the current repository and install it manually via the plugin installation
manager of QGIS. Bestagon requires a minimum QGIS version of ``3.0``.

## Examplary Usage
To work, Bestagon requires a point layer to display any intensity information. Anyhow,
the independence of the source of the file, we demonstrate the usage on a point layer file
by [QuickOSM](https://plugins.qgis.org/plugins/QuickOSM/) from OpenStreetMap. Furthermore,
shapefiles used in the following analysis can be downloaded at 
[GADM](https://gadm.org/download_country.html) country-wise.

### Research Question
In the following, we investigate onto the bakery-density across europe. Since Germany is 
called the land with the most sorts of bread, we would expect the highest density of individual
bakeries here. Bestagon easily gives a visual overview whether this is true through the
following steps:

1. Download the data
We here utilize a point layer of QuickOSM of all backeries in europe and the world GADM administrative 
boundaries world shapefile cut to europe (also described in Section [Examplary Usage](#examplary-usage)).

2. 



