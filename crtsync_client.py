import json
import logging
import os.path
import tempfile
import time

import requests

from .plugin_settings import resolve_path

"""
Crtdrd synchronization client
"""

CA_FILE = resolve_path("assets/cacert.pem")

if not os.path.exists(CA_FILE):
    raise Exception(f"Invalid CA file path: {CA_FILE}")


class ApiClientListener:

    def notify(self, message):
        logging.info(message)


class CrtDrdSyncClient:
    def __init__(self, endpoint, credentials, **kwargs):
        self.endpoint = endpoint
        if self.endpoint[-1] != '/':
            self.endpoint += '/'
        self.credentials = credentials
        self._listener = ApiClientListener()
        self._current_sync_id = None
        self._MAX_WAIT = 60000
        self._SLEEP_TIME = 5  # time between checks
        # location of downloade file, if not provided, the file will be downloaded in the SO temp folder
        self.temp_folder = self.temp_folder = kwargs["temp_folder"] if "temp_folder" in kwargs else None

    def set_listener(self, listener: ApiClientListener):
        self._listener = listener

    def exec(self, file: str):
        # location files to upload
        self._listener.notify("Starting synchronization process, sending file {}".format(file))
        sync_uri = self._create_sync(file)

        # push sync resources
        # self._listener.notify("Pushing files to sync_uri " + sync_uri)
        # self.push_files(sync_uri, files)
        # run synchronization

        # wait for sync to finish
        self._listener.notify("Checking sync status")
        self._check_status(sync_uri)

        # download result files
        self._listener.notify("Synchronization process finished, downloading files")
        local_file = self.download_file(sync_uri)

        self._listener.notify("Update download state")
        self.finish_sync(sync_uri)

        self._listener.notify("Synchronization completed!")
        return local_file

    def _create_sync(self, file):
        if not os.path.exists(file) or not os.path.isfile(file):
            msg = "Invalid db file path. File doesn't exists: {}".format(file)
            self._listener.exception(msg)
            raise BaseException(msg)

        url = self.endpoint + "cnt/rest/syncro/"
        file_params = {"contentFile": open(file, 'rb')}
        self._listener.info("Starting synchronization against url {}".format(url))

        try:
            response = requests.post(url, files=file_params, headers=self.credentials, verify=False)
            location = response.headers.get('location')
        except:
            error_msg = f"Error occurred while trying to connect to resource uri {url}. " \
                        f"Check the endpoint value in wks configuration."
            self._listener.exception(error_msg)
            raise BaseException(error_msg)

        if response.status_code != 200:
            error_msg = f"Error occurred while trying to connect to resource uri {url}. Status:{response.status_code} " \
                        f"content: {response.text}. Check the endpoint value in wks configuration."
            self._listener.exception(error_msg)
            raise BaseException(error_msg)
        return location

    def get_sync_status(self, sync_uri, return_response=False):
        response = requests.get(sync_uri, headers=self.credentials, verify=False)
        return response, response.json() if return_response else response

    def _check_status(self, sync_uri):
        pending = True
        init_time = time.time()
        elapsed = 0
        while pending and elapsed < self._MAX_WAIT:
            time.sleep(self._SLEEP_TIME)
            response, content = self.get_sync_status(sync_uri, return_response=True)
            pending = response.status_code == 200 and content["state"] == "INIT"
            elapsed = time.time() - init_time
            self._listener.notify("Checking synchronization {}".format(sync_uri))

        if pending:
            raise BaseException("Synchronization not finished, max wait exceeded!")
        if response.status_code != 200:
            raise BaseException(
                "Error occurred while trying to connect to resource uri {}: {}".format(sync_uri, response.content()))
        if content["state"] != "FINISHED":
            raise BaseException(
                "The synchronization {} finished in an invalid state:  {}".format(sync_uri, content))

    def download_file(self, sync_uri):
        url = sync_uri.replace("syncro", "syncroFile")
        response = requests.get(url, headers=self.credentials, verify=False)
        if response.status_code != 200:
            raise BaseException(
                "Error occurred while trying to connect to resource uri {}: {}".format(sync_uri, response.content))
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite.zip', dir=self.temp_folder)
        temp.write(response.content)
        temp.close()
        self._listener.notify("Downloaded file {}".format(temp.name))
        return temp.name

    def finish_sync(self, sync_uri):
        headers = dict(self.credentials)
        headers['Content-type'] = 'application/json'
        response = requests.put(sync_uri, data=json.dumps({}), headers=headers, verify=False)
        if response.status_code != 200:
            raise BaseException(
                "Error occurred while trying to connect to resource uri {}: {}".format(sync_uri, response.content))
