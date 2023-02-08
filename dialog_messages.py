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

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QStyle, QMessageBox
from PyQt5.QtWidgets import QApplication
from qgis.PyQt import uic

if os.environ.get("TEST_RUNNING", 0):
    pass
else:
    pass

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'dialog_messages.ui'))

ICON_NAMES = {
    "info": "SP_MessageBoxInformation",
    "warning": "SP_MessageBoxWarning",
    "error": "SP_MessageBoxCritical",
}


class MessagesDialog(QtWidgets.QDialog, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super(MessagesDialog, self).__init__(parent)
        self.setupUi(self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.btn_copy.clicked.connect(self.__copy_msg)
        self.setModal(True)
        self.lstw_messages.setAutoScroll(True)

    def __copy_msg(self):
        msgs = []
        for i in range(self.lstw_messages.count()):
            msgs.append(self.lstw_messages.item(i).text())
        text = "\n".join(msgs)
        QApplication.clipboard().setText(text)
        QMessageBox.question(None, "Info", "Mensajes copiados al portapapeles", QMessageBox.Ok)

    def notify_msg(self, msg_type, msg):
        # add new message to list
        item = QtWidgets.QListWidgetItem(self.lstw_messages)
        msg_type = msg_type.lower()
        if msg_type not in ICON_NAMES:
            raise BaseException(f"Invalid message type: {msg_type}")
        pixmapi = getattr(QStyle, ICON_NAMES[msg_type])
        item.setIcon(self.style().standardIcon(pixmapi))
        item.setSizeHint(QtCore.QSize(0, 30))
        item.setText(msg)
        self.lstw_messages.addItem(item)
        self.lstw_messages.scrollTo(self.lstw_messages.indexFromItem(item))
