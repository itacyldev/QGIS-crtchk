import json
import logging
import os
import traceback
from dataclasses import dataclass, field

from qgis.core import (
    QgsProject)

"""
Read and writing of plugin settings
Configurations are store in project settings as json objects


"""
PLUGIN_ID = "cartodruid_sync"
CRTSYNC_CONFIGS = "CRTSYNC_CONFIGS"  # list of configurations
CRTSYNC_ENDPOINTS = "CRTSYNC_ENDPOINTS"  # list of available endpoints


def _read_object_from_settings(proj: QgsProject, setting_id, setting_name, listener=None):
    settings_str = None
    if not listener:
        listener = logging
    try:
        settings_str, type_conversion_ok = proj.readEntry(PLUGIN_ID, setting_id)
    except:
        listener.error(
            "Error while trying to parse {} configuration object: [{}].\nThe setting will be removed from project.".format(
                setting_name, settings_str))
        # proj.removeEntry(PLUGIN_ID, setting_id)

    return settings_str


def _write_object_to_settings(proj: QgsProject, setting_id, json_str, listener=None):
    if not listener:
        listener = logging
    proj.writeEntry(PLUGIN_ID, setting_id, json_str)
    listener.info("Project configuration updated.")


def read_endpoints(proj: QgsProject, listener=None):
    json_str = _read_object_from_settings(proj, CRTSYNC_ENDPOINTS, "endpoints", listener)
    if not json_str:
        return None
    return json.loads(json_str)


def write_endpoints(proj: QgsProject, endpoint_list, listener=None):
    json_str = json.dumps(endpoint_list, default=vars)
    _write_object_to_settings(proj, CRTSYNC_ENDPOINTS, json_str, listener)


def read_sync_configs(proj: QgsProject, listener=None):
    json_str = _read_object_from_settings(proj, CRTSYNC_CONFIGS, "sync. configs", listener)
    if not json_str:
        return None

    wks_config = None
    settings_dict = json.loads(json_str)
    try:
        wks_config = WksConfig(**settings_dict)
    except Exception:
        traceback.print_exc()
        listener.exception("Error while trying to read sync configurations")
        # proj.removeEntry(PLUGIN_ID, CRTSYNC_CONFIGS)

    return wks_config


def write_sync_configs(proj: QgsProject, wks_configs, listener=None):
    json_str = json.dumps(wks_configs, default=vars)
    print(proj)
    print(json_str)
    _write_object_to_settings(proj, CRTSYNC_CONFIGS, json_str, listener)
    proj.write()


class PluginConfig:
    endpoints = []
    wksConfigs = []


@dataclass
class WksConfig:
    db_file: str
    wks: str
    username: str
    apikey: str
    endpoint: str
    """
    List of tables used to sync data. This list is used to configure update/delete triggers.
    Each item contains the pair (table_name, update_field)
    """
    table_list: list = field(default_factory=lambda: [])

    def __json__(self):
        return self.__dict__


def read_config(proj: QgsProject, listener):
    conf = PluginConfig()
    conf.endpoints = read_endpoints(proj, listener)
    conf.wksConfigs = read_sync_configs(proj, listener)
    listener.info("Configuration found: {}".format(conf.wksConfigs))
    if conf.wksConfigs is None:
        return None
    else:
        return conf.wksConfigs if conf.wksConfigs else None


def plugin_folder():
    return os.path.dirname(os.path.realpath(__file__))


def resolve_path(path):
    print("project path: {}".format(plugin_folder()))
    return os.path.join(plugin_folder(), path)


if __name__ == '__main__':
    wks = WksConfig("0", "1", "2", "3", "4")
    json_str = json.dumps(wks, default=vars)
    print(json_str)
    settings_object = json.loads(json_str)
    settings_object = WksConfig(**settings_object)
    print(settings_object)
