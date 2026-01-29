"""
Testes de integração para endpoints da API.
"""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Testes para o endpoint /api/health."""
    
    def test_health_check(self, client):
        """Testa health check básico."""
        response = client.get("/api/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data
        assert "cache_type" in data
    
    def test_root_health_check(self, client):
        """Testa health check no endpoint raiz."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["status"] == "ok"
        assert "timestamp" in data


class TestRootEndpoint:
    """Testes para o endpoint raiz."""
    
    def test_root_endpoint(self, client):
        """Testa endpoint raiz."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data
        assert "timestamp" in data


class TestEstimateEndpoint:
    """Testes para o endpoint /api/estimate."""
    
    @pytest.mark.slow
    def test_get_estimate_success(self, client, mocker):
        """Testa geração de estimativa com sucesso."""
        # Mock do serviço para evitar chamadas reais à API
        mock_estimate = {
            "data": "2024-01-15",
            "quadra": [5, 12, 23, 45],
            "quina": [5, 12, 23, 45, 58],
            "sorte": [5, 12, 23, 45, 58, 60]
        }
        
        mocker.patch(
            'app.routes.api.service.get_estimate',
            return_value=mock_estimate
        )
        
        response = client.get("/api/estimate")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "data" in data
        assert "quadra" in data
        assert "quina" in data
        assert "sorte" in data
        
        assert len(data["quadra"]) == 4
        assert len(data["quina"]) == 5
        assert len(data["sorte"]) == 6
    
    def test_get_estimate_validation(self, client, mocker):
        """Testa validação da resposta de estimativa."""
        # Mock com dados inválidos
        mock_estimate = {
            "data": "2024-01-15",
            "quadra": [1, 2],  # Apenas 2 números (inválido)
            "quina": [1, 2, 3, 4, 5],
            "sorte": [1, 2, 3, 4, 5, 6]
        }
        
        mocker.patch(
            'app.routes.api.service.get_estimate',
            return_value=mock_estimate
        )
        
        response = client.get("/api/estimate")
        
        # Deve retornar erro de validação
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDrawEndpoint:
    """Testes para o endpoint /api/draw/{date}."""
    
    def test_get_draw_invalid_date_format(self, client):
        """Testa busca com formato de data inválido."""
        response = client.get("/api/draw/invalid-date")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        
        assert "detail" in data
        assert "error_code" in data
    
    def test_get_draw_not_found(self, client, mocker):
        """Testa busca de concurso não encontrado."""
        from app.exceptions import DrawNotFoundError
        
        mocker.patch(
            'app.routes.api.service.get_draw_by_date',
            side_effect=DrawNotFoundError("2024-01-15")
        )
        
        response = client.get("/api/draw/2024-01-15")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        
        assert "detail" in data
        assert "error_code" in data
    
    def test_get_draw_success(self, client, mocker):
        """Testa busca de concurso com sucesso."""
        mock_draw = {
            "data": "15/01/2024",
            "numero_concurso": "2650",
            "numeros": [5, 12, 23, 45, 58, 60]
        }
        
        mocker.patch(
            'app.routes.api.service.get_draw_by_date',
            return_value=mock_draw
        )
        
        response = client.get("/api/draw/2024-01-15")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["data"] == "15/01/2024"
        assert data["numero_concurso"] == "2650"
        assert len(data["numeros"]) == 6


class TestStatsEndpoint:
    """Testes para o endpoint /api/stats."""
    
    def test_get_stats(self, client):
        """Testa obtenção de estatísticas."""
        response = client.get("/api/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "cache_type" in data
        assert "circuit_breaker" in data
        assert "timestamp" in data


class TestCacheClearEndpoint:
    """Testes para o endpoint /api/cache/clear."""
    
    def test_clear_cache(self, client):
        """Testa limpeza de cache."""
        response = client.post("/api/cache/clear")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "message" in data
        assert "timestamp" in data


class TestMiddleware:
    """Testes para middleware."""
    
    def test_security_headers(self, client):
        """Testa que headers de segurança são adicionados."""
        response = client.get("/health")
        
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers
    
    def test_custom_headers(self, client):
        """Testa headers customizados."""
        response = client.get("/health")
        
        assert "X-Process-Time" in response.headers
        assert "X-API-Version" in response.headers


class TestCORS:
    """Testes para configuração de CORS."""
    
    def test_cors_headers(self, client):
        """Testa que CORS está configurado."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        assert "access-control-allow-origin" in response.headers
