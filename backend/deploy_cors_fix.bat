@echo off
REM Deploy Backend with CORS Fixes to Render (Windows)

echo 🚀 Deploying Backend with CORS Fixes
echo ======================================

REM Check if we're in the backend directory
if not exist "main.py" (
    echo ❌ Error: Please run this script from the backend directory
    exit /b 1
)

echo 📋 CORS Configuration Summary:
echo - Frontend URL: https://nrasfrontend.vercel.app
echo - Backend URL: https://requirements-analysis-system.onrender.com
echo - CORS: Configured for Vercel deployment

REM Test local backend first (if running)
echo.
echo 🧪 Testing local CORS configuration...
python test_cors.py
if errorlevel 1 (
    echo ⚠️ Local CORS test failed or backend not running locally
) else (
    echo ✅ Local CORS test passed
)

REM Check git status
echo.
echo 📝 Git Status:
git status --short

REM Add and commit changes
echo.
echo 💾 Committing CORS fixes...
git add main.py render.yaml test_cors.py deploy_cors_fix.sh deploy_cors_fix.bat
git commit -m "🔧 Fix CORS configuration for Vercel frontend - Add specific Vercel URL to allowed origins - Set FRONTEND_URL environment variable - Add explicit CORS preflight handler - Include health check endpoints - Add CORS testing script Fixes: Access-Control-Allow-Origin header missing"

REM Push to trigger Render deployment
echo.
echo 🚀 Pushing to trigger Render deployment...
git push origin HEAD

echo.
echo ✅ Deployment triggered!
echo.
echo 📋 Next Steps:
echo 1. Wait for Render deployment to complete (3-5 minutes)
echo 2. Test the API endpoint: https://requirements-analysis-system.onrender.com/health
echo 3. Test CORS with: python test_cors.py
echo 4. Verify frontend can connect to backend
echo.
echo 🔗 Monitor deployment at:
echo    https://dashboard.render.com/
echo.
echo 🐛 If issues persist:
echo    1. Check Render logs for deployment errors
echo    2. Verify environment variables are set correctly
echo    3. Test with browser dev tools network tab
echo    4. Check Render service logs for CORS-related messages

pause
