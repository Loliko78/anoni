@echo off
echo Starting Flask application and LocalTunnel...
echo.

REM Запускаем Flask в фоне
start "Flask App" cmd /k "python app.py"

REM Ждем немного для запуска Flask
timeout /t 3 /nobreak > nul

REM Запускаем LocalTunnel
echo Starting LocalTunnel...
echo You'll get a URL like: https://abc123.loca.lt
echo.
npx localtunnel --port 5000

pause 