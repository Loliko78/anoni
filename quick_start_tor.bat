@echo off
chcp 65001 >nul
title Harvestano Tor Setup

:menu
cls
echo ========================================
echo    Harvestano Tor Setup Menu
echo ========================================
echo.
echo Выберите действие:
echo.
echo [1] Полная настройка Tor (рекомендуется)
echo [2] Быстрый старт с Tor
echo [3] Установка Tor Browser
echo [4] Альтернативная установка Tor
echo [5] Проверка статуса Tor
echo [6] Исправление проблем с Tor
echo [7] Сборка Android APK
echo [8] Запуск сервера
echo [9] Тест подключения
echo [10] Инструкции по решению проблем
echo [0] Выход
echo.
echo ========================================

set /p choice="Введите номер (0-10): "

if "%choice%"=="1" (
    echo.
    echo Запуск полной настройки...
    call setup_complete_tor.bat
    goto menu
) else if "%choice%"=="2" (
    echo.
    echo Запуск быстрого старта...
    call quick_start_tor_simple.bat
    goto menu
) else if "%choice%"=="3" (
    echo.
    echo Установка Tor Browser...
    call install_tor_browser.bat
    goto menu
) else if "%choice%"=="4" (
    echo.
    echo Альтернативная установка Tor...
    python manual_tor_setup.py
    echo.
    pause
    goto menu
) else if "%choice%"=="5" (
    echo.
    echo Проверка статуса Tor...
    python check_tor_status.py
    echo.
    pause
    goto menu
) else if "%choice%"=="6" (
    echo.
    echo Исправление проблем с Tor...
    python fix_tor_issues.py
    echo.
    pause
    goto menu
) else if "%choice%"=="7" (
    echo.
    echo Сборка Android APK...
    call build_tor_apk.bat
    goto menu
) else if "%choice%"=="8" (
    echo.
    echo Запуск сервера...
    call start_tor_simple.bat
    goto menu
) else if "%choice%"=="9" (
    echo.
    echo Тест подключения...
    python test_tor_connection.py
    echo.
    pause
    goto menu
) else if "%choice%"=="10" (
    echo.
    echo Открытие инструкций по решению проблем...
    start TOR_INSTALLATION_TROUBLESHOOTING.md
    echo.
    echo Также доступны:
    echo - ENCODING_FIX.md (исправление кодировки)
    echo - README_TOR.md (основные инструкции)
    echo.
    pause
    goto menu
) else if "%choice%"=="0" (
    echo.
    echo Выход...
    exit /b 0
) else (
    echo.
    echo Неверный выбор. Попробуйте снова.
    timeout /t 2 >nul
    goto menu
) 