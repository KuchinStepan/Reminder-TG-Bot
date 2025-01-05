rmdir /s /q dist
rmdir /s /q build
pyinstaller --noconsole --onefile telebot_autorun.py
pause
