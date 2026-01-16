"""
Serviço para buscar e processar dados da Mega-Sena.
Consome APIs públicas e processa os dados históricos.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from app.utils.data_processor import (
    normalize_data,
    filter_last_two_years,
    calculate_frequencies,
    generate_estimates
)


class MegaSenaService:
    """Serviço para gerenciar dados da Mega-Sena."""
    
    def __init__(self):
        # API pública da Caixa para Mega-Sena
        self.base_url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena"
        self.cache_data = None
        self.cache_date = None
    
    def _fetch_single_draw(self, num: int, cutoff_date: datetime) -> Optional[Dict]:
        """
        Busca um único concurso.
        """
        try:
            draw_response = requests.get(
                f"{self.base_url}/{num}",
                timeout=10
            )
            if draw_response.status_code == 200:
                draw_data = draw_response.json()
                
                # Verifica se a data do concurso está dentro do período
                data_apuracao = draw_data.get('dataApuracao', draw_data.get('data', draw_data.get('dataApuracaoStr', '')))
                if data_apuracao:
                    try:
                        # Tenta diferentes formatos de data
                        try:
                            draw_date = datetime.strptime(data_apuracao, '%d/%m/%Y')
                        except ValueError:
                            try:
                                draw_date = datetime.strptime(data_apuracao, '%Y-%m-%d')
                            except ValueError:
                                # Se não conseguir parsear, inclui mesmo assim
                                return draw_data
                        
                        if draw_date >= cutoff_date:
                            return draw_data
                    except (ValueError, TypeError):
                        # Se não conseguir parsear a data, inclui mesmo assim
                        return draw_data
            return None
        except requests.RequestException:
            return None

    def fetch_historical_data(self) -> List[Dict]:
        """
        Busca dados históricos da Mega-Sena dos últimos 2 anos.
        
        Returns:
            Lista de dicionários com dados dos concursos
        """
        try:
            # Busca o último concurso para saber quantos concursos existem
            response = requests.get(f"{self.base_url}", timeout=10)
            response.raise_for_status()
            last_draw = response.json()
            
            cutoff_date = datetime.now() - timedelta(days=730)
            
            all_draws = []
            concurso_num = last_draw.get('numero', last_draw.get('numeroConcurso', 1))
            start_num = max(1, concurso_num - 180)
            
            # Usa ThreadPoolExecutor para buscar em paralelo
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_num = {
                    executor.submit(self._fetch_single_draw, num, cutoff_date): num 
                    for num in range(start_num, concurso_num + 1)
                }
                
                for future in as_completed(future_to_num):
                    result = future.result()
                    if result:
                        all_draws.append(result)
            
            # Ordena por número do concurso para garantir consistência
            all_draws.sort(key=lambda x: x.get('numero', x.get('numeroConcurso', 0)))
            
            return all_draws
            
        except requests.RequestException as e:
            print(f"Erro ao buscar dados: {e}")
            return []
    
    def get_processed_data(self, force_refresh: bool = False) -> List[Dict]:
        """
        Obtém e processa os dados históricos.
        
        Args:
            force_refresh: Se True, força atualização dos dados
            
        Returns:
            Lista processada com dados dos últimos 2 anos
        """
        # Verifica cache (válido por 1 hora)
        if not force_refresh and self.cache_data is not None:
            cache_age = datetime.now() - self.cache_date if self.cache_date else timedelta(hours=2)
            if cache_age < timedelta(hours=1):
                return self.cache_data
        
        # Busca dados históricos
        raw_data = self.fetch_historical_data()
        
        # Normaliza os dados
        data = normalize_data(raw_data)
        
        # Filtra últimos 2 anos
        data_filtered = filter_last_two_years(data)
        
        # Atualiza cache
        self.cache_data = data_filtered
        self.cache_date = datetime.now()
        
        return data_filtered
    
    def get_estimate(self) -> Dict:
        """
        Gera estimativa de números mais prováveis.
        
        Returns:
            Dicionário com quadra, quina e sorte
        """
        data = self.get_processed_data()
        
        # Calcula frequências
        frequencies = calculate_frequencies(data)
        
        # Gera estimativas
        estimates = generate_estimates(frequencies)
        
        # Adiciona data atual
        estimates['data'] = datetime.now().strftime('%Y-%m-%d')
        
        return estimates
    
    def get_draw_by_date(self, date: str) -> Optional[Dict]:
        """
        Busca os números sorteados em uma data específica.
        
        Args:
            date: Data no formato YYYY-MM-DD
            
        Returns:
            Dicionário com dados do concurso ou None se não encontrado
        """
        try:
            # Converte data para formato brasileiro
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_br = date_obj.strftime('%d/%m/%Y')
            
            # Busca dados históricos
            data = self.get_processed_data()
            
            if not data:
                return None
            
            # Busca concurso na data especificada
            match = None
            for row in data:
                row_date = row.get('data', '')
                if row_date == date_br:
                    match = row
                    break
            
            if match:
                return {
                    'data': date_br,
                    'numero_concurso': str(match['numero_concurso']),
                    'numeros': match['numeros']
                }
            
            # Se não encontrou, tenta buscar diretamente na API
            # Busca em um range de concursos recentes
            response = requests.get(f"{self.base_url}", timeout=10)
            response.raise_for_status()
            last_draw = response.json()
            concurso_num = last_draw.get('numero', last_draw.get('numeroConcurso', 1))
            
            for num in range(max(1, concurso_num - 300), concurso_num + 1):
                try:
                    draw_response = requests.get(f"{self.base_url}/{num}", timeout=5)
                    if draw_response.status_code == 200:
                        draw_data = draw_response.json()
                        draw_date = draw_data.get('dataApuracao', draw_data.get('data', ''))
                        if draw_date == date_br:
                            numeros = []
                            if 'dezenas' in draw_data:
                                numeros = [int(n) for n in draw_data['dezenas']]
                            elif 'listaDezenas' in draw_data:
                                numeros = [int(n) for n in draw_data['listaDezenas']]
                            
                            return {
                                'data': date_br,
                                'numero_concurso': str(draw_data.get('numero', draw_data.get('numeroConcurso', ''))),
                                'numeros': numeros
                            }
                except requests.RequestException:
                    continue
            
            return None
            
        except ValueError:
            return None
        except requests.RequestException:
            return None
