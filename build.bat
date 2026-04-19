@echo off
setlocal

echo ============================================
echo  eFootball Patch Manager — Build
echo ============================================
echo.

:: --- Verification venv ---
if not exist ".venv\Scripts\python.exe" (
    echo [ERREUR] .venv introuvable. Lance d'abord :
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install customtkinter darkdetect py7zr rarfile pyinstaller
    pause & exit /b 1
)

:: --- Nettoyage ---
echo [1/3] Nettoyage des builds precedents...
if exist "build" rmdir /s /q "build"
if exist "dist\eFootball Patch Manager" rmdir /s /q "dist\eFootball Patch Manager"
echo       OK

:: --- PyInstaller : version portable ---
echo.
echo [2/3] Build PyInstaller (version portable)...
.venv\Scripts\pyinstaller eFootball_PatchManager.spec --noconfirm
if errorlevel 1 (
    echo [ERREUR] PyInstaller a echoue.
    pause & exit /b 1
)
echo       OK — dossier : dist\eFootball Patch Manager\

:: --- Inno Setup : installateur .exe ---
echo.
echo [3/3] Build installateur Inno Setup...

set INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
if not exist "%INNO_PATH%" (
    echo [AVERTISSEMENT] Inno Setup introuvable dans "%INNO_PATH%".
    echo                 Installer depuis https://jrsoftware.org/isinfo.php
    echo                 L'installateur .exe n'a pas ete genere.
    echo                 La version portable est disponible dans dist\
    goto :done
)

"%INNO_PATH%" "installer\setup.iss"
if errorlevel 1 (
    echo [ERREUR] Inno Setup a echoue.
    pause & exit /b 1
)
echo       OK — installateur : dist\eFootball_PatchManager_1.3.0_Setup.exe

:done
echo.
echo ============================================
echo  Build termine.
echo  Livrables dans : dist\
echo ============================================
pause
