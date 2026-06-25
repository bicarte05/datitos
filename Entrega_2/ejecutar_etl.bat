@echo off
echo =========================================
echo Iniciando proceso ETL - Los Datitos Delivery
echo =========================================

:: 1. Entrar a la carpeta del proyecto
cd C:\Users\iancu\OneDrive\Escritorio\github_repos\datitos\Entrega_2

:: 2. Activar el entorno virtual (usando la ruta exacta de tu venv)
call C:\Users\iancu\OneDrive\Escritorio\github_repos\datitos\venv\Scripts\activate.bat

:: 3. Ejecutar el script y guardar el registro
python etl.py >> historial_etl.log 2>&1

echo Proceso finalizado. Revisa historial_etl.log