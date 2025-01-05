rmdir /s /q dist
rmdir /s /q build
pyinstaller --noconsole --onefile main.py
del /f .\dist\telebot.exe
ren .\dist\main.exe telebot.exe
pause
