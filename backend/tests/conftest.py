"""
Fixtures compartilhadas para testes.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from typing import List, Dict

from app.main import app
from app.services.mega_sena_service import MegaSenaService


@pytest.fixture
def client():
    """Cliente de teste para a API."""
    return TestClient(app)


@pytest.fixture
def mock_draw_data() -> List[Dict]:
    """Dados mockados de concursos."""
    return [
        {
            "numero": 2650,
            "dataApuracao": "15/01/2024",
            "dezenas": ["05", "12", "23", "45", "58", "60"]
        },
        {
            "numero": 2649,
            "dataApuracao": "13/01/2024",
            "dezenas": ["03", "12", "23", "35", "45", "58"]
        },
        {
            "numero": 2648,
            "dataApuracao": "10/01/2024",
            "dezenas": ["05", "10", "23", "30", "45", "58"]
        }
    ]


@pytest.fixture
def mock_normalized_data() -> List[Dict]:
    """Dados normalizados mockados."""
    return [
        {
            "data": "15/01/2024",
            "numero_concurso": "2650",
            "numeros": [5, 12, 23, 45, 58, 60]
        },
        {
            "data": "13/01/2024",
            "numero_concurso": "2649",
            "numeros": [3, 12, 23, 35, 45, 58]
        },
        {
            "data": "10/01/2024",
            "numero_concurso": "2648",
            "numeros": [5, 10, 23, 30, 45, 58]
        }
    ]


@pytest.fixture
def mock_frequencies() -> Dict[int, int]:
    """Frequências mockadas."""
    frequencies = {i: 0 for i in range(1, 61)}
    frequencies.update({
        5: 10,
        12: 9,
        23: 15,
        45: 12,
        58: 11,
        60: 8,
        3: 7,
        35: 6,
        10: 5,
        30: 4
    })
    return frequencies


@pytest.fixture
def mock_estimate() -> Dict:
    """Estimativa mockada."""
    return {
        "data": "2024-01-15",
        "quadra": [5, 12, 23, 45],
        "quina": [5, 12, 23, 45, 58],
        "sorte": [5, 12, 23, 45, 58, 60]
    }


@pytest.fixture
def service():
    """Instância do serviço para testes."""
    return MegaSenaService()


@pytest.fixture(autouse=True)
def clear_cache(service):
    """Limpa o cache antes de cada teste."""
    service.clear_cache()
    yield
    service.clear_cache()
