@echo off
echo Downloading cloudflared...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
echo Cloudflared downloaded successfully!
echo.
echo To start your tunnel, run: cloudflared.exe tunnel --url http://localhost:5000
pause 