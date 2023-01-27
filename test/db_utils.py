import sqlite3

import test.utilities as utl


def create_test_db():
    tmp_file = utl.tmp_filename(utl.get_build_folder())
    conn = None
    try:
        conn = sqlite3.connect(tmp_file)
    finally:
        if conn:
            conn.close()
    return tmp_file


def create_random_table(db_file):
    table_name = utl.random_string(10)
    query = f"""
        CREATE TABLE {table_name} (
            col1 integer PRIMARY KEY,
            col2 text,
            f_update integer
        )
    """
    try:
        conn = sqlite3.connect(db_file)
        conn.executescript(query)
        return table_name
    finally:
        if conn:
            conn.close()


