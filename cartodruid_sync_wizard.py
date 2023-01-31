# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CartoDruidSyncDialog
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
import os
import sqlite3

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QListWidgetItem, QMessageBox
from qgis.PyQt import QtWidgets
from qgis.PyQt import uic
from qgis.core import QgsProject, QgsVectorLayer

from .plugin_settings import resolve_path
from . import db_manage as dbm
from . import plugin_settings as stt

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'cartodruid_sync_dialog_base.ui'))
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'cartodruid_sync_wizard.ui'))


class CartoDruidSyncDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None, listener=None):
        """Constructor."""
        super(CartoDruidSyncDialog, self).__init__(parent)
        self.listener = listener
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.__initGui()

        self.wks_config = None
        self.table_list = None
        self.selection_list = None
        self.plugin_confs = None

    def __initGui(self):
        self.plugin_confs = stt.read_config(QgsProject.instance(), self.listener)
        if self.plugin_confs and self.plugin_confs.wks_configs:
            self.wks_config = self.plugin_confs.wks_configs[0]
            self.__preload_data(self.wks_config)

        # bind actions to ui components
        self.btn_next.clicked.connect(self.__go_credentials)
        self.btn_prev.clicked.connect(self.__go_select_db)

        self.btn_accept.clicked.connect(self.accept)

        # list management
        self.btn_add.clicked.connect(self.__add_selected)
        self.btn_add_all.clicked.connect(self.__add_all)
        self.btn_remove.clicked.connect(self.__remove_selected)

        self.rad_layer.toggled.connect(self.__select_layer)
        self.rad_file.toggled.connect(self.__select_file)

        self.combo_layer_name.currentIndexChanged.connect(self.reload_tables)
        self.fileWidget.fileChanged.connect(self.reload_tables)

        # load layers in combo
        self.vector_layers = [layer for layer in QgsProject().instance().mapLayers().values() if
                              isinstance(layer, QgsVectorLayer)]
        layer_names = ["", ] + [layer.name() for layer in self.vector_layers]
        self.combo_layer_name.addItems(layer_names)

    def __preload_data(self, wks_conf):
        """
        Loads dialog data from settings object
        :param wks_config:
        :return:
        """
        self.dlg.fileWidget.setFilePath(wks_conf.db_file)
        self.dlg.wksId.setText(wks_conf.wks)
        self.dlg.userName.setText(wks_conf.username)
        self.dlg.userApikey.setText(wks_conf.apikey)
        self.dlg.endpoint.setText(wks_conf.endpoint)

    def __cancel(self):
        pass

    def __add_selected(self):
        # get selected tables and check if some of them don't have the trigger and ask to add them
        ok_tables = []
        no_trigger_tables = []
        for item_idx in self.lstw_tableList.selectedIndexes():
            table_name, has_index = self.table_list[item_idx.row()]
            if has_index:
                ok_tables.append(table_name)
            else:
                no_trigger_tables.append(table_name)

        # add ok tables to selected list
        ok_icon = QIcon(resolve_path("assets/check-mark-16.png"))
        for table_name in ok_tables:
            self.lstw_tableList.addItem(QListWidgetItem(ok_icon, table_name))

        msg = "Estas tablas no tienen asociado un trigger de actualización, este trigger es necesario para registrar " \
              "los cambios: \n {} \n¿Deseas crearlos?".format("\n".join(no_trigger_tables))

        result = QMessageBox.question(None, "Ha seleccionado tablas no monitorizadas", msg,
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == QMessageBox.Yes:
            # create trigger and add tables to list
            conn = sqlite3.connect(self.get_db_file())
            try:
                dbm.create_update_trigger()
            finally:
                if conn:
                    conn.close()

    def __add_all(self):
        pass

    def __remove_selected(self):
        pass

    def __go_credentials(self):
        self.stackedWidget.setCurrentIndex(1)

    def __go_select_db(self):
        self.stackedWidget.setCurrentIndex(0)

    def __select_layer(self):
        # disable file widget
        self.fileWidget.setEnabled(False)
        self.combo_layer_name.setEnabled(True)

    def __select_file(self):
        self.fileWidget.setEnabled(True)
        self.combo_layer_name.setEnabled(False)

    def get_db_file(self):
        if self.rad_file.isChecked():
            return self.fileWidget.filePath()
        else:
            idx = self.combo_layer_name.currentIndex()
            # get layer file
            if idx == 0:
                return None
            else:
                uri = self.vector_layers[idx - 1].dataProvider().dataSourceUri()
                # parse URI: dbname='/path/to/mydb.sqlite' table="mytable" (geometry) sql=
                return uri.split(" ")[0].split("=")[1].replace("'", "")

    def get_sync_config(self):
        return self.wks_configs[0]

    def reload_tables(self):
        file_path = self.get_db_file()
        if not file_path:
            self.lstw_tableList.clear()
            self.lstw_selectionList.clear()
            return
        # leer las tablas de la BD
        conn = sqlite3.connect(file_path)
        try:
            table_names = dbm.get_table_list(conn)
            self.table_list = []
            item_list = []
            # check if tablas has an update trigger
            for name in table_names:
                has_trigger = dbm.has_update_trigger(conn, name)
                self.table_list.append((name, has_trigger))
                icon = QIcon(resolve_path("assets/check-mark-16.png")) if has_trigger else QIcon(
                    resolve_path("assets/x-mark-16.png"))
                self.lstw_tableList.addItem(QListWidgetItem(icon, name))
        finally:
            if conn:
                conn.close()
