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
The difference between modern and traditional, hence cultural, ways to life is a challenge in many countries.
Especially young people are often forced and split between the decision of choosing either way. Mostly, during this age,
educational institutions as schools influence their decision.

We note, that Sweden is mostly modern in the south and that traditionality increases the more north we go. We here
utilize Bestagon to quickly get a visual overview wheter this is really the case. For this we execute the following steps:

1. Download data\
As already mentioned, we utilize the GADM shapefile of the country of Sweden from GADM and a point layer of all
schools in Sweden from QuickOSM (see Section [Examplary Usage](#examplary-usage)).
2. Bestagon settings
Call the installed Bestagon plugin and have the following settings logged in:
![Bestagon](readme/usage_step_2.PNG)



