@echo off
cd /d "%~dp0"
goto menu

:menu
cls
echo what mode do you want?
echo def: downloads all files with there installers
echo short: downloads most files with there installers
echo long: downloads all files witout there installers (can take min or houers more time but you know thay are all installed no madder what)
echo forse: forse downloads all files via installers with admin and if it fails it deletes the failed files and trys agen
set /p mode="enter choice: "

if /I not "%mode%"=="def" ^
if /I not "%mode%"=="short" ^
if /I not "%mode%"=="long" ^
if /I not "%mode%"=="forse" (
    echo Invalid mode!
    timeout /t 3 2>&1
    goto menu
) else (
    if exist "mode_A.txt" (
        del "mode_A.txt"
    )
    echo %mode%>mode_A.txt
    start "" cmd /k "python installer.py" 
)