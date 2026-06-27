@echo off
set "REPO_ROOT=%~dp0..\.."
cd /d "%REPO_ROOT%"
echo === RevRate ===
echo.

if not exist ".venv\Scripts\python.exe" (
    echo .venv nie istnieje. Uruchom deploy.bat najpierw.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo === Instalacja zaleznosci ===
pip install -r requirements.txt
if errorlevel 1 (
    echo Instalacja zaleznosci nieudana
    pause
    exit /b 1
)

echo.
echo === Wypakowywanie datasetu ===
python backend\tools\unpack_dataset.py
if errorlevel 1 echo Nie udalo sie wypakowac datasetu.

echo.
echo === Uruchamianie ===
python run.py
pause