@echo off
chcp 65001 >nul
echo ========================================
echo    Сборка Harvestano APK с Tor
echo ========================================
echo.

REM Проверяем наличие Android SDK
if not exist "%ANDROID_HOME%" (
    echo ОШИБКА: ANDROID_HOME не установлен
    echo Установите Android SDK и добавьте ANDROID_HOME в переменные среды
    pause
    exit /b 1
)

echo Проверяем наличие Gradle...
cd HarvestanoApp

REM Очищаем предыдущую сборку
echo Очищаем предыдущую сборку...
call gradlew clean

REM Собираем APK
echo Собираем APK...
call gradlew assembleRelease

REM Проверяем результат
if exist "app\build\outputs\apk\release\app-release.apk" (
    echo.
    echo ========================================
    echo    Сборка завершена успешно!
    echo ========================================
    echo.
    echo APK файл: app\build\outputs\apk\release\app-release.apk
    echo.
    echo Инструкции по установке:
    echo 1. Установите APK на Android устройство
    echo 2. Установите Orbot (Tor для Android) из Play Store
    echo 3. Запустите Orbot и включите VPN
    echo 4. Запустите Harvestano приложение
    echo.
    echo Примечание: Для работы приложения необходимо
    echo настроить Tor сервер и получить .onion адрес
    echo.
) else (
    echo.
    echo ========================================
    echo    ОШИБКА СБОРКИ!
    echo ========================================
    echo.
    echo Проверьте:
    echo - Установлен ли Android SDK
    echo - Правильно ли настроен ANDROID_HOME
    echo - Есть ли все необходимые файлы
    echo.
)

pause 