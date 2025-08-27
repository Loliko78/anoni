@echo off
echo Установка и настройка ngrok...

echo 1. Установка ngrok...
winget install ngrok.ngrok

echo 2. Регистрация на ngrok.com...
echo Откройте https://ngrok.com/signup
echo Скопируйте ваш authtoken
echo.

set /p TOKEN="Введите ваш ngrok authtoken: "

echo 3. Авторизация ngrok...
ngrok authtoken %TOKEN%

echo 4. Создание конфигурации...
mkdir %USERPROFILE%\.ngrok2
echo version: "2" > %USERPROFILE%\.ngrok2\ngrok.yml
echo authtoken: %TOKEN% >> %USERPROFILE%\.ngrok2\ngrok.yml
echo tunnels: >> %USERPROFILE%\.ngrok2\ngrok.yml
echo   postgres: >> %USERPROFILE%\.ngrok2\ngrok.yml
echo     addr: 5432 >> %USERPROFILE%\.ngrok2\ngrok.yml
echo     proto: tcp >> %USERPROFILE%\.ngrok2\ngrok.yml

echo Настройка завершена!
echo Теперь запустите: ngrok tcp 5432
pause