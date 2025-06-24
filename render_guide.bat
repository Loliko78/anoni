@echo off
echo Render Deployment Guide - FREE FIXED DOMAIN
echo ==========================================
echo.
echo 1. Go to https://render.com/
echo 2. Sign up with GitHub (FREE)
echo 3. Click "New +" then "Web Service"
echo 4. Connect your GitHub repository: anoni
echo 5. Configure:
echo    - Name: harvestano (or any name)
echo    - Environment: Python 3
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: gunicorn --worker-class eventlet -w 1 app:app --bind 0.0.0.0:$PORT
echo    - Plan: Free
echo 6. Click "Create Web Service"
echo 7. You'll get a FIXED domain like: https://harvestano.onrender.com
echo.
echo Your app is already configured with:
echo - requirements.txt (dependencies)
echo - render.yaml (configuration)
echo.
echo After deployment:
echo - Your domain will be PERMANENT
echo - FREE tier available
echo - Automatic HTTPS
echo.
pause 