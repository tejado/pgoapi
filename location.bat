@echo off
:begin
echo Starting webpage
Start "" "C:\Users\USERNAME\Desktop\pokemongo-api-demo-maps\chromeGo"
echo Select location:
echo =============
echo -
echo 1) Location 1 
echo 2) Location 2
echo 3) Location 3
echo 4) Location 4
echo -
set /p op=Type option:
if "%op%"=="1" goto op1
if "%op%"=="2" goto op2
if "%op%"=="3" goto op3
if "%op%"=="4" goto op4

:op1
python main.py -u USERNAME -p PASSWORD -l "12.13, 14.15"

:op2
python main.py -u USERNAME -p PASSWORD -l "12.52, 13.25"

:op3
python main.py -u USERNAME -p PASSWORD -l "16.61, 13.25"

:op4
python main.py -u USERNAME -p PASSWORD -l "Las Vegas, Nevada, USA"

:exit
@exit
