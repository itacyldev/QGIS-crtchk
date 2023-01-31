# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CartoDruidSync
                                 A QGIS plugin
 Plugin to synchronize SQLite databases to Cartodruid Synchronization services at ITACyL
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-01-20
        git sha              : $Format:%H$
        copyright            : (C) 2023 by ITACyL
        email                : gustavo.rio@itacyl.es
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os.path
import sys
import traceback

from PyQt5.QtCore import QTimer, QEventLoop
from PyQt5.QtWidgets import QMessageBox
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
# Import the code for the dialog
from qgis.core import QgsMessageLog, Qgis, QgsProject, QgsVectorLayer, QgsApplication

from . import db_manage as dbm
from . import plugin_settings as stt
from .crtsync_client import ApiClientListener
from .dialog_conf_sync import CartoDruidConfSyncDialog
from .plugin_settings import resolve_path
from .sync_task import SyncQTask


#
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S')


class CartoDruidSync:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CartoDruidSync_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&CartoDruid Synchronizer')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.listener = SyncListener(iface)
        # init dlg variables
        self.dlg = None
        self.conf_dlg = None

        # list of layers target of the synchronization
        self.sync_layers = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CartoDruidSync', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.add_action(resolve_path('icon.png'),
                        text=self.tr(u'Configure Sync'),
                        callback=self.run_config,
                        parent=self.iface.mainWindow())
        self.add_action(resolve_path("assets/synchronize.png"),
                        text=self.tr(u'Synchronize'),
                        callback=self.run_sync,
                        parent=self.iface.mainWindow())

        # will be set False in run()
        self.plugin_conf = stt.read_config(QgsProject.instance(), self.listener)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            # self.iface.removePluginMenu(self.tr(u'&CartoDruid Synchronizer'), action)
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)

    def run_config(self):
        """Run method that performs all the real work"""
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.dlg is None:
            # first exec
            self.dlg = CartoDruidConfSyncDialog(listener=self.listener)
        self.dlg.go_config()

        current_project = QgsProject.instance()
        # show the dialog
        wks_config = stt.read_config(current_project, self.listener)
        self.dlg.load_settings(wks_config)
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        if not result:
            return
        wks_config = self.dlg.get_wks_config()
        # create empty db
        if not os.path.exists(wks_config.db_file):
            self.listener.info("Empty database created in {}".format(wks_config.db_file))
            dbm.create_empty_db(wks_config.db_file)

        self.listener.info("{}".format(wks_config))
        stt.write_sync_configs(current_project, wks_config, self.listener)

        QMessageBox.question(None, self.tr("Info"), self.tr("Configuración modificada, recuerde guardar el proyecto "
                                                            "para almacenar los cambios."), QMessageBox.Ok)

    def run_sync(self):
        wks_config = stt.read_config(QgsProject.instance(), self.listener)
        if not wks_config:
            QMessageBox.question(None, self.tr("Info"), self.tr("No hay ninguna configuración de sincronización"),
                                 QMessageBox.Ok)
            return
        self.listener.info("Lanzando tarea a ejecución")

        # SyncWorker.run_task(wks_config, self.listener)
        task = SyncQTask("CartoDruid Sync Task", wks_config, self.listener)
        try:
            QgsApplication.taskManager().addTask(task)
        except:
            QgsMessageLog.logMessage("Error al lanzar la tarea", level=Qgis.Critical)

        wait_for_task(task)


def wait_for_task(task, timeout=60):
    """
    active wait without blocking UI window
    :param task:
    :param timeout:
    :return:
    """
    loop = QEventLoop()
    task.taskCompleted.connect(loop.quit)
    task.taskTerminated.connect(loop.quit)
    QTimer.singleShot(timeout * 1000, loop.quit)
    loop.exec_()


def add_vector_layer(wks_config, listener):
    file_path = wks_config.db_file
    listener.info("Obtaining tables and layers for db {}".format(file_path))
    table_list = dbm.get_table_list(db_file=file_path)
    print(f"table filter: {wks_config.table_filter}")
    if wks_config.table_filter:
        table_list = [tbl for tbl in table_list if tbl in wks_config.table_filter]
    # table_list = dbm.get_geo_layers(file_path)
    listener.info("Geo layers found in [{}]: {}".format(file_path, table_list))
    # add layers to project
    sync_layers = []

    current_layers = QgsProject.instance().mapLayers().values()

    for table_name in table_list:
        # new_layer = QgsVectorLayer("dbname='{}' table='{}' (geom) sql=".format(file_path, table_name), table_name, "spatialite")
        layer_found = next(filter(lambda l: l.name() == table_name, current_layers), None)
        if not layer_found:
            new_layer = QgsVectorLayer('{}|layername={}'.format(file_path, table_name), table_name)
            QgsProject.instance().addMapLayer(new_layer)
            listener.info("Layer {} add to project.".format(table_name))
            sync_layers.append(new_layer)
        else:
            layer_found.reload()
            listener.info("Layer {} reloaded.".format(table_name))


class SyncListener(ApiClientListener):

    def __init__(self, iface):
        self.iface = iface

    def notify(self, message):
        QgsMessageLog.logMessage(message, level=Qgis.Info)

    def info(self, message):
        QgsMessageLog.logMessage(message, level=Qgis.Info)

    def error(self, message):
        QgsMessageLog.logMessage(message, level=Qgis.Critical)
        print(message)

    def exception(self, message):
        QgsMessageLog.logMessage(message, level=Qgis.Critical)
        QgsMessageLog.logMessage(repr(traceback.format_exception(*sys.exc_info())), level=Qgis.Critical)

    def on_success(self, wks_config):
        add_vector_layer(wks_config, self)
        QgsMessageLog.logMessage("Sincronización finalizada con éxito", level=Qgis.Info)
        self.iface.messageBar().pushMessage("CartoDruid Sync", QCoreApplication.translate('CartoDruidSync',
                                                                                          "Sincronización finalizada con éxito"),
                                            level=Qgis.Info)

    def on_error(self):
        QgsMessageLog.logMessage("Se produjo un error durante la sincronización", level=Qgis.Critical)
        self.iface.messageBar().pushMessage("CartoDruid Sync", QCoreApplication.translate('CartoDruidSync',
                                                                                          "Se produjo un error durante la sincronización, consulte la consola."),
                                            level=Qgis.Critical)
