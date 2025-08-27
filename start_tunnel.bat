@echo off
title PostgreSQL ngrok Tunnel
echo Запуск туннеля для PostgreSQL...
echo.
echo ВАЖНО: Не закрывайте это окно!
echo Туннель должен работать постоянно для доступа к базе данных.
echo.

:start
echo Запуск ngrok туннеля...
ngrok tcp 5432

echo Туннель остановлен. Перезапуск через 5 секунд...
timeout /t 5
goto start