@echo off
echo ===================================================
echo   ZOHO AUTOMATION: GITHUB DEPLOYMENT HELPER
echo ===================================================
echo.
echo This script will help you push this project to GitHub.
echo.

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/ and run this script again.
    pause
    exit /b
)

:: Prompt for GitHub Repository URL
echo Please go to GitHub, create a new repository (do not add README, gitignore, or license), and copy the repository URL.
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/repo.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] Repository URL cannot be empty.
    pause
    exit /b
)

echo.
echo 1. Initializing Git Repository...
if not exist .git (
    git init
) else (
    echo Git already initialized.
)

echo.
echo 2. Staging files...
git add .

echo.
echo 3. Checking .env file tracking...
git status | findstr /C:".env" >nul
if %errorlevel% equ 0 (
    echo [INFO] .env is properly ignored by .gitignore.
)

echo.
echo 4. Committing files...
git commit -m "Initial commit: Zoho People Playwright Automation Agent"

echo.
echo 5. Setting main branch and remote origin...
git branch -M main
git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%

echo.
echo 6. Pushing to GitHub...
echo (You may be prompted to log in to GitHub in your browser)
git push -u origin main

echo.
echo ===================================================
echo   PUSH PROCESS COMPLETED!
echo ===================================================
pause
