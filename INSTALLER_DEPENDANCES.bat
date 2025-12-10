@echo off
echo ========================================
echo    INSTALLATION DES DEPENDANCES
echo ========================================
echo.

echo Installation des dependances pour le Projet Elyes...
cd elyesRo
pip install -r requirements.txt
cd ..
echo.

echo Installation des dependances pour le Projet Makki...
cd makkiRo
pip install -r requirements.txt
cd ..
echo.

echo Installation des dependances pour le Projet Yassine...
cd yassineRo
pip install -r requirements.txt
cd ..
echo.

echo Installation des dependances pour le Projet Aymen...
cd aymenRo
pip install -r requirements.txt
cd ..
echo.

echo ========================================
echo    INSTALLATION TERMINEE !
echo ========================================
echo.
echo Vous pouvez maintenant lancer LANCER_PROJETS.bat
echo.
pause
