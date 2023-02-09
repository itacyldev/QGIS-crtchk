# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'gustavo.rio@itacyl.es'
__date__ = '2023-01-20'
__copyright__ = 'Copyright 2023, ITACyL'

import os
import unittest
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["TEST_RUNNING"] = "1"
from utilities import get_qgis_app

QGIS_APP = get_qgis_app()

from PyQt5.QtWidgets import QDialogButtonBox, QDialog

from dialog_conf_sync import CartoDruidConfSyncDialog


# @unittest.skip
class CartoDruidSyncDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = CartoDruidConfSyncDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_ok(self):
        """Test we can click OK."""
        # fill data
        self.dialog.wksId.setText("asdf")
        self.dialog.userName.setText("asdf")
        self.dialog.userApikey.setText("asdf")
        self.dialog.endpoint.setText("http://mydomain.com")
        self.dialog.fileWidget.setFilePath("/path/to_file")

        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)


    def test_dialog_cancel(self):
        """Test we can click cancel."""
        button = self.dialog.button_box.button(QDialogButtonBox.Cancel)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Rejected)


if __name__ == "__main__":
    suite = unittest.makeSuite(CartoDruidSyncDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
