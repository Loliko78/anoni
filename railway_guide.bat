@echo off
echo Railway Deployment Guide - FREE FIXED DOMAIN
echo ============================================
echo.
echo 1. Go to https://railway.app/
echo 2. Sign up with GitHub (FREE)
echo 3. Click "New Project"
echo 4. Select "Deploy from GitHub repo"
echo 5. Choose your repository: anoni
echo 6. Railway will automatically:
echo    - Detect Python project
echo    - Install dependencies
echo    - Deploy your app
echo    - Give you a FIXED domain like: https://harvestano.railway.app
echo.
echo Your app is already configured with:
echo - requirements.txt (dependencies)
echo - Procfile (start command)
echo - railway.json (configuration)
echo.
echo After deployment:
echo - Your domain will be PERMANENT
echo - You can set custom domain in settings
echo - FREE tier includes 500 hours/month
echo.
echo To deploy manually via CLI:
echo 1. Install Railway CLI: npm install -g @railway/cli
echo 2. Run: railway login
echo 3. Run: railway init
echo 4. Run: railway up
echo.
pause 