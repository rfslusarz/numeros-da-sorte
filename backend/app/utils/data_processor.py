"""
Módulo para processamento de dados da Mega-Sena.
Calcula frequências e probabilidades dos números.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any

def normalize_data(data: List[Dict]) -> List[Dict]:
    """
    Normaliza os dados dos concursos em uma lista de dicionários.
    
    Args:
        data: Lista de dicionários com dados dos concursos
        
    Returns:
        Lista de dicionários com chaves: data, numero_concurso, numeros
    """
    if not data:
        return []
    
    records = []
    for item in data:
        # Extrai os números sorteados
        numeros = []
        
        # Tenta diferentes formatos de resposta da API
        if 'dezenas' in item and isinstance(item['dezenas'], list):
            try:
                numeros = [int(n) for n in item['dezenas']]
            except (ValueError, TypeError):
                pass
        elif 'listaDezenas' in item and isinstance(item['listaDezenas'], list):
            try:
                numeros = [int(n) for n in item['listaDezenas']]
            except (ValueError, TypeError):
                pass
        elif 'numeros' in item and isinstance(item['numeros'], list):
            try:
                numeros = [int(n) for n in item['numeros']]
            except (ValueError, TypeError):
                pass
        
        # Se encontrou números válidos, adiciona ao registro
        if numeros and len(numeros) >= 4:  # Pelo menos 4 números (quadra)
            records.append({
                'data': item.get('dataApuracao', item.get('data', item.get('dataApuracaoStr', ''))),
                'numero_concurso': str(item.get('numero', item.get('numeroConcurso', item.get('concurso', '')))),
                'numeros': numeros
            })
    
    return records


def filter_last_two_years(data: List[Dict]) -> List[Dict]:
    """
    Filtra apenas os concursos dos últimos 2 anos.
    
    Args:
        data: Lista de dicionários com dados dos concursos
        
    Returns:
        Lista filtrada
    """
    if not data:
        return data
    
    # Data de corte: 2 anos atrás
    cutoff_date = datetime.now() - timedelta(days=730)
    
    filtered_data = []
    
    for item in data:
        date_str = item.get('data', '')
        if not date_str:
            continue
            
        try:
            # Tenta converter a data
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            
            if date_obj >= cutoff_date:
                # Adiciona o objeto datetime para facilitar uso posterior, ou mantém string?
                # Vamos manter string para compatibilidade, mas a comparação foi feita
                filtered_data.append(item)
        except ValueError:
            pass
            
    return filtered_data


def calculate_frequencies(data: List[Dict]) -> Dict[int, int]:
    """
    Calcula a frequência de cada número (1 a 60).
    
    Args:
        data: Lista de dicionários com dados dos concursos
        
    Returns:
        Dicionário com frequência de cada número
    """
    frequencies = {i: 0 for i in range(1, 61)}
    
    if not data:
        return frequencies
    
    # Conta a frequência de cada número
    for row in data:
        numeros = row.get('numeros', [])
        if isinstance(numeros, list):
            for num in numeros:
                if 1 <= num <= 60:
                    frequencies[num] += 1
    
    return frequencies


def calculate_probabilities(frequencies: Dict[int, int]) -> Dict[int, float]:
    """
    Calcula a probabilidade simples baseada em recorrência histórica.
    
    Args:
        frequencies: Dicionário com frequência de cada número
        
    Returns:
        Dicionário com probabilidade de cada número
    """
    total_occurrences = sum(frequencies.values())
    
    if total_occurrences == 0:
        return {i: 0.0 for i in range(1, 61)}
    
    probabilities = {}
    for num in range(1, 61):
        probabilities[num] = frequencies[num] / total_occurrences if total_occurrences > 0 else 0.0
    
    return probabilities


def generate_estimates(frequencies: Dict[int, int]) -> Dict[str, List[int]]:
    """
    Gera estimativas de quadra, quina e sena baseadas nas frequências.
    
    Args:
        frequencies: Dicionário com frequência de cada número
        
    Returns:
        Dicionário com quadra, quina e sorte (sena)
    """
    # Ordena os números por frequência (mais frequentes primeiro)
    sorted_numbers = sorted(frequencies.items(), key=lambda x: x[1], reverse=True)
    
    # Extrai apenas os números (sem a frequência)
    numbers_by_frequency = [num for num, _ in sorted_numbers]
    
    # Gera as estimativas
    quadra = numbers_by_frequency[:4] if len(numbers_by_frequency) >= 4 else numbers_by_frequency
    quina = numbers_by_frequency[:5] if len(numbers_by_frequency) >= 5 else numbers_by_frequency
    sorte = numbers_by_frequency[:6] if len(numbers_by_frequency) >= 6 else numbers_by_frequency
    
    # Ordena os números em ordem crescente para melhor visualização
    quadra.sort()
    quina.sort()
    sorte.sort()
    
    return {
        'quadra': quadra,
        'quina': quina,
        'sorte': sorte
    }
