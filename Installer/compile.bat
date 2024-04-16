@ECHO OFF
pyinstaller --onefile --add-data idlelib.zip:. main.py
move .\dist\main.exe main.exe
rmdir dist /S /Q
pause