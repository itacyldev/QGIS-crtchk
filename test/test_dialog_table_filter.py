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

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from dialog_table_filter import TableFilterScreen
from dialog_conf_sync import CartoDruidConfSyncDialog

from test import db_utils as dbu


# @unittest.skip
class TableFilterDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.main_dialog = CartoDruidConfSyncDialog(None)
        self.dialog = TableFilterScreen(self.main_dialog)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_reload_tables(self):
        """
        Create db test with two tables, prss the reload button and check there are two items in the select
        :return:
        """
        # create db with two tables
        db_file = dbu.create_test_db()
        dbu.create_random_table(db_file)
        dbu.create_random_table(db_file)
        # Arrange: set db_file in widget
        self.main_dialog.fileWidget.setFilePath(db_file)

        # Act
        self.main_dialog.btn_reload.click()

        # Assert: check listWidget has two elements
        self.assertEquals(2, self.main_dialog.lstw_tableList.count())


if __name__ == "__main__":
    suite = unittest.makeSuite(TableFilterDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
