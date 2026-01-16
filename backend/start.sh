#!/bin/bash
echo "Iniciando servidor FastAPI..."
echo ""
echo "Certifique-se de ter ativado o ambiente virtual antes de executar este script."
echo ""
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
