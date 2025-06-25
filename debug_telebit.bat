@echo off
echo Debugging Telebit Tunnel...
echo.

REM Проверяем Node.js
echo Checking Node.js...
node --version
if errorlevel 1 (
    echo ERROR: Node.js not found!
    pause
    exit /b 1
)

REM Проверяем npm
echo.
echo Checking npm...
npm --version
if errorlevel 1 (
    echo ERROR: npm not found!
    pause
    exit /b 1
)

REM Проверяем tunnel-packer
echo.
echo Checking tunnel-packer...
npx tunnel-packer --version
if errorlevel 1 (
    echo ERROR: tunnel-packer not found!
    echo Installing tunnel-packer...
    npm install -g tunnel-packer
    if errorlevel 1 (
        echo ERROR: Failed to install tunnel-packer!
        pause
        exit /b 1
    )
)

REM Запускаем Flask в фоне
echo.
echo Starting Flask...
start "Flask App" cmd /k "python app.py"

REM Ждем немного для запуска Flask
echo Waiting for Flask to start...
timeout /t 5 /nobreak > nul

REM Проверяем, что Flask запустился
echo Checking if Flask is running...
curl -s http://localhost:5000 >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flask is not running on port 5000!
    echo Check if there are any errors in the Flask window.
    pause
    exit /b 1
)

REM Запускаем Telebit с подробным выводом
echo.
echo Starting Telebit tunnel...
echo.
npx tunnel-packer http 5000

echo.
echo If you see an error above, please copy it and share.
pause 