@echo off
echo ========================================
echo    LAUNCHER - PROJETS RO
echo ========================================
echo.
echo Lancement de l'interface de selection...
echo.

python launcher.py

if errorlevel 1 (
    echo.
    echo ERREUR: Impossible de lancer l'interface
    echo Verifiez que Python et PyQt5 sont installes
    pause
)
