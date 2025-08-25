# 🌐 Harvestano Tor Hosting

Полная настройка хостинга Harvestano через Tor с доменом `.onion` и Android приложением с поддержкой Tor.

## 🚀 Быстрый старт

### 1. Автоматическая настройка (рекомендуется)
```bash
# Запустите полный скрипт настройки
setup_complete_tor.bat
```

### 2. Ручная настройка
```bash
# Шаг 1: Установка зависимостей
pip install -r requirements.txt

# Шаг 2: Настройка Tor
python tor_setup.py

# Шаг 3: Настройка harvestano.onion
python setup_harvestano_onion.py

# Шаг 4: Проверка статуса
python check_tor_status.py

# Шаг 5: Сборка Android APK
build_tor_apk.bat
```

## 📱 Android приложение

### Особенности:
- ✅ Автоматическая интеграция с Orbot
- ✅ Поддержка .onion доменов
- ✅ Обработка ошибок подключения
- ✅ Диалоги с инструкциями
- ✅ WebView с поддержкой JavaScript

### Установка:
1. Соберите APK: `build_tor_apk.bat`
2. Установите APK на Android устройство
3. Установите Orbot из Play Store
4. Запустите Orbot и включите VPN
5. Запустите приложение

## 🔧 Конфигурация

### Tor конфигурация:
- **Файл**: `harvestano_torrc`
- **Порт**: 9050 (SOCKS)
- **Hidden Service**: Порт 80 → 127.0.0.1:10000
- **Версия**: Hidden Service v3

### Android конфигурация:
- **Минимальная версия**: API 21 (Android 5.0)
- **Целевая версия**: API 33 (Android 13)
- **Разрешения**: Интернет, сеть, VPN
- **Безопасность**: Поддержка HTTP для .onion

## 🌐 Доступ к сайту

После настройки ваш сайт будет доступен по адресу:
```
http://[ваш-onion-адрес].onion
```

Адрес сохраняется в файлах:
- `harvestano_onion_address.txt`
- `harvestano_onion_service/hostname`

## 🔒 Безопасность

### Рекомендации:
1. **Регулярно обновляйте Tor**
2. **Используйте файрвол**
3. **Мониторьте логи**
4. **Не используйте личные данные**

### Ограничения:
- .onion адреса генерируются случайно
- Скорость соединения медленнее
- Требуется Tor Browser или Orbot

## 🛠️ Управление

### Запуск сервера:
```bash
# Автоматический запуск
start_harvestano_tor.bat

# Ручной запуск
tor.exe -f harvestano_torrc
python run_with_tor.py
```

### Проверка статуса:
```bash
python check_tor_status.py
```

### Остановка:
```bash
# Windows
taskkill /f /im tor.exe

# Linux/Mac
pkill tor
```

## 📋 Файлы проекта

### Скрипты настройки:
- `tor_setup.py` - Установка и настройка Tor
- `setup_harvestano_onion.py` - Настройка .onion домена
- `run_with_tor.py` - Запуск Flask с Tor
- `check_tor_status.py` - Проверка статуса
- `setup_complete_tor.bat` - Полная автоматическая настройка

### Android:
- `HarvestanoApp/` - Исходный код Android приложения
- `build_tor_apk.bat` - Сборка APK
- `MainActivity.java` - Основная активность с Tor поддержкой

### Конфигурация:
- `harvestano_torrc` - Конфигурация Tor
- `torrc` - Базовая конфигурация Tor
- `network_security_config.xml` - Настройки безопасности Android

## 🚨 Устранение неполадок

### Tor не запускается:
1. Проверьте порт 9050
2. Запустите от имени администратора
3. Проверьте логи: `harvestano_tor.log`

### Android не подключается:
1. Убедитесь, что Orbot запущен
2. Проверьте VPN в Orbot
3. Перезапустите приложение

### Медленное соединение:
1. Это нормально для Tor
2. Попробуйте переподключиться
3. Используйте мосты если доступ заблокирован

## 📞 Поддержка

### Логи:
- Tor: `harvestano_tor.log`
- Flask: Консоль приложения
- Android: Logcat

### Проверка:
```bash
# Полная диагностика
python check_tor_status.py

# Проверка процесса
tasklist | findstr tor.exe
```

## 🔄 Обновление

### Tor:
```bash
# Остановите Tor
taskkill /f /im tor.exe

# Переустановите
python tor_setup.py
```

### Приложение:
```bash
# Пересоберите APK
build_tor_apk.bat
```

---

## 📖 Дополнительная документация

- [TOR_SETUP_INSTRUCTIONS.md](TOR_SETUP_INSTRUCTIONS.md) - Подробные инструкции
- [README.md](README.md) - Основная документация проекта
- [SECURITY_SETUP.md](SECURITY_SETUP.md) - Настройки безопасности

## ⚠️ Важно

Использование Tor обеспечивает анонимность, но не гарантирует полную безопасность. Всегда соблюдайте меры предосторожности при работе с конфиденциальными данными.

---

**🌐 Harvestano Tor Hosting** - Анонимный мессенджер через Tor сеть 