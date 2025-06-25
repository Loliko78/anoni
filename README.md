# 🌐 Harvestano - Анонимный мессенджер

Harvestano - это анонимный мессенджер с поддержкой групповых чатов, каналов и шифрования. Теперь с полной поддержкой Tor хостинга и Android приложения.

## 🚀 Быстрый старт

### Tor хостинг (рекомендуется)
```bash
# Быстрый запуск с меню
quick_start_tor.bat

# Или полная настройка
setup_complete_tor.bat
```

### Обычный хостинг
```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
python app.py
```

## 📱 Android приложение

### Сборка APK:
```bash
# С Tor поддержкой
build_tor_apk.bat

# Обычная сборка
build_existing_apk.bat
```

### Установка:
1. Соберите APK
2. Установите на Android устройство
3. Для Tor: установите Orbot и включите VPN
4. Запустите приложение

## 🌐 Доступ

### Tor (.onion):
```
http://[ваш-onion-адрес].onion
```

### Обычный доступ:
```
http://localhost:10000
```

## 🔧 Возможности

### Основные функции:
- ✅ Личные чаты с E2EE шифрованием
- ✅ Групповые чаты
- ✅ Каналы с подписками
- ✅ Загрузка файлов
- ✅ Анонимные профили
- ✅ Tor хостинг
- ✅ Android приложение

### Безопасность:
- 🔐 End-to-end шифрование
- 🌐 Tor сеть
- 🛡️ Защита от брутфорса
- 🔒 Анонимные ники
- 📱 Безопасное Android приложение

## 📋 Требования

### Сервер:
- Python 3.7+
- Flask и зависимости
- Tor (для .onion хостинга)

### Android:
- Android 5.0+ (API 21)
- Orbot (для Tor подключения)

## 🛠️ Настройка

### Tor хостинг:
1. `python tor_setup.py` - Установка Tor
2. `python setup_harvestano_onion.py` - Настройка .onion
3. `start_harvestano_tor.bat` - Запуск сервера
4. `build_tor_apk.bat` - Сборка Android APK

### Обычный хостинг:
1. `pip install -r requirements.txt`
2. `python app.py`
3. `build_existing_apk.bat` - Сборка Android APK

## 📖 Документация

- [README_TOR.md](README_TOR.md) - Подробная документация по Tor
- [TOR_SETUP_INSTRUCTIONS.md](TOR_SETUP_INSTRUCTIONS.md) - Инструкции по настройке Tor
- [SECURITY_SETUP.md](SECURITY_SETUP.md) - Настройки безопасности
- [INSTRUCTIONS.md](INSTRUCTIONS.md) - Общие инструкции

## 🔍 Проверка статуса

```bash
# Проверка Tor
python check_tor_status.py

# Тестирование подключения
python test_tor_connection.py
```

## 🚨 Устранение неполадок

### Tor проблемы:
1. Проверьте статус: `python check_tor_status.py`
2. Перезапустите Tor: `taskkill /f /im tor.exe`
3. Проверьте логи: `harvestano_tor.log`

### Android проблемы:
1. Убедитесь, что Orbot запущен
2. Проверьте VPN в Orbot
3. Перезапустите приложение

## 🔄 Обновление

```bash
# Обновление Tor
python tor_setup.py

# Пересборка APK
build_tor_apk.bat
```

## 📞 Поддержка

### Логи:
- Tor: `harvestano_tor.log`
- Flask: Консоль приложения
- Android: Logcat

### Диагностика:
```bash
python check_tor_status.py
python test_tor_connection.py
```

## ⚠️ Важно

- Использование Tor обеспечивает анонимность, но не гарантирует полную безопасность
- Всегда соблюдайте меры предосторожности при работе с конфиденциальными данными
- Регулярно обновляйте Tor и зависимости

---

**🌐 Harvestano** - Анонимный мессенджер с поддержкой Tor сети

**🔗 Ссылки:**
- [Tor Project](https://www.torproject.org/)
- [Orbot](https://guardianproject.info/apps/orbot/)
- [Flask](https://flask.palletsprojects.com/) 