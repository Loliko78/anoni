@echo off
echo =================================
echo Настройка домашней базы данных
echo =================================

echo.
echo 1. Установка PostgreSQL...
winget install PostgreSQL.PostgreSQL

echo.
echo 2. Установка Cloudflare Tunnel...
winget install Cloudflare.cloudflared

echo.
echo 3. Создание базы данных...
timeout /t 5
createdb -U postgres harvest_db

echo.
echo 4. Настройка PostgreSQL для внешних подключений...
echo Редактируем postgresql.conf и pg_hba.conf...

echo.
echo =================================
echo Следующие шаги:
echo =================================
echo 1. Выполните: cloudflared tunnel login
echo 2. Выполните: cloudflared tunnel create harvest-db
echo 3. Создайте config.yml (инструкция ниже)
echo 4. Запустите: cloudflared tunnel run harvest-db
echo.
pause