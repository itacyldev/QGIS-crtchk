Tested on QGIS 3.24

# Configure development environment

In the QGIS reference explains how to configure your IDE to refer to QGIS python packages. In this case I prefer to
use (a .pth file)[# https://docs.python.org/3/library/site.html] to append the QGIS site-package directory to the env
PYTTHONPATH variable. Create a `qgis.pth` file and copy it in `project/venv/lib/<python.version>/site-packages/` with
this content:

```txt
# Adss QGIS instalation folder
/usr/lib/python3/dist-packages/qgis/
```

To get the path from your system, you can start python console in QGIS and type "qgis", the origin path of the package
will be shown.

https://docs.qgis.org/3.22/en/docs/pyqgis_developer_cookbook/plugins/ide_debugging.html

Create proyecto in pycharm

# Deploying the plugin

The "copy method".
Copy the plugin folder to
/home/<your_user>/.local/share/QGIS/QGIS3/profiles/default/python/plugins
# check this for other OS: https://g-sherman.github.io/Qgis-Plugin-Builder/