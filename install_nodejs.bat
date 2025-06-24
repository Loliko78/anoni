@echo off
echo Installing Node.js for LocalTunnel...
echo.

REM Проверяем, установлен ли Node.js
node --version >nul 2>&1
if not errorlevel 1 (
    echo Node.js уже установлен ✓
    node --version
    echo.
    echo Теперь запустите: start_localtunnel.bat
    pause
    exit /b 0
)

REM Скачиваем Node.js
echo Downloading Node.js...
powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v18.17.0/node-v18.17.0-x64.msi' -OutFile 'nodejs.msi'"

REM Устанавливаем Node.js
echo Installing Node.js...
msiexec /i nodejs.msi /quiet /norestart

REM Ждем установки
timeout /t 15 /nobreak > nul

REM Удаляем установщик
del nodejs.msi

echo.
echo Node.js установлен! Перезагрузите компьютер и запустите start_localtunnel.bat
echo.

pause 