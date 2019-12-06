@ECHO OFF
ECHO Starting Program...
SET /P convert="Would you like to convert xls file to csv?(requires MS Excel) y|n: "

IF "%convert%"=="y" (CALL :convert_xls)
IF "%convert%"=="n" (CALL :run_app)

:convert_xls
SET /P xls_file="Enter name of xls file (if spaces exist, use quotes): "
ExcelToCsv.vbs %xls_file%.xls %xls_file%.csv
GOTO :run_app

:run_app
py 60335_data_ack_eval.py
start "" "url.html"
EXIT