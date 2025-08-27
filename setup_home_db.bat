@echo off
echo Установка домашней базы данных...

echo 1. Установка PostgreSQL...
choco install postgresql -y

echo 2. Создание базы данных...
createdb harvest_db

echo 3. Установка Cloudflare Tunnel...
choco install cloudflared -y

echo 4. Настройка завершена!
echo Теперь выполните:
echo cloudflared tunnel login
echo cloudflared tunnel create harvest-db
echo 
echo Затем добавьте в Render переменную:
echo DATABASE_URL=postgresql://postgres:password@your-tunnel-url:5432/harvest_db

pause