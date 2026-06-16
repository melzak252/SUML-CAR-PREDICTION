@echo off
cd /d "%~dp0"
echo === RevRate - Automatyczna instalacja ===
echo.

set "GIT_DIR=%~dp0git"
set "GIT_EXE=%GIT_DIR%\cmd\git.exe"
set "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.49.0.windows.1/MinGit-2.49.0-64-bit.zip"
set "GIT_ZIP=%TEMP%\mingit.zip"

set "PY_DIR=%~dp0python310"
set "PY_EXE=%PY_DIR%\python.exe"
set "PY_URL=https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip"
set "PY_ZIP=%TEMP%\python-embed.zip"

:: === Git ===
if exist "%GIT_EXE%" goto :git_ok
set "LOCAL_GIT=%~dp0MinGit-2.49.0-64-bit.zip"
if exist "%LOCAL_GIT%" goto :git_local
echo Pobieranie Git...
powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%GIT_URL%' -OutFile '%GIT_ZIP%' -UseBasicParsing"
if errorlevel 1 (
    echo.
    echo Nie udalo sie pobrac Git z sieci.
    echo Pobierz recznie plik MinGit-2.49.0-64-bit.zip
    echo z https://github.com/git-for-windows/git/releases
    echo i umiesc go obok deploy.bat, potem uruchom ponownie.
    pause
    exit /b 1
)
goto :git_extract

:git_local
echo Znaleziono lokalny plik ZIP Git.
set "GIT_ZIP=%LOCAL_GIT%"

:git_extract
echo Wypakowywanie Git...
powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%GIT_ZIP%' -DestinationPath '%GIT_DIR%' -Force"
if not "%LOCAL_GIT%"=="" del "%GIT_ZIP%" 2>nul

:git_ok
echo Git gotowy.
set "PATH=%GIT_DIR%\cmd;%PATH%"

:: === Python (extract only, configure later) ===
if exist "%PY_EXE%" goto :py_ok
set "LOCAL_ZIP=%~dp0python-3.10.11-embed-amd64.zip"
if exist "%LOCAL_ZIP%" goto :py_local
echo Pobieranie Python 3.10...
powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_ZIP%' -UseBasicParsing"
if errorlevel 1 (
    echo.
    echo Nie udalo sie pobrac Pythona z sieci.
    echo Pobierz recznie plik python-3.10.11-embed-amd64.zip
    echo z https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip
    echo i umiesc go obok deploy.bat, potem uruchom ponownie.
    pause
    exit /b 1
)
goto :py_extract

:py_local
echo Znaleziono lokalny plik ZIP Pythona.
set "PY_ZIP=%LOCAL_ZIP%"

:py_extract
echo Wypakowywanie Python...
powershell -ExecutionPolicy Bypass -Command "Expand-Archive -Path '%PY_ZIP%' -DestinationPath '%PY_DIR%' -Force"
if not "%LOCAL_ZIP%"=="" del "%PY_ZIP%" 2>nul

:py_ok
echo Python wypakowany.

:: === Klonowanie repo ===
if exist "SUML-CAR-PREDICTION\" (
    echo Repozytorium juz istnieje. Aktualizacja...
    cd SUML-CAR-PREDICTION
    git pull
) else (
    echo Klonowanie repozytorium...
    git clone -b deployment https://github.com/melzak252/SUML-CAR-PREDICTION.git
    cd SUML-CAR-PREDICTION
)

:: === Konfiguracja Python (pip + virtualenv) ===
if exist "%PY_DIR%\Scripts\pip.exe" goto :pip_ok
echo Instalacja pip i virtualenv...
powershell -ExecutionPolicy Bypass -Command ^
    "$p='%PY_DIR%';" ^
    "$pth=Get-ChildItem \"$p\*._pth\" | Select-Object -First 1;" ^
    "$c=Get-Content $pth.FullName;" ^
    "$c=$c | ForEach-Object { $_ -replace '^#?\s*import site','import site' };" ^
    "if($c -notcontains 'Lib\site-packages'){$c+='Lib\site-packages'};" ^
    "Set-Content $pth.FullName -Value $c;" ^
    "& \"$p\python.exe\" 'scripts\windows\get-pip.py' 2>$null | Out-Null;" ^
    "& \"$p\python.exe\" -m pip install virtualenv 2>$null | Out-Null"

:pip_ok
echo Python gotowy.

:: === venv ===
if exist ".venv\Scripts\python.exe" goto :venv_exists
echo === Tworzenie srodowiska wirtualnego ===
"%PY_EXE%" -m virtualenv .venv
if errorlevel 1 (
    echo Nie udalo sie utworzyc venv
    pause
    exit /b 1
)

echo Kopiowanie bibliotek Pythona do venv...
copy /y "%PY_DIR%\python310.zip" ".venv\Scripts\" >nul
for %%f in ("%PY_DIR%\*.pyd") do copy /y "%%f" ".venv\Scripts\" >nul
copy /y "%PY_DIR%\python3.dll" ".venv\Scripts\" >nul
copy /y "%PY_DIR%\python310.dll" ".venv\Scripts\" >nul
copy /y "%PY_DIR%\vcruntime140.dll" ".venv\Scripts\" >nul
copy /y "%PY_DIR%\vcruntime140_1.dll" ".venv\Scripts\" >nul
copy /y "%PY_DIR%\libcrypto-1_1.dll" ".venv\Scripts\" >nul
copy /y "%PY_DIR%\libssl-1_1.dll" ".venv\Scripts\" >nul
copy /y "%PY_DIR%\libffi-7.dll" ".venv\Scripts\" >nul
copy /y "%PY_DIR%\sqlite3.dll" ".venv\Scripts\" >nul

echo Tworzenie pliku _pth dla venv...
(
    echo python310.zip
    echo .
    echo ..\Lib
    echo ..\Lib\site-packages
    echo import site
) > ".venv\Scripts\python310._pth"

echo Aktualizacja konfiguracji venv...
set "VENV_SCRIPTS=%CD%\.venv\Scripts"
powershell -ExecutionPolicy Bypass -Command ^
    "$h='%VENV_SCRIPTS%'.Replace('\','/');" ^
    "$c=Get-Content '.venv\pyvenv.cfg';" ^
    "for($i=0;$i -lt $c.Count;$i++){if($c[$i] -match '^home = '){$c[$i]='home = '+$h}};" ^
    "Set-Content '.venv\pyvenv.cfg' -Value $c"

:venv_exists
echo .venv gotowe.

:: === Instalacja zaleznosci ===
call .venv\Scripts\activate.bat
echo.
echo === Instalacja zaleznosci ===
pip install -r requirements.txt
if errorlevel 1 (
    echo Instalacja zaleznosci nieudana
    pause
    exit /b 1
)
call deactivate

:: === Czyszczenie tymczasowych narzedzi ===
echo.
echo === Czyszczenie tymczasowych plikow ===
cd /d "%~dp0"
if exist "python310\" (
    echo Usuwanie tymczasowego Python...
    rmdir /s /q "python310" 2>nul
)
if exist "git\" (
    echo Usuwanie tymczasowego Git...
    rmdir /s /q "git" 2>nul
)
cd /d "%~dp0SUML-CAR-PREDICTION"

:: === Setup (rozpakowanie datasetu + uruchomienie) ===
echo.
echo === Uruchamianie setup ===
call scripts\windows\setup.bat
pause