@echo off
echo Iniciando servidor FastAPI...
echo.

if exist "..\venv\Scripts\activate.bat" (
    echo Ativando ambiente virtual...
    call ..\venv\Scripts\activate.bat
) else (
    echo Ambiente virtual nao encontrado ou nao configurado automaticamente.
    echo Certifique-se de ter ativado o ambiente virtual manualmente.
)

echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
