import os
import shutil
import sqlite3
import sys
import tempfile
import threading
from zipfile import ZipFile

from PyQt5.QtCore import QRunnable, QThreadPool
from qgis.core import QgsTask, QgsApplication

from . import db_manage as dbm
from .crtsync_client import CrtDrdSyncClient
from .plugin_settings import WksConfig


def _create_db_triggers(db_file, listener):
    """
    Creates update triggers to register changes in tables
    """
    # find tables with date columns filtering by name
    lst_tables = dbm.updatable_tables(db_file)
    listener.info("Found updatable tables: {}".format(lst_tables))
    conn = sqlite3.connect(db_file)
    try:
        for table_name in lst_tables:
            listener.info("Creating insert and update triggers for table {}".format(table_name))
            dbm.create_update_trigger(conn, table_name)
            dbm.create_insert_trigger(conn, table_name)
    finally:
        if conn:
            conn.close()


def run_sync(wks_conf: WksConfig, listener):
    api = CrtDrdSyncClient(wks_conf.endpoint,
                           {"wks": wks_conf.wks, "user": wks_conf.username, "password": wks_conf.apikey},
                           listener=listener)
    api.set_listener(listener)

    try:
        # downloaded = '/media/gus/data/cartodruid/test.sqlite'
        downloaded = '/media/gus/data/cartodruid/ribera2022.zip' # mocking
        # downloaded = api.exec(wks_conf.db_file)
        listener.info("Downloaded database: {}".format(downloaded))

        # uncompress downloaded file
        uncompressed_db = _extract(downloaded, tempfile.gettempdir())

        # add triggers to register changes
        _create_db_triggers(uncompressed_db, listener)

        # backup original file
        listener.info("Backing up current data base to {}".format(wks_conf.db_file + ".backup"))
        shutil.copy(wks_conf.db_file, wks_conf.db_file + ".backup")

        # copy downloaded file to origin
        listener.info("Replacing layer with downloaded file: {}".format(wks_conf.db_file))
        shutil.copy(uncompressed_db, wks_conf.db_file)
    except Exception as e:
        listener.exception("Error during sync process.")
        raise BaseException("Error during sync process.")


def _extract(file, dest_folder):
    """
    Open donwloaded file and extract the sqlite file to dest_folder
    :param file:
    :param dest_folder:
    :return:
    """
    zref = ZipFile(file, 'r')
    # sqlites in the file
    lst_db_files = list((filter(lambda x: x.filename.endswith(".sqlite"), zref.filelist)))
    if len(lst_db_files) == 0:
        raise BaseException("The downloaded file {} contains no database.".format(file))
    if len(lst_db_files) > 1:
        raise BaseException("The downloaded file {} contains more than one database.".format(file))

    # get files from zip file
    db_filename = lst_db_files[0].filename

    with ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)

    db_filename = os.path.join(dest_folder, db_filename)
    # check exists
    if not os.path.exists(db_filename):
        raise BaseException(
            "Something went wrong during the zip extraction, the expected file {} doesn't exists".format(
                db_filename))
    return db_filename


class SyncQTask(QgsTask):
    def __init__(self, description, wks_config, listener=None):
        super().__init__(description, QgsTask.CanCancel)
        self.wks_config = wks_config
        self.listener = listener

    def run(self) -> bool:
        try:
            run_sync(self.wks_config, self.listener)
            return True
        except:
            return False

    def finished(self, result: bool) -> None:
        if result:
            self.listener.on_success(self.wks_config)
        else:
            self.listener.on_error()

    def cancel(self) -> None:
        self.listener.info("Synchronization task canceled by user.")
        super().cancel()


class SyncWorker(QRunnable):
    def __init__(self, wks_config, listener=None):
        super().__init__()
        self.wks_config = wks_config
        self.listener = listener

    def run(self):
        # Código a ejecutar
        print("Ejecutando tarea en segundo plano")

    @staticmethod
    def run_task(wks_config, listener):
        app = QgsApplication.instance()
        thread_pool = QThreadPool()
        runnable = SyncWorker(wks_config, listener)
        thread_pool.start(runnable)
        sys.exit(app.exec_())


class SyncPythonWorker:
    def __init__(self, wks_config, listener=None):
        super().__init__()
        self.wks_config = wks_config
        self.listener = listener

    def run(self):
        # Código a ejecutar
        try:
            run_sync(self.wks_config, self.listener)
            self.listener.on_success()
        except:
            self.listener.on_error()

    @staticmethod
    def run_task(wks_config, listener):
        def task_fnc():
            worker = SyncPythonWorker(wks_config, listener)
            worker.run()

        thread = threading.Thread(target=task)
        # Iniciar el hilo
        thread.start()

        # Esperar a que la tarea se complete antes de continuar con el código principal
        thread.join()


if __name__ == '__main__':
    task = SyncQTask()
