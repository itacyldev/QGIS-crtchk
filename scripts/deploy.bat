cp -r ../QGIS-crtchk %QGIS_PROFILE_HOME%/python/plugins/
rm -rf %QGIS_PROFILE_HOME%/python/plugins/cartodruid_sync
mv %QGIS_PROFILE_HOME%/python/plugins/QGIS-crtchk  %QGIS_PROFILE_HOME%/python/plugins/cartodruid_sync
rm -rf %QGIS_PROFILE_HOME%/python/plugins/cartodruid_sync/venv
rm -rf %QGIS_PROFILE_HOME%/python/plugins/cartodruid_sync/build
rm -rf %QGIS_PROFILE_HOME%/python/plugins/cartodruid_sync/.git
rm -rf %QGIS_PROFILE_HOME%/python/plugins/cartodruid_sync/.idea


