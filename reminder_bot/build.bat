rmdir /s /q dist
rmdir /s /q build
pyinstaller --noconsole --onefile --add-data "../common;common" --hidden-import sqlite3 main.py
del /f .\dist\telebot.exe
ren .\dist\main.exe telebot.exe
pause
