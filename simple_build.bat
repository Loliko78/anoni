@echo off
echo Simple APK Builder
echo ==================
echo.

REM Проверяем существование проекта
if not exist HarvestanoApp (
    echo ERROR: HarvestanoApp folder not found!
    pause
    exit /b 1
)

cd HarvestanoApp

echo Building APK from existing project...
echo.

REM Пытаемся собрать APK
if exist gradlew.bat (
    echo Using existing gradle wrapper...
    gradlew.bat assembleRelease
) else (
    echo No gradle wrapper found, trying to create one...
    
    REM Создаем простой gradlew.bat
    echo @echo off > gradlew.bat
    echo java -version >> gradlew.bat
    echo echo Building APK... >> gradlew.bat
    echo echo Please install Android Studio and build manually >> gradlew.bat
    echo pause >> gradlew.bat
    
    echo Created basic gradle wrapper
    echo Please install Android Studio to build APK
)

echo.
echo If build failed, install Android Studio and:
echo 1. Open this folder in Android Studio
echo 2. Let it download SDK and build tools
echo 3. Build ^> Build Bundle^/APK ^> Build APK
echo.
pause 