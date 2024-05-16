# coding=utf-8
"""Common functionality used by regression tests."""
import os
import string
import sys
import logging
import tempfile
import traceback
import zipfile
from pathlib import Path
import random

# from _gui import QgisInterface
from qgis.gui import QgsMapCanvas, QgisInterface
LOGGER = logging.getLogger('QGIS')
QGIS_APP = None  # Static variable used to hold hand to running QGIS app
CANVAS = None
PARENT = None
IFACE = None


def get_qgis_app():
    """ Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """

    try:
        from qgis.PyQt import QtGui, QtCore
        from PyQt5.QtWidgets import QApplication
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas, QgisInterface
        from PyQt5 import QtWidgets
        # from qgis_interface import QgisInterface
    except ImportError:
        # return None, None, None, None
        print(repr(traceback.format_exception(*sys.exc_info())))
        raise

    global QGIS_APP  # pylint: disable=W0603

    if QGIS_APP is None:
        gui_flag = True  # All test will run qgis in gui mode
        # noinspection PyPep8Naming
        try:
            QGIS_APP = QgsApplication(sys.argv, gui_flag)
        except:
            QGIS_APP = QgsApplication([x.encode("utf-8") for x in sys.argv], gui_flag)
        # Make sure QGIS_PREFIX_PATH is set in your env if needed!
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()
        LOGGER.debug(s)

    global PARENT  # pylint: disable=W0603
    if PARENT is None:
        # noinspection PyPep8Naming
        # PARENT = QtGui.QWidget()
        PARENT = QtWidgets.QWidget()

    global CANVAS  # pylint: disable=W0603
    if CANVAS is None:
        # noinspection PyPep8Naming
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(400, 400))

    global IFACE  # pylint: disable=W0603
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        # noinspection PyPep8Naming
        IFACE = MyQgisInterface(CANVAS)

    return QGIS_APP, CANVAS, IFACE, PARENT


class MyQgisInterface(QgisInterface):
    def __init__(self, parent=None):
        super(QgisInterface, self).__init__()


def get_project_root():
    return Path(__file__).parent.parent


def tmp_filename(folder):
    tf = tempfile.NamedTemporaryFile(delete=False, dir=folder)
    return tf.name


def get_build_folder():
    build_folder = os.path.join(get_project_root(), "build")
    if not os.path.exists(build_folder):
        os.mkdir(build_folder)
    return build_folder


def random_string(size):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(size))
