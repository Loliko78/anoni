@echo off
echo 🚀 Запуск ngrok туннеля для PostgreSQL...
echo.
echo ⚠️  ВАЖНО: Оставьте это окно открытым!
echo    Закрытие окна остановит туннель.
echo.
echo 📋 После запуска скопируйте URL вида:
echo    tcp://0.tcp.ngrok.io:12345
echo.
pause
ngrok tcp 5432