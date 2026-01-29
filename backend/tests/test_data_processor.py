"""
Testes unitários para funções de processamento de dados.
"""

import pytest
from datetime import datetime, timedelta

from app.utils.data_processor import (
    normalize_data,
    filter_last_two_years,
    calculate_frequencies,
    generate_estimates
)


class TestNormalizeData:
    """Testes para a função normalize_data."""
    
    def test_normalize_empty_data(self):
        """Testa normalização de lista vazia."""
        result = normalize_data([])
        assert result == []
    
    def test_normalize_with_dezenas(self, mock_draw_data):
        """Testa normalização com campo 'dezenas'."""
        result = normalize_data(mock_draw_data)
        
        assert len(result) == 3
        assert result[0]["data"] == "15/01/2024"
        assert result[0]["numero_concurso"] == "2650"
        assert result[0]["numeros"] == [5, 12, 23, 45, 58, 60]
    
    def test_normalize_with_lista_dezenas(self):
        """Testa normalização com campo 'listaDezenas'."""
        data = [{
            "numero": 2650,
            "dataApuracao": "15/01/2024",
            "listaDezenas": ["05", "12", "23", "45", "58", "60"]
        }]
        
        result = normalize_data(data)
        assert len(result) == 1
        assert result[0]["numeros"] == [5, 12, 23, 45, 58, 60]
    
    def test_normalize_filters_invalid_data(self):
        """Testa que dados inválidos são filtrados."""
        data = [
            {"numero": 1, "dataApuracao": "01/01/2024"},  # Sem números
            {"numero": 2, "dataApuracao": "02/01/2024", "dezenas": ["01", "02"]},  # Poucos números
            {"numero": 3, "dataApuracao": "03/01/2024", "dezenas": ["01", "02", "03", "04", "05", "06"]}  # Válido
        ]
        
        result = normalize_data(data)
        assert len(result) == 1
        assert result[0]["numero_concurso"] == "3"


class TestFilterLastTwoYears:
    """Testes para a função filter_last_two_years."""
    
    def test_filter_empty_data(self):
        """Testa filtro de lista vazia."""
        result = filter_last_two_years([])
        assert result == []
    
    def test_filter_recent_data(self):
        """Testa que dados recentes são mantidos."""
        recent_date = (datetime.now() - timedelta(days=30)).strftime('%d/%m/%Y')
        data = [{
            "data": recent_date,
            "numero_concurso": "2650",
            "numeros": [1, 2, 3, 4, 5, 6]
        }]
        
        result = filter_last_two_years(data)
        assert len(result) == 1
    
    def test_filter_old_data(self):
        """Testa que dados antigos são removidos."""
        old_date = (datetime.now() - timedelta(days=800)).strftime('%d/%m/%Y')
        data = [{
            "data": old_date,
            "numero_concurso": "2000",
            "numeros": [1, 2, 3, 4, 5, 6]
        }]
        
        result = filter_last_two_years(data)
        assert len(result) == 0
    
    def test_filter_mixed_data(self):
        """Testa filtro com dados mistos."""
        recent = (datetime.now() - timedelta(days=30)).strftime('%d/%m/%Y')
        old = (datetime.now() - timedelta(days=800)).strftime('%d/%m/%Y')
        
        data = [
            {"data": recent, "numero_concurso": "2650", "numeros": [1, 2, 3, 4, 5, 6]},
            {"data": old, "numero_concurso": "2000", "numeros": [1, 2, 3, 4, 5, 6]},
            {"data": recent, "numero_concurso": "2649", "numeros": [1, 2, 3, 4, 5, 6]}
        ]
        
        result = filter_last_two_years(data)
        assert len(result) == 2


class TestCalculateFrequencies:
    """Testes para a função calculate_frequencies."""
    
    def test_calculate_empty_data(self):
        """Testa cálculo com lista vazia."""
        result = calculate_frequencies([])
        
        assert len(result) == 60
        assert all(v == 0 for v in result.values())
    
    def test_calculate_frequencies(self, mock_normalized_data):
        """Testa cálculo de frequências."""
        result = calculate_frequencies(mock_normalized_data)
        
        assert result[23] == 3  # Aparece em todos os 3 concursos
        assert result[45] == 3
        assert result[58] == 3
        assert result[12] == 2
        assert result[5] == 2
        assert result[60] == 1
        assert result[1] == 0  # Não aparece
    
    def test_calculate_frequencies_bounds(self):
        """Testa que apenas números de 1 a 60 são contados."""
        data = [{
            "data": "01/01/2024",
            "numero_concurso": "1",
            "numeros": [0, 5, 10, 61, 100]  # Números fora do range
        }]
        
        result = calculate_frequencies(data)
        assert result[5] == 1
        assert result[10] == 1
        # Números fora do range não devem causar erro


class TestGenerateEstimates:
    """Testes para a função generate_estimates."""
    
    def test_generate_estimates(self, mock_frequencies):
        """Testa geração de estimativas."""
        result = generate_estimates(mock_frequencies)
        
        assert "quadra" in result
        assert "quina" in result
        assert "sorte" in result
        
        assert len(result["quadra"]) == 4
        assert len(result["quina"]) == 5
        assert len(result["sorte"]) == 6
        
        # Verifica que os números mais frequentes estão incluídos
        assert 23 in result["sorte"]  # Mais frequente
        assert 45 in result["sorte"]
        assert 58 in result["sorte"]
    
    def test_estimates_are_sorted(self, mock_frequencies):
        """Testa que estimativas são ordenadas."""
        result = generate_estimates(mock_frequencies)
        
        assert result["quadra"] == sorted(result["quadra"])
        assert result["quina"] == sorted(result["quina"])
        assert result["sorte"] == sorted(result["sorte"])
    
    def test_generate_with_empty_frequencies(self):
        """Testa geração com frequências vazias."""
        frequencies = {i: 0 for i in range(1, 61)}
        result = generate_estimates(frequencies)
        
        assert len(result["quadra"]) == 4
        assert len(result["quina"]) == 5
        assert len(result["sorte"]) == 6
