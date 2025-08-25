# 🔧 Решение проблем с установкой Tor

## Проблема: Таймаут при скачивании Tor

### Причина
Проблемы с сетью, блокировка или медленное соединение к серверам Tor Project.

### Решения

#### 1. Использование Tor Browser (рекомендуется)
Самый простой и надежный способ:

```cmd
# Запустите скрипт установки Tor Browser
install_tor_browser.bat
```

**Преимущества:**
- Не требует скачивания через скрипт
- Автоматически настраивает Tor сеть
- Работает даже при блокировке
- Простая установка

#### 2. Альтернативная установка
```cmd
# Запустите альтернативный скрипт
python manual_tor_setup.py
```

Этот скрипт предлагает:
- Установку через пакетные менеджеры
- Ручную установку
- Проверку существующих установок

#### 3. Ручная установка

**Для Windows:**
1. Скачайте Tor Browser с https://www.torproject.org/download/
2. Установите Tor Browser
3. Запустите и нажмите "Connect"

**Для Linux:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tor

# Fedora/RHEL/CentOS
sudo dnf install tor

# Arch Linux
sudo pacman -S tor
```

**Для macOS:**
```bash
# Через Homebrew
brew install tor

# Или скачайте Tor Browser
```

#### 4. Использование Chocolatey (Windows)
```cmd
# Установите Chocolatey, затем:
choco install tor
```

#### 5. Использование Scoop (Windows)
```cmd
# Установите Scoop, затем:
scoop install tor
```

## Проверка установки

### Проверка Tor в системе:
```cmd
python manual_tor_setup.py
```

### Проверка статуса:
```cmd
python check_tor_status.py
```

## Альтернативные источники

Если официальные серверы недоступны:

### 1. Зеркала Tor Project
- https://archive.torproject.org/
- https://dist.torproject.org/

### 2. Пакетные менеджеры
- **Windows**: Chocolatey, Scoop
- **Linux**: apt, dnf, pacman, yum
- **macOS**: Homebrew, MacPorts

### 3. GitHub релизы
- https://github.com/torproject/tor/releases

## Настройка после установки

### 1. Создание конфигурации:
```cmd
python manual_tor_setup.py
```

### 2. Запуск Tor:
```cmd
# Windows
tor.exe -f torrc

# Linux/macOS
./tor -f torrc
```

### 3. Проверка работы:
```cmd
python check_tor_status.py
```

## Решение конкретных проблем

### Проблема: "Connection refused"
**Решение:**
1. Проверьте, не блокирует ли файрвол порт 9050
2. Убедитесь, что Tor не запущен в другом процессе
3. Попробуйте другой порт в конфигурации

### Проблема: "Permission denied"
**Решение:**
1. Запустите от имени администратора
2. Проверьте права доступа к директориям
3. Убедитесь, что у вас есть права на запись

### Проблема: "Address already in use"
**Решение:**
1. Остановите другие процессы Tor
2. Измените порт в конфигурации
3. Перезагрузите систему

## Использование Tor Browser вместо CLI

Если у вас проблемы с CLI версией Tor:

1. **Установите Tor Browser**
2. **Запустите Tor Browser**
3. **Нажмите "Connect"**
4. **Используйте SOCKS прокси 127.0.0.1:9050**

### Настройка Flask для работы с Tor Browser:
```python
# В app.py добавьте:
import os
os.environ['TOR_SOCKS_PORT'] = '9050'
```

## Проверка работоспособности

### Тест подключения:
```cmd
python test_tor_connection.py
```

### Тест внешних сайтов:
```cmd
# Через Python
import requests
proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
response = requests.get('http://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion', proxies=proxies)
print(response.status_code)
```

## Рекомендации

### Для начинающих:
1. **Используйте Tor Browser** - самый простой способ
2. **Следуйте инструкциям** в `install_tor_browser.bat`
3. **Проверяйте статус** через `check_tor_status.py`

### Для продвинутых:
1. **Установите CLI Tor** через пакетный менеджер
2. **Настройте конфигурацию** вручную
3. **Используйте мосты** при необходимости

### Для разработчиков:
1. **Используйте Docker** с Tor
2. **Настройте CI/CD** с Tor
3. **Тестируйте** через разные сети

---

**Примечание**: Tor Browser является наиболее надежным способом получения доступа к Tor сети и рекомендуется для большинства пользователей. 