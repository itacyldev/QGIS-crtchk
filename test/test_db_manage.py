import os.path
import sqlite3
import unittest
import test.utilities as utl

from db_manage import create_update_trigger, query_for_list, has_update_trigger, get_table_list, create_empty_db, \
    get_table_cols, has_update_col
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
            table_list = get_table_list(conn)
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
            create_update_trigger(conn, table_name)

            lst = query_for_list(conn,
                                 f"select count(1) from sqlite_master where type = 'trigger' and tbl_name = '{table_name}'")
            num_triggers = lst[0][0]
            self.assertEqual(1, num_triggers)
        finally:
            if conn:
                conn.close()

    def test_has_trigger(self):
        """Test we can click OK."""
        db_file = create_test_db()
        table_name = create_random_table(db_file)
        # create trigger
        try:
            conn = sqlite3.connect(db_file)
            create_update_trigger(conn, table_name)

            self.assertTrue(has_update_trigger(conn, table_name))
        finally:
            if conn:
                conn.close()

    def test_create_empty_db(self):
        tmp_file = utl.tmp_filename(utl.get_build_folder())

        create_empty_db(tmp_file)

        self.assertTrue(os.path.exists(tmp_file))

    def test_get_table_cols(self):
        db_file = create_test_db()
        table_name = create_random_table(db_file)
        try:
            conn = sqlite3.connect(db_file)
            col_list = get_table_cols(conn, table_name)

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
            self.assertTrue(has_update_col(conn, table_name))
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    suite = unittest.makeSuite(CartoDruidSyncDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
