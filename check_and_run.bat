@echo off
echo Checking Node.js and starting LocalTunnel...
echo.

REM Проверяем Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js не установлен!
    echo.
    echo Установить Node.js? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        call install_nodejs.bat
    ) else (
        echo Установите Node.js вручную с https://nodejs.org/
        pause
        exit /b 1
    )
) else (
    echo Node.js найден ✓
    node --version
    echo.
    echo Запускаем LocalTunnel...
    call start_localtunnel.bat
)

pause 