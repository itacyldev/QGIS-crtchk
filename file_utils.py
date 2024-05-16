import os
import tempfile
import zipfile
from datetime import datetime
from qgis.core import QgsMessageLog, Qgis, QgsProject, QgsVectorLayer, QgsApplication

import logging


def compress_file(file):
    """
    Creates a zip file in the OS tempfile that contains the original file
    :param file:
    :return:
    """
    if not os.path.isfile(file):
        raise FileNotFoundError(f"The file {file} doesn't exists.")

    # Crear un archivo temporal para el archivo ZIP
    temp_folder = tempfile.gettempdir()
    time_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    infix = os.path.splitext(os.path.basename(file))[0]
    zipped_filename = os.path.join(temp_folder, f"{time_stamp}_{infix}.zip")
    logging.info(zipped_filename)

    # Create zipo file
    with zipfile.ZipFile(zipped_filename, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file_obj:
        zip_file_obj.write(file, os.path.basename(file))

    return zipped_filename
