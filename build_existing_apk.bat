@echo off
echo Building APK from existing Android project
echo ==========================================
echo.

REM Проверяем Java
java -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java not found!
    echo Install Java JDK from https://adoptium.net/
    pause
    exit /b 1
)

REM Проверяем существование проекта
if not exist HarvestanoApp (
    echo ERROR: HarvestanoApp folder not found!
    echo Make sure you have the Android project folder
    pause
    exit /b 1
)

cd HarvestanoApp

echo Checking project structure...

REM Проверяем основные файлы
if not exist app\build.gradle (
    echo ERROR: app\build.gradle not found!
    echo Invalid Android project structure
    pause
    exit /b 1
)

if not exist build.gradle (
    echo ERROR: build.gradle not found!
    echo Invalid Android project structure
    pause
    exit /b 1
)

echo Project structure OK!

REM Проверяем gradle wrapper
if not exist gradlew.bat (
    echo Creating gradle wrapper...
    
    REM Создаем gradlew.bat
    (
    echo @rem
    echo @rem Copyright 2015 the original author or authors.
    echo @rem
    echo @rem Licensed under the Apache License, Version 2.0 ^(the "License"^);
    echo @rem you may not use this file except in compliance with the License.
    echo @rem You may obtain a copy of the License at
    echo @rem
    echo @rem      https://www.apache.org/licenses/LICENSE-2.0
    echo @rem
    echo @rem Unless required by applicable law or agreed to in writing, software
    echo @rem distributed under the License is distributed on an "AS IS" BASIS,
    echo @rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    echo @rem See the License for the specific language governing permissions and
    echo @rem limitations under the License.
    echo @rem
    echo.
    echo @if "%%1" == "" @echo off
    echo.
    echo @rem Set local scope for the variables with windows NT shell
    echo if "%%OS%%"=="Windows_NT" setlocal
    echo.
    echo set DIRNAME=%%~dp0
    echo if "%%OS%%"=="Windows_NT" set DIRNAME=%%DIRNAME:~0,-1%%
    echo.
    echo set APP_BASE_NAME=%%~n0
    echo set APP_HOME=%%DIRNAME%%
    echo.
    echo @rem Resolve any "." and ".." in APP_HOME to make it shorter.
    echo for %%%%i in ^("%%APP_HOME%%"^) do set APP_HOME=%%%%~fi
    echo.
    echo @rem Add default JVM options here. You can also use JAVA_OPTS and GRADLE_OPTS to pass JVM options to this script.
    echo set DEFAULT_JVM_OPTS="-Xmx64m" "-Xms64m"
    echo.
    echo @rem Find java.exe
    echo if defined JAVA_HOME goto findJavaFromJavaHome
    echo.
    echo set JAVA_EXE=java.exe
    echo %JAVA_EXE% -version ^>NUL 2^>^&1
    echo if "%%ERRORLEVEL%%" == "0" goto execute
    echo.
    echo echo.
    echo echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
    echo echo.
    echo echo Please set the JAVA_HOME variable in your environment to match the
    echo echo location of your Java installation.
    echo echo.
    echo goto fail
    echo.
    echo :findJavaFromJavaHome
    echo set JAVA_HOME=%%JAVA_HOME:"=%%
    echo set JAVA_EXE=%%JAVA_HOME%%/bin/java.exe
    echo.
    echo if exist "%%JAVA_EXE%%" goto execute
    echo.
    echo echo.
    echo echo ERROR: JAVA_HOME is set to an invalid directory: %%JAVA_HOME%%
    echo echo.
    echo echo Please set the JAVA_HOME variable in your environment to match the
    echo echo location of your Java installation.
    echo echo.
    echo goto fail
    echo.
    echo :execute
    echo @rem Setup the command line
    echo.
    echo set CLASSPATH=%%APP_HOME%%\\gradle\\wrapper\\gradle-wrapper.jar
    echo.
    echo @rem Execute Gradle
    echo "%%JAVA_EXE%%" %%DEFAULT_JVM_OPTS%% %%JAVA_OPTS%% %%GRADLE_OPTS%% "-Dorg.gradle.appname=%%APP_BASE_NAME%%" -classpath "%%CLASSPATH%%" org.gradle.wrapper.GradleWrapperMain %%*
    echo.
    echo :end
    echo @rem End local scope for the variables with windows NT shell
    echo if "%%ERRORLEVEL%%"=="0" goto mainEnd
    echo.
    echo :fail
    echo rem Set variable GRADLE_EXIT_CONSOLE if you need the _script_ return code instead of
    echo rem the _cmd_ return code when the batch file is called from the command line.
    echo if not "%%EXIT_CODE%%" == "0" exit /b %%EXIT_CODE%%
    echo exit /b 1
    echo.
    echo :mainEnd
    echo if "%%OS%%"=="Windows_NT" endlocal
    echo.
    echo :omega
    ) > gradlew.bat
    
    REM Создаем gradle wrapper jar
    mkdir gradle\wrapper 2>nul
    
    echo Downloading gradle wrapper jar...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/gradle/gradle/raw/master/gradle/wrapper/gradle-wrapper.jar' -OutFile 'gradle\wrapper\gradle-wrapper.jar'"
    
    echo Gradle wrapper created!
)

echo.
echo Building APK...
echo This may take several minutes...
echo.

REM Собираем APK
gradlew.bat assembleRelease

if errorlevel 1 (
    echo.
    echo ❌ Build failed!
    echo.
    echo Common solutions:
    echo 1. Check if Android SDK is installed
    echo 2. Set ANDROID_HOME environment variable
    echo 3. Install build tools via Android Studio
    echo.
    echo Alternative: Use Android Studio to open this folder
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ APK built successfully!
echo.
echo 📱 APK location: app\build\outputs\apk\release\app-release.apk
echo.
echo To install on Android device:
echo 1. Enable "Unknown sources" in Android settings
echo 2. Copy APK to your Android device
echo 3. Install APK file
echo.
echo 🌐 App will load: https://harvestano.loca.lt/
echo.
pause 