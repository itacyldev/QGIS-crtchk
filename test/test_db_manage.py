import os.path
import sqlite3
import unittest
import test.utilities as utl

import db_manage as dbm
from test.db_utils import create_test_db, create_random_table


class CartoDruidSyncDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_list_tables(self):
        db_file = create_test_db()
        table_name = create_random_table(db_file)
        conn = sqlite3.connect(db_file)
        try:
            table_list = dbm.get_table_list(conn)
            self.assertEquals(1, len(table_list))
            self.assertTrue(table_name in table_list)
        finally:
            if conn:
                conn.close()

    def test_create_trigger(self):
        db_file = create_test_db()
        table_name = create_random_table(db_file)
        # create trigger
        try:
            conn = sqlite3.connect(db_file)
            dbm.create_update_trigger(conn, table_name)

            lst = dbm.query_for_list(conn,
                                 f"select count(1) from sqlite_master where type = 'trigger' and tbl_name = '{table_name}'")
            num_triggers = lst[0][0]
            self.assertEqual(1, num_triggers)
        finally:
            if conn:
                conn.close()

    def test_has_update_trigger(self):
        """Test we can click OK."""
        db_file = create_test_db()
        table_name = create_random_table(db_file)
        # create trigger
        try:
            conn = sqlite3.connect(db_file)
            dbm.create_update_trigger(conn, table_name)

            self.assertTrue(dbm.has_update_trigger(conn, table_name))
        finally:
            if conn:
                conn.close()

    def test_setup_db_triggers(self):
        """Test we can click OK."""
        db_file = create_test_db()
        table_name = create_random_table(db_file)
        # create trigger
        dbm.setup_db_triggers(db_file)

        # comprobar que
        lst_tables = dbm.updatable_tables(db_file)

        self.assertTrue(table_name in lst_tables)

    def test_get_geo_layer(self):
        """Test we can click OK."""
        db_file = create_test_db()
        lst_tables = dbm.get_geo_layers(db_file)

        self.assertEquals(0, len(lst_tables))

    def test_query_for_one(self):
        """Test we can click OK."""
        db_file = create_test_db()
        try:
            conn = sqlite3.connect(db_file)
            table_name = create_random_table(db_file)

            num = dbm.query_for_one(conn, f"select count(1) from {table_name}")
            self.assertEquals(0, num)
        finally:
            if conn:
                conn.close()

def test_create_empty_db(self):
    tmp_file = utl.tmp_filename(utl.get_build_folder())

    dbm.create_empty_db(tmp_file)

    self.assertTrue(os.path.exists(tmp_file))


def test_get_table_cols(self):
    db_file = create_test_db()
    table_name = create_random_table(db_file)
    try:
        conn = sqlite3.connect(db_file)
        col_list = dbm.get_table_cols(conn, table_name)

        self.assertEquals(3, len(col_list))
        self.assertTrue("col1" in col_list)
        self.assertTrue("f_update" in col_list)
    finally:
        if conn:
            conn.close()


def test_has_update_col(self):
    db_file = create_test_db()
    table_name = create_random_table(db_file)

    try:
        conn = sqlite3.connect(db_file)
        self.assertTrue(dbm.has_update_col(conn, table_name))
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    suite = unittest.makeSuite(CartoDruidSyncDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
