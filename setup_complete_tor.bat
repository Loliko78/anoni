@echo off
chcp 65001 >nul
echo ========================================
echo    Полная настройка Harvestano Tor
echo ========================================
echo.

echo Шаг 1: Установка зависимостей...
pip install -r requirements.txt

echo.
echo Шаг 2: Настройка Tor...
echo Выберите способ установки Tor:
echo 1. Автоматическая установка (может не работать из-за сети)
echo 2. Альтернативная установка (рекомендуется)
echo 3. Пропустить (если Tor уже установлен)
echo.
set /p tor_choice="Введите номер (1-3): "

if "%tor_choice%"=="1" (
    echo Запуск автоматической установки Tor...
    python tor_setup.py
) else if "%tor_choice%"=="2" (
    echo Запуск альтернативной установки Tor...
    python manual_tor_setup.py
) else if "%tor_choice%"=="3" (
    echo Пропускаем установку Tor...
) else (
    echo Неверный выбор, используем альтернативную установку...
    python manual_tor_setup.py
)

echo.
echo Шаг 3: Настройка harvestano.onion...
python setup_harvestano_onion.py

echo.
echo Шаг 4: Проверка статуса...
python check_tor_status.py

echo.
echo Шаг 5: Сборка Android APK...
call build_tor_apk.bat

echo.
echo ========================================
echo    Настройка завершена!
echo ========================================
echo.
echo Следующие шаги:
echo 1. Запустите сервер: start_harvestano_tor.bat
echo 2. Установите APK на Android устройство
echo 3. Установите Orbot на Android
echo 4. Запустите приложение
echo.
echo Для проверки статуса используйте:
echo python check_tor_status.py
echo.
echo Если Tor не установлен, используйте:
echo python manual_tor_setup.py
echo.
pause 