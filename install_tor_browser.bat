@echo off
chcp 65001 >nul
echo ========================================
echo    Установка Tor Browser
echo ========================================
echo.

echo Tor Browser - это самый простой способ получить Tor
echo.

echo Выберите действие:
echo 1. Открыть страницу скачивания Tor Browser
echo 2. Показать инструкции по установке
echo 3. Проверить, установлен ли Tor
echo 4. Выход
echo.

set /p choice="Введите номер (1-4): "

if "%choice%"=="1" (
    echo Открываем страницу скачивания Tor Browser...
    start https://www.torproject.org/download/
    echo.
    echo После скачивания и установки Tor Browser:
    echo 1. Запустите Tor Browser
    echo 2. Нажмите "Connect" для подключения к сети Tor
    echo 3. Запустите: python manual_tor_setup.py
) else if "%choice%"=="2" (
    echo.
    echo Инструкции по установке Tor Browser:
    echo.
    echo 1. Перейдите на https://www.torproject.org/download/
    echo 2. Скачайте версию для вашей системы
    echo 3. Установите Tor Browser
    echo 4. Запустите Tor Browser и нажмите "Connect"
    echo 5. После подключения к сети Tor, запустите:
    echo    python manual_tor_setup.py
    echo.
    echo Tor Browser автоматически предоставляет доступ к Tor сети
    echo и может использоваться для настройки .onion сервисов
) else if "%choice%"=="3" (
    echo Проверяем установленный Tor...
    python manual_tor_setup.py
) else if "%choice%"=="4" (
    echo Выход...
    exit /b 0
) else (
    echo Неверный выбор
)

echo.
pause 