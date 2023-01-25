QGIS Plugin to synchronize SQLite databases to Cartodruid Synchronization services
============================

This project contains a QGIS plugin to sincronize the SQlite databases of your project using CartoDruid Synchronization
services.

CartoDruid is a free GIS Android tool that allows field technicians to capture information quickly without needing GIS
skills. The tool includes the most common functions of a GIS editor and manages both vector and raster information, but
focuses on making the data collection and integration of the tool as easy as possible in the organization's workflows.

Cartodruid handles vector data natively in SQLite with the Spatialite expansion, allowing cartography up to 2GB to be
handled with minimal latency. For raster data, CartoDruid supports mbtiles and rasterlite files and also supports the
display of virtual layers based on images with EXIF metadata. These open formats give CartoDruid one of its greatest
strengths, offline work since it allows technicians to carry all the information necessary for their work on their
device and carry out tasks without the need for coverage.

To see a full list of features visit http://www.cartodruid.es.

## Configuring dev environment

In the QGIS reference explains how to configure your IDE to refer to QGIS python packages. In this case I prefer to
use (a .pth file)[# https://docs.python.org/3/library/site.html] to append the QGIS site-package directory to the env
PYTTHONPATH variable. Create a qgis.pth file and copy it into `project/venv/lib/<python.version>/site-packages/` if
you're working on linux or  `project/venv/Lib/site-packages/` if you're in windows, with this content:

``` shell
# Adss QGIS instalation folder
/usr/lib/python3/dist-packages/qgis/

#Or in windows something like this:
C:/Desarrollo/tools/QGIS 3.6/apps/qgis-ltr/python/qgis/
```

You can find the qqis dist packages by typing this in the QGIS python console:
``` python
import qgis; print(qgis)
```

# Adss QGIS instalation folder

/usr/lib/python3/dist-packages/qgis/ To get the path from your system, you can start python console in QGIS and type "
qgis", the origin path of the package will be shown.

https://docs.qgis.org/3.22/en/docs/pyqgis_developer_cookbook/plugins/ide_debugging.html

## Publish plugin

Use the command line script `plugin_upload.py`, the script has been modified to get the credentials from the
variable `QGIS_PLUGIN_CREDENTIALS` with the format `QGIS_PLUGIN_CREDENTIALS=<username>_<password>`.

```bash
py .\plugin_upload.py cartodruid_sync.zip

```
