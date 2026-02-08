@echo off
setlocal
set SCRIPT_DIR=%~dp0
python "%SCRIPT_DIR%fetch_wikidata_toki_pona.py"
endlocal
