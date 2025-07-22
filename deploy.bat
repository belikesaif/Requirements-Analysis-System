@echo off
echo 🚀 Deploying NLP Requirements Analysis System
echo ==============================================

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed. Please install Git first.
    pause
    exit /b 1
)

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if errorlevel 1 (
    echo ❌ Not in a Git repository. Please run this script from the project root.
    pause
    exit /b 1
)

echo 📝 Committing changes...
git add .
git commit -m "Deploy: Add deployment configuration and scripts"

echo 📤 Pushing to GitHub...
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
git push origin %CURRENT_BRANCH%

echo ✅ Code pushed to GitHub successfully!
echo.
echo Next steps:
echo 1. Deploy backend to Render:
echo    - Go to https://render.com
echo    - Create new Web Service
echo    - Connect GitHub repo: Requirements-Analysis-System
echo    - Set root directory to: backend
echo    - Use Python environment
echo.
echo 2. Deploy frontend to Vercel:
echo    - Run: cd frontend ^&^& vercel --prod
echo    - Or use Vercel dashboard
echo.
echo 📖 See DEPLOYMENT_GUIDE.md for detailed instructions
pause
