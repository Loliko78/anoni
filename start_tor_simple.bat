@echo off
chcp 65001 >nul
title Harvestano Tor Hosting

echo.
echo ========================================
echo    Harvestano Tor Hosting
echo ========================================
echo.

echo Доступные команды:
echo.
echo 1. python tor_setup.py
echo 2. python setup_harvestano_onion.py
echo 3. python check_tor_status.py
echo 4. python test_tor_connection.py
echo 5. python run_with_tor.py
echo 6. build_tor_apk.bat
echo.

echo Введите номер команды (1-6) или 0 для выхода:
set /p cmd="Команда: "

if "%cmd%"=="1" (
    echo Запуск: python tor_setup.py
    python tor_setup.py
    pause
    goto start
)

if "%cmd%"=="2" (
    echo Запуск: python setup_harvestano_onion.py
    python setup_harvestano_onion.py
    pause
    goto start
)

if "%cmd%"=="3" (
    echo Запуск: python check_tor_status.py
    python check_tor_status.py
    pause
    goto start
)

if "%cmd%"=="4" (
    echo Запуск: python test_tor_connection.py
    python test_tor_connection.py
    pause
    goto start
)

if "%cmd%"=="5" (
    echo Запуск: python run_with_tor.py
    python run_with_tor.py
    pause
    goto start
)

if "%cmd%"=="6" (
    echo Запуск: build_tor_apk.bat
    call build_tor_apk.bat
    pause
    goto start
)

if "%cmd%"=="0" (
    echo Выход...
    exit /b 0
)

echo Неверная команда. Попробуйте снова.
pause
goto start

:start
cls
goto :eof 