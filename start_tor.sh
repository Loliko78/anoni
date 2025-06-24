#!/bin/bash

# Запуск Flask-приложения через Tor Hidden Service

echo "🔥 Запуск Harvest через Tor Hidden Service..."

# Проверяем, установлен ли Tor
if ! command -v tor &> /dev/null; then
    echo "❌ Tor не установлен. Установите Tor сначала."
    exit 1
fi

# Создаем директорию для hidden service
sudo mkdir -p /var/lib/tor/harvestano/
sudo chown debian-tor:debian-tor /var/lib/tor/harvestano/
sudo chmod 700 /var/lib/tor/harvestano/

# Копируем конфигурацию Tor
sudo cp torrc /etc/tor/torrc.harvestano

# Запускаем Tor с нашей конфигурацией
echo "🚀 Запуск Tor..."
sudo tor -f /etc/tor/torrc.harvestano &

# Ждем немного для инициализации
sleep 5

# Получаем .onion адрес
if [ -f /var/lib/tor/harvestano/hostname ]; then
    ONION_ADDRESS=$(sudo cat /var/lib/tor/harvestano/hostname)
    echo "🌐 Ваш .onion адрес: http://$ONION_ADDRESS"
    echo "🔒 Сайт доступен только через Tor Browser!"
else
    echo "⚠️  .onion адрес еще не сгенерирован. Подождите немного..."
fi

# Запускаем Flask-приложение
echo "🚀 Запуск Flask-приложения..."
python app.py 