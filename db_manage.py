import logging
import sqlite3


# with open(script_path, 'r') as sql_file:
def read_script(file_path):
    with open(file_path, 'r') as f:
        return f.read()


table_list_select = """
    SELECT name FROM {schema_table}
    WHERE type='table'
    ORDER BY name
"""


def get_table_list(conn):
    # use sqlite_master
    schema_tables = ["sqlite_master", "sqlite_schema"]
    table_list = None
    for table_name in schema_tables:
        try:
            results = query_for_list(conn, table_list_select.format("sqlite_master"))
            table_list = [name["name"] for name in results]
        except:
            logging.warning(f"Coudn't query table list using table [{table_name}].")
    return table_list


def query_for_one(conn, query):
    cur = conn.cursor()
    try:
        cur.execute(query)
        rows = cur.fetchone()
        result = []
        for row in rows:
            result.append(row)
    except Exception as e:
        logging.exception(e)
        raise e
    finally:
        cur.close()
    return result


def query_for_list(conn, query):
    cur = conn.cursor()
    try:
        cur.execute(query)
        rows = cur.fetchall()
        result = []
        for row in rows:
            result.append(row)
    except Exception as e:
        logging.exception(e)
        raise e
    finally:
        cur.close()
    return result


UPDATE_TRIGGER_NAME = "crtsyn_upt_{}"


def has_update_trigger(conn, table_name):
    trigger_name = UPDATE_TRIGGER_NAME.format(table_name)
    query = f"select * from sqlite_master where type = 'trigger' and tbl_name = '{table_name}' and name = '{trigger_name}' "
    result = query_for_list(conn, query)
    return len(result) > 0


UPDATE_TRIGGER = """
    CREATE TRIGGER {trigger_name} AFTER UPDATE ON {table_name} 
    BEGIN
        update {table_name} SET {update_column} = datetime('now') WHERE ROWID = new.ROWID;
    END;
"""

UPDATE_COL_NAMES = ["f_update", "update_date", "mod_date", "f_actualizacion", "f_actuacion", "f_modificacion"]

def create_update_trigger(conn, table_name):
    # list cols to find the update column
    list_cols = f"SELECT name FROM PRAGMA_TABLE_INFO('{table_name}')"
    found_cols = [col[0].lower() for col in query_for_list(conn, list_cols)]
    col_names = [col for col in found_cols if col in UPDATE_COL_NAMES]
    if not col_names:
        raise Exception(
            f"""Cannot find a possible update column for table {table_name}. No column with names {UPDATE_COL_NAMES}. "
            Cols found: {found_cols}""")

    update_column = col_names[0]
    trigger_sql = UPDATE_TRIGGER.format(table_name=table_name, update_column=update_column,
                                        trigger_name=UPDATE_TRIGGER_NAME.format(table_name))
    conn.executescript(trigger_sql)


def setup_db_triggers(db_file, script):
    # table list
    conn = sqlite3.connect(db_file)

    script_path = None

    try:
        table_list = get_table_list(conn)
        # check if the triggers are already create, if not, create triggers
        for table_name in table_list:
            if not has_update_trigger(conn, table_name):
                create_update_trigger(conn, table_name)

    finally:
        conn.close()
