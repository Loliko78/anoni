@echo off
echo Настройка PostgreSQL для внешних подключений...

echo 1. Создание базы данных...
createdb -U postgres harvest_db

echo 2. Создание пользователя...
psql -U postgres -c "CREATE USER harvest WITH PASSWORD 'harvest123';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE harvest_db TO harvest;"

echo 3. Настройка postgresql.conf...
echo listen_addresses = '*' >> "C:\Program Files\PostgreSQL\15\data\postgresql.conf"

echo 4. Настройка pg_hba.conf...
echo host all all 0.0.0.0/0 md5 >> "C:\Program Files\PostgreSQL\15\data\pg_hba.conf"

echo 5. Перезапуск PostgreSQL...
net stop postgresql-x64-15
net start postgresql-x64-15

echo Настройка завершена!
pause