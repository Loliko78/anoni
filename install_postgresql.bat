@echo off
echo Установка PostgreSQL...

echo 1. Скачивание PostgreSQL...
winget install PostgreSQL.PostgreSQL

echo 2. Ожидание завершения установки...
timeout /t 10

echo 3. Добавление в PATH...
set PATH=%PATH%;C:\Program Files\PostgreSQL\15\bin

echo Установка завершена!
echo Теперь выполните следующие команды:
echo.
echo createdb -U postgres harvest_db
echo psql -U postgres -d harvest_db
echo.
pause