@echo off
echo ========================================
echo   GESTION DE FLOTTE AVANCEE V2.0
echo ========================================
echo.
echo Lancement de l'application...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ERREUR lors du lancement!
    echo Verifiez que PyQt5 est installe: pip install -r requirements.txt
    pause
)
