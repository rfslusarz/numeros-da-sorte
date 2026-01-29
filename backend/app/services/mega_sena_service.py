"""
Serviço para buscar e processar dados da Mega-Sena.
Consome APIs públicas e processa os dados históricos.
Versão refatorada com cache, circuit breaker e logging estruturado.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

from app.config import settings
from app.utils.data_processor import (
    normalize_data,
    filter_last_two_years,
    calculate_frequencies,
    generate_estimates
)
from app.utils.cache import get_cache
from app.utils.circuit_breaker import get_api_circuit_breaker
from app.utils.logger import get_logger
from app.exceptions import (
    APIConnectionError,
    DataProcessingError,
    DrawNotFoundError,
    CircuitBreakerOpenError
)

logger = get_logger(__name__)


class MegaSenaService:
    """Serviço para gerenciar dados da Mega-Sena."""
    
    def __init__(self):
        self.base_url = settings.mega_sena_api_url
        self.cache = get_cache()
        self.circuit_breaker = get_api_circuit_breaker()
        logger.info(f"MegaSenaService initialized with cache type: {self.cache.get_type()}")
    
    def _fetch_single_draw(self, num: int, cutoff_date: datetime) -> Optional[Dict]:
        """
        Busca um único concurso com proteção de circuit breaker.
        
        Args:
            num: Número do concurso
            cutoff_date: Data de corte para filtrar concursos
        
        Returns:
            Dados do concurso ou None se não encontrado
        """
        try:
            def make_request():
                response = requests.get(
                    f"{self.base_url}/{num}",
                    timeout=settings.circuit_breaker_timeout
                )
                response.raise_for_status()
                return response.json()
            
            # Usa circuit breaker para proteger a chamada
            draw_data = self.circuit_breaker.call(make_request)
            
            # Verifica se a data do concurso está dentro do período
            data_apuracao = draw_data.get(
                'dataApuracao',
                draw_data.get('data', draw_data.get('dataApuracaoStr', ''))
            )
            
            if data_apuracao:
                try:
                    # Tenta diferentes formatos de data
                    try:
                        draw_date = datetime.strptime(data_apuracao, '%d/%m/%Y')
                    except ValueError:
                        try:
                            draw_date = datetime.strptime(data_apuracao, '%Y-%m-%d')
                        except ValueError:
                            logger.warning(f"Could not parse date for draw {num}: {data_apuracao}")
                            return draw_data
                    
                    if draw_date >= cutoff_date:
                        return draw_data
                    else:
                        logger.debug(f"Draw {num} is before cutoff date")
                        return None
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing date for draw {num}: {e}")
                    return draw_data
            
            return None
            
        except CircuitBreakerOpenError:
            logger.warning("Circuit breaker is open, skipping request")
            raise
        except requests.RequestException as e:
            logger.error(f"Error fetching draw {num}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching draw {num}: {e}")
            return None
    
    def fetch_historical_data(self) -> List[Dict]:
        """
        Busca dados históricos da Mega-Sena dos últimos 2 anos.
        
        Returns:
            Lista de dicionários com dados dos concursos
        
        Raises:
            APIConnectionError: Se não conseguir conectar à API
        """
        logger.info("Fetching historical data from Mega-Sena API")
        
        try:
            # Busca o último concurso para saber quantos concursos existem
            def fetch_latest():
                response = requests.get(
                    self.base_url,
                    timeout=settings.circuit_breaker_timeout
                )
                response.raise_for_status()
                return response.json()
            
            last_draw = self.circuit_breaker.call(fetch_latest)
            
            cutoff_date = datetime.now() - timedelta(days=730)
            concurso_num = last_draw.get('numero', last_draw.get('numeroConcurso', 1))
            start_num = max(1, concurso_num - 180)
            
            logger.info(f"Fetching draws from {start_num} to {concurso_num}")
            
            all_draws = []
            
            # Usa ThreadPoolExecutor para buscar em paralelo
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_num = {
                    executor.submit(self._fetch_single_draw, num, cutoff_date): num 
                    for num in range(start_num, concurso_num + 1)
                }
                
                for future in as_completed(future_to_num):
                    try:
                        result = future.result()
                        if result:
                            all_draws.append(result)
                    except CircuitBreakerOpenError:
                        logger.warning("Circuit breaker opened during batch fetch")
                        break
                    except Exception as e:
                        logger.error(f"Error in future result: {e}")
            
            # Ordena por número do concurso para garantir consistência
            all_draws.sort(key=lambda x: x.get('numero', x.get('numeroConcurso', 0)))
            
            logger.info(f"Successfully fetched {len(all_draws)} draws")
            return all_draws
            
        except CircuitBreakerOpenError:
            raise APIConnectionError("Circuit breaker is open, API temporarily unavailable")
        except requests.RequestException as e:
            logger.error(f"API connection error: {e}")
            raise APIConnectionError(f"Failed to connect to Mega-Sena API: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error fetching historical data: {e}")
            raise DataProcessingError(f"Error fetching historical data: {str(e)}")
    
    def get_processed_data(self, force_refresh: bool = False) -> List[Dict]:
        """
        Obtém e processa os dados históricos com cache.
        
        Args:
            force_refresh: Se True, força atualização dos dados
        
        Returns:
            Lista processada com dados dos últimos 2 anos
        """
        cache_key = "mega_sena:processed_data"
        
        # Verifica cache se não for refresh forçado
        if not force_refresh:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.info("Returning processed data from cache")
                return cached_data
        
        logger.info("Processing fresh data from API")
        
        # Busca dados históricos
        raw_data = self.fetch_historical_data()
        
        # Normaliza os dados
        data = normalize_data(raw_data)
        
        # Filtra últimos 2 anos
        data_filtered = filter_last_two_years(data)
        
        # Atualiza cache
        self.cache.set(cache_key, data_filtered, ttl=settings.cache_ttl)
        logger.info(f"Cached {len(data_filtered)} processed draws")
        
        return data_filtered
    
    def get_estimate(self) -> Dict:
        """
        Gera estimativa de números mais prováveis.
        
        Returns:
            Dicionário com quadra, quina e sorte
        """
        logger.info("Generating number estimates")
        
        cache_key = "mega_sena:estimate"
        
        # Verifica cache
        cached_estimate = self.cache.get(cache_key)
        if cached_estimate is not None:
            logger.info("Returning estimate from cache")
            return cached_estimate
        
        # Busca dados processados
        data = self.get_processed_data()
        
        if not data:
            logger.warning("No data available for estimate")
            raise DataProcessingError("No historical data available")
        
        # Calcula frequências
        frequencies = calculate_frequencies(data)
        
        # Gera estimativas
        estimates = generate_estimates(frequencies)
        
        # Adiciona data atual
        estimates['data'] = datetime.now().strftime('%Y-%m-%d')
        
        # Cache por menos tempo (30 minutos)
        self.cache.set(cache_key, estimates, ttl=1800)
        
        logger.info("Estimate generated successfully")
        return estimates
    
    def get_draw_by_date(self, date: str) -> Optional[Dict]:
        """
        Busca os números sorteados em uma data específica.
        
        Args:
            date: Data no formato YYYY-MM-DD
        
        Returns:
            Dicionário com dados do concurso
        
        Raises:
            DrawNotFoundError: Se não encontrar concurso para a data
        """
        logger.info(f"Searching for draw on date: {date}")
        
        cache_key = f"mega_sena:draw:{date}"
        
        # Verifica cache
        cached_draw = self.cache.get(cache_key)
        if cached_draw is not None:
            logger.info(f"Returning draw from cache for date {date}")
            return cached_draw
        
        try:
            # Converte data para formato brasileiro
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            date_br = date_obj.strftime('%d/%m/%Y')
            
            # Busca dados históricos
            data = self.get_processed_data()
            
            if not data:
                logger.warning("No historical data available")
                raise DrawNotFoundError(date)
            
            # Busca concurso na data especificada
            for row in data:
                row_date = row.get('data', '')
                if row_date == date_br:
                    result = {
                        'data': date_br,
                        'numero_concurso': str(row['numero_concurso']),
                        'numeros': row['numeros']
                    }
                    # Cache permanente para dados históricos
                    self.cache.set(cache_key, result, ttl=86400)  # 24 horas
                    logger.info(f"Found draw for date {date}: concurso {result['numero_concurso']}")
                    return result
            
            # Se não encontrou nos dados em cache, tenta buscar diretamente
            logger.info(f"Draw not found in cache, searching API for date {date}")
            result = self._search_draw_in_api(date_br)
            
            if result:
                self.cache.set(cache_key, result, ttl=86400)
                return result
            
            logger.warning(f"No draw found for date {date}")
            raise DrawNotFoundError(date)
            
        except ValueError as e:
            logger.error(f"Invalid date format: {date}")
            raise DrawNotFoundError(date)
    
    def _search_draw_in_api(self, date_br: str) -> Optional[Dict]:
        """
        Busca um concurso diretamente na API por data.
        
        Args:
            date_br: Data no formato brasileiro (DD/MM/YYYY)
        
        Returns:
            Dados do concurso ou None
        """
        try:
            # Busca último concurso
            def fetch_latest():
                response = requests.get(self.base_url, timeout=10)
                response.raise_for_status()
                return response.json()
            
            last_draw = self.circuit_breaker.call(fetch_latest)
            concurso_num = last_draw.get('numero', last_draw.get('numeroConcurso', 1))
            
            # Busca em um range limitado (últimos 100 concursos)
            for num in range(max(1, concurso_num - 100), concurso_num + 1):
                try:
                    def fetch_draw():
                        response = requests.get(f"{self.base_url}/{num}", timeout=5)
                        response.raise_for_status()
                        return response.json()
                    
                    draw_data = self.circuit_breaker.call(fetch_draw)
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
                except (requests.RequestException, CircuitBreakerOpenError):
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching draw in API: {e}")
            return None
    
    def clear_cache(self):
        """Limpa todo o cache do serviço."""
        self.cache.clear()
        logger.info("Service cache cleared")
    
    def get_stats(self) -> Dict:
        """
        Retorna estatísticas do serviço.
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            "cache_type": self.cache.get_type(),
            "circuit_breaker": self.circuit_breaker.get_stats()
        }
