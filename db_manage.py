import logging
import random
import sqlite3


def read_script(file_path):
    with open(file_path, 'r') as f:
        return f.read()


# include list of tables excluding virtual tables
table_list_select = "SELECT name FROM {schema_table} WHERE type='table' and not UPPER(SQL) LIKE '%VIRTUAL%' ORDER BY name"


def is_spatialite_table(table_name):
    table_name = table_name.lower()
    if table_name in ['sqlite_master', 'networks', 'elementarygeometries', 'spatialindex', 'spatial_ref_sys',
                      'spatial_ref_sys_aux',
                      'spatialite_history', 'sql_statements_log', 'sqlite_sequence', 'topologies', 'data_licenses']:
        return True
    keywords_found = list(
        filter(lambda x: x in table_name,
               ["location", "coverages", "_raster_", "_fonts", "_vector_", "_styled_", "stored_", "se_fonts",
                "se_group_", "se_external", "geometry_"]))

    return len(keywords_found) > 0


def get_table_list(conn=None, db_file=None, filter_schema_tables=True):
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(db_file)
        close_conn = True

    # use sqlite_master
    schema_tables = ["sqlite_master", "sqlite_schema"]
    table_list = []
    for table_name in schema_tables:
        try:
            query = table_list_select.format(schema_table=table_name)
            results = query_for_list(conn, query)
            table_list = [row[0] for row in results]
            if filter_schema_tables:
                table_list = [table_name.lower() for table_name in table_list if not is_spatialite_table(table_name)]

            return table_list
        except:
            logging.exception()
            logging.warning(f"Couldn't query table list using table [{table_name}].")
        finally:
            if close_conn and conn:
                conn.close()

    raise Exception("No se han podido consultar las tablas de la bd")


def query_for_one(conn, query):
    cur = conn.cursor()
    try:
        cur.execute(query)
        rows = cur.fetchone()
        result = []
        for row in rows:
            return row
    except Exception as e:
        logging.exception(e)
        raise e
    finally:
        cur.close()
    return None


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


UPDATE_TRIGGER_NAME = "crtsyn_{}_updt"

UPDATE_TRIGGER = """
    CREATE TRIGGER {trigger_name} AFTER UPDATE ON {table_name} 
    BEGIN
        update {table_name} SET {update_column} = strftime('%s', 'now') WHERE ROWID = new.ROWID;
    END;
"""

UPDATE_COL_NAMES = ["f_update", "update_date", "mod_date", "f_actualizacion", "f_actuacion", "f_modificacion"]


def has_update_trigger(conn, table_name):
    trigger_name = UPDATE_TRIGGER_NAME.format(table_name)
    query = f"select * from sqlite_master where type = 'trigger' and tbl_name = '{table_name}' and name = '{trigger_name}' "
    result = query_for_list(conn, query)
    return len(result) > 0


def drop_trigger(conn, trigger_name):
    conn.executescript("DROP TRIGGER {}".format(trigger_name))


def get_update_col(conn, table_name):
    """
    Given a  connection and a table name, returns the name of the column detected as the column that records the
    update date.
    :param conn:
    :param table_name:
    :return:
    """
    list_cols = get_table_cols(conn, table_name)
    found_cols = [col for col in list_cols if col in UPDATE_COL_NAMES]
    return None if len(found_cols) == 0 else list_cols[0]


def create_update_trigger(conn, table_name, re_create=True):
    # drop existing trigger
    if re_create and has_update_trigger(conn, table_name):
        drop_trigger(conn, UPDATE_TRIGGER_NAME.format(table_name))

    # list cols to find the update column
    update_col = get_update_col(conn, table_name)
    if not update_col:
        raise Exception(
            f"""Cannot find a possible update column for table {table_name}. No column with names {UPDATE_COL_NAMES}.
            """)
    trigger_sql = UPDATE_TRIGGER.format(table_name=table_name, update_column=update_col,
                                        trigger_name=UPDATE_TRIGGER_NAME.format(table_name))
    conn.executescript(trigger_sql)


INSERT_TRIGGER_NAME = "crtsyn_{}_insrt"

INSERT_TRIGGER = """
    CREATE TRIGGER {trigger_name} AFTER INSERT ON {table_name} 
    BEGIN
        update {table_name} SET {insert_column} = strftime('%s', 'now') WHERE ROWID = new.ROWID;
    END;
"""

INSERT_COL_NAMES = ["f_insert", "insert_date", "ins_date", "f_insercion", "f_creacion"]


def has_insert_trigger(conn, table_name):
    trigger_name = INSERT_TRIGGER_NAME.format(table_name)
    query = f"select * from sqlite_master where type = 'trigger' and tbl_name = '{table_name}' and name = '{trigger_name}' "
    result = query_for_list(conn, query)
    return len(result) > 0


def create_insert_trigger(conn, table_name, re_create=True):
    if re_create and has_insert_trigger(conn, table_name):
        drop_trigger(conn, INSERT_TRIGGER_NAME.format(table_name))

    # list cols to find the update column
    list_cols = f"SELECT name FROM PRAGMA_TABLE_INFO('{table_name}')"
    found_cols = [col[0].lower() for col in query_for_list(conn, list_cols)]
    col_names = [col for col in found_cols if col in INSERT_COL_NAMES]
    if not col_names:
        raise Exception(
            f"""Cannot find a possible insert column for table {table_name}. No column with names {INSERT_COL_NAMES}. "
            Cols found: {found_cols}""")

    insert_column = col_names[0]
    trigger_sql = INSERT_TRIGGER.format(table_name=table_name, insert_column=insert_column,
                                        trigger_name=INSERT_TRIGGER_NAME.format(table_name))
    conn.executescript(trigger_sql)


def setup_db_triggers(db_file):
    # table list
    conn = sqlite3.connect(db_file)

    try:
        table_list = get_table_list(conn)
        # check if the triggers are already create, if not, create triggers
        for table_name in table_list:
            if not has_update_trigger(conn, table_name):
                create_update_trigger(conn, table_name)
            if not has_insert_trigger(conn, table_name):
                create_insert_trigger(conn, table_name)

    finally:
        conn.close()


def has_update_col(conn, table_name):
    """
    Returns true if the referenced table has a column to register the update date.
    :param conn:
    :param table_name:
    :return:
    """
    col_list = get_table_cols(conn, table_name)
    col_list = [col.lower() for col in col_list]
    for col_name in UPDATE_COL_NAMES:
        if col_name in col_list:
            return True
    return False


def get_table_cols(conn, table_name):
    """
    Returns the list of column names from the selected table
    :param conn:
    :param table_name:
    :return:
    """
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info({})".format(table_name))
        return [columna[1].lower() for columna in cursor.fetchall()]
    finally:
        cursor.close()


def updatable_tables(db_file):
    """
    Returns the list of tables that have update registering columns, and for each table, marks if it's a geographic table
    :param db_file:
    :return:
    """

    conn = sqlite3.connect(db_file)
    updatable_tables = []
    try:
        table_list = get_table_list(conn)
        for table_name in table_list:
            is_updatable = has_update_col(conn, table_name)
            if is_updatable:
                updatable_tables.append(table_name)
    finally:
        if conn:
            conn.close()

    return updatable_tables


def get_geo_layers(db_file):
    conn = sqlite3.connect(db_file)
    table_list = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT f_table_name FROM geometry_columns")
        # get layer tables
        result_set = cursor.fetchall()
        # cerrar la conexión a la base de datos
        for row in result_set:
            table_list.append(row[0].lower())
    except:
        # no geo columns
        pass
    finally:
        if conn:
            conn.close()
    return table_list


def create_random_table(conn):
    query = "create table ttt_{} ( id number)".format(random.randint())
    conn.executescript(query)


def create_empty_db(file_path):
    conn = None
    try:
        conn = sqlite3.connect(file_path)

    finally:
        if conn:
            conn.close()

