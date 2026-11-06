@echo off
REM Build Convertidor NUP for Windows - By AbadXDev
REM Requires: .NET 8 SDK (https://dotnet.microsoft.com/download)
setlocal
cd /d %~dp0
dotnet publish ConvertidorNUP.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true -o publish
echo.
echo Listo: publish\ConvertidorNUP.exe
pause
