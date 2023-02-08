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

from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QApplication

from dialog_messages import MessagesDialog


# @unittest.skip
class MessagesDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = MessagesDialog(None)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_dialog_copy(self):
        """Test we can click OK."""
        self.dialog.btn_copy.click()

        clipboard_content = QApplication.clipboard().text()

        self.assertIsNotNone(clipboard_content)

    def test_dialog_accept(self):
        """Test we can click OK."""
        button = self.dialog.button_box.button(QDialogButtonBox.Ok)
        button.click()
        result = self.dialog.result()
        self.assertEqual(result, QDialog.Accepted)




if __name__ == "__main__":
    suite = unittest.makeSuite(MessagesDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
