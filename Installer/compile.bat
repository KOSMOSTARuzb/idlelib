@ECHO OFF
echo Compressing...
powershell -command "Compress-Archive -Path .\..\*.py, .\..\*.txt, .\..\*.bat, .\..\*.html, .\..\*.def, .\..\*.pyw, .\..\Icons, .\..\idle_test, .\..\pymsgbox, .\..\pynput -CompressionLevel Fastest -DestinationPath .\idlelib.zip -Force" 
echo Compressed
echo.
echo Compiling...
pyinstaller --onefile --add-data idlelib.zip:. main.py
move .\dist\main.exe setup.exe
rmdir dist /S /Q
echo DONE
pause