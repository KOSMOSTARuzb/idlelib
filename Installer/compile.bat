@ECHO OFF
pyinstaller --onefile --add-data idlelib.zip:. main.py
pause