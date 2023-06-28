set PROFILE_HOME=C:/Users/ita-riobrigu/AppData/Roaming/QGIS/QGIS3/profiles/default

cp -r ../QGIS-crtchk %PROFILE_HOME%/python/plugins/
rm -rf %PROFILE_HOME%/python/plugins/cartodruid_sync
mv %PROFILE_HOME%/python/plugins/QGIS-crtchk  %PROFILE_HOME%/python/plugins/cartodruid_sync
rm -rf %PROFILE_HOME%/python/plugins/cartodruid_sync/venv
rm -rf %PROFILE_HOME%/python/plugins/cartodruid_sync/build
rm -rf %PROFILE_HOME%/python/plugins/cartodruid_sync/.git
rm -rf %PROFILE_HOME%/python/plugins/cartodruid_sync/.idea


