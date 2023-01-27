import sqlite3
import unittest

from db_manage import create_update_trigger, query_for_list, has_update_trigger
from test.db_utils import create_test_db, create_random_table


class CartoDruidSyncDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_create_trigger(self):
        """Test we can click OK."""
        db_file = create_test_db()
        table_name = create_random_table(db_file)
        # create trigger
        try:
            conn = sqlite3.connect(db_file)
            create_update_trigger(conn, table_name)

            lst = query_for_list(conn, f"select count(1) from sqlite_master where type = 'trigger' and tbl_name = '{table_name}'")
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


if __name__ == "__main__":
    suite = unittest.makeSuite(CartoDruidSyncDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)