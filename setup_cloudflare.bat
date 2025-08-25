@echo off
echo Cloudflare Tunnel Setup - FREE PERMANENT DOMAIN
echo ===============================================
echo.

REM Проверяем, есть ли cloudflared
if not exist "cloudflared.exe" (
    echo Cloudflared not found! Downloading...
    call download_cloudflared.bat
)

echo.
echo Cloudflare Tunnel Setup Steps:
echo.
echo 1. Go to https://dash.cloudflare.com/
echo 2. Sign up for FREE account
echo 3. Add a domain (you can use a free subdomain)
echo 4. Go to "Zero Trust" -> "Access" -> "Tunnels"
echo 5. Create a new tunnel
echo 6. Copy the tunnel token
echo.
echo After setup, you'll get a PERMANENT domain like:
echo https://your-app.your-domain.com
echo.
echo To start tunnel with Flask:
echo 1. Run: start_cloudflare.bat
echo 2. Or manually: cloudflared.exe tunnel --url http://localhost:5000
echo.
echo Advantages:
echo - COMPLETELY FREE
echo - PERMANENT domain
echo - No credit card required
echo - Global CDN
echo - DDoS protection
echo.
pause 