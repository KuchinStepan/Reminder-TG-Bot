rmdir /s /q dist
rmdir /s /q build
pyinstaller --noconsole --onefile main.py
del /f .\dist\telebot_admin.exe
ren .\dist\main.exe telebot_admin.exe
pause
