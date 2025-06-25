@echo off
chcp 65001 >nul
title Harvestano Tor Hosting - Quick Start
color 0A

echo.
echo ========================================
echo    Harvestano Tor Hosting
echo    Быстрый запуск
echo ========================================
echo.

echo Выберите действие:
echo.
echo 1. Полная настройка (впервые)
echo 2. Запуск сервера
echo 3. Проверка статуса
echo 4. Тестирование подключения
echo 5. Сборка Android APK
echo 6. Выход
echo.

set /p choice="Введите номер (1-6): "

if "%choice%"=="1" goto full_setup
if "%choice%"=="2" goto start_server
if "%choice%"=="3" goto check_status
if "%choice%"=="4" goto test_connection
if "%choice%"=="5" goto build_apk
if "%choice%"=="6" goto exit
goto invalid

:full_setup
echo.
echo [1] Запуск полной настройки...
call setup_complete_tor.bat
goto end

:start_server
echo.
echo [2] Запуск Tor сервера...
if exist "start_harvestano_tor.bat" (
    call start_harvestano_tor.bat
) else (
    echo [ОШИБКА] Скрипт запуска не найден
    echo Запустите полную настройку сначала
    pause
)
goto end

:check_status
echo.
echo [3] Проверка статуса...
python check_tor_status.py
pause
goto end

:test_connection
echo.
echo [4] Тестирование подключения...
python test_tor_connection.py
pause
goto end

:build_apk
echo.
echo [5] Сборка Android APK...
call build_tor_apk.bat
goto end

:invalid
echo.
echo [ОШИБКА] Неверный выбор. Попробуйте снова.
pause
goto start

:exit
echo.
echo [6] До свидания!
exit /b 0

:end
echo.
echo Нажмите любую клавишу для возврата в меню...
pause >nul
goto start

:start
cls
goto :eof 