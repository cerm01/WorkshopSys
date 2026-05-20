@echo off
chcp 65001 >nul
echo ================================================
echo   WorkshopSys - Generador de Ejecutable (.exe)
echo ================================================
echo.

:: Verificar que existe el entorno virtual
if not exist "env\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual en la carpeta env\
    echo Ejecuta primero: python -m venv env
    pause
    exit /b 1
)

:: Verificar que existe el modelo ML
if not exist "modelo_ml_onehot.pkl" (
    echo [AVISO] No se encontro modelo_ml_onehot.pkl
    echo El modulo de prediccion de precios no funcionara.
    echo Para entrenarlo ejecuta: env\Scripts\python.exe entrenar_onehot.py
    echo.
    set /p CONTINUAR="Deseas continuar sin el modelo ML? [S/N]: "
    if /i "%CONTINUAR%" neq "S" (
        echo Cancelado.
        pause
        exit /b 0
    )
)

:: Limpiar builds anteriores
echo [1/3] Limpiando builds anteriores...
if exist "dist\WorkshopSys.exe" del /f /q "dist\WorkshopSys.exe"
if exist "build\WorkshopSys" rmdir /s /q "build\WorkshopSys"

:: Construir el ejecutable
echo [2/3] Construyendo WorkshopSys.exe (puede tardar 2-5 minutos)...
echo.
env\Scripts\pyinstaller.exe --clean WorkshopSys.spec

:: Verificar resultado
echo.
if exist "dist\WorkshopSys.exe" (
    echo ================================================
    echo [OK] Ejecutable generado exitosamente!
    echo.
    for %%F in ("dist\WorkshopSys.exe") do echo    Tamano: %%~zF bytes
    echo    Ubicacion: %CD%\dist\WorkshopSys.exe
    echo.
    echo [3/3] Puedes distribuir el archivo:
    echo    dist\WorkshopSys.exe
    echo.
    echo Para instalar en otra PC solo copia ese archivo.
    echo No requiere Python ni ninguna dependencia adicional.
    echo ================================================
) else (
    echo [ERROR] No se pudo generar el ejecutable.
    echo Revisa los mensajes de error arriba.
)

echo.
pause
