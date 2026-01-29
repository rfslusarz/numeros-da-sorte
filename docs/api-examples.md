# Exemplos de Uso da API

Este documento fornece exemplos práticos de como usar a API do Números da Sorte.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

Verifica o status da API.

**Request:**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00.123456",
  "version": "1.0.0",
  "cache_type": "redis"
}
```

**cURL:**
```bash
curl http://localhost:8000/api/health
```

---

### 2. Gerar Estimativa

Retorna estimativa de números mais prováveis baseada em análise histórica.

**Request:**
```http
GET /api/estimate
```

**Response:**
```json
{
  "data": "2024-01-15",
  "quadra": [5, 12, 23, 45],
  "quina": [5, 12, 23, 45, 58],
  "sorte": [5, 12, 23, 45, 58, 60]
}
```

**cURL:**
```bash
curl http://localhost:8000/api/estimate
```

**Python:**
```python
import requests

response = requests.get("http://localhost:8000/api/estimate")
data = response.json()

print(f"Quadra: {data['quadra']}")
print(f"Quina: {data['quina']}")
print(f"Sorte: {data['sorte']}")
```

**JavaScript:**
```javascript
fetch('http://localhost:8000/api/estimate')
  .then(response => response.json())
  .then(data => {
    console.log('Quadra:', data.quadra);
    console.log('Quina:', data.quina);
    console.log('Sorte:', data.sorte);
  });
```

---

### 3. Buscar Concurso por Data

Retorna os números sorteados em uma data específica.

**Request:**
```http
GET /api/draw/{date}
```

**Parâmetros:**
- `date` (path): Data no formato YYYY-MM-DD

**Response (Sucesso):**
```json
{
  "data": "15/01/2024",
  "numero_concurso": "2650",
  "numeros": [5, 12, 23, 45, 58, 60]
}
```

**Response (Não Encontrado):**
```json
{
  "detail": "Nenhum concurso encontrado para a data 2024-01-15",
  "error_code": "DRAW_NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**cURL:**
```bash
curl http://localhost:8000/api/draw/2024-01-15
```

**Python:**
```python
import requests
from datetime import datetime

date = "2024-01-15"
response = requests.get(f"http://localhost:8000/api/draw/{date}")

if response.status_code == 200:
    data = response.json()
    print(f"Concurso {data['numero_concurso']}")
    print(f"Data: {data['data']}")
    print(f"Números: {data['numeros']}")
elif response.status_code == 404:
    print("Concurso não encontrado")
```

---

### 4. Estatísticas do Sistema

Retorna estatísticas e métricas do sistema.

**Request:**
```http
GET /api/stats
```

**Response:**
```json
{
  "cache_type": "redis",
  "circuit_breaker": {
    "state": "closed",
    "failure_count": 0,
    "failure_threshold": 5,
    "last_failure_time": null
  },
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**cURL:**
```bash
curl http://localhost:8000/api/stats
```

---

### 5. Limpar Cache

Limpa todo o cache do sistema.

**Request:**
```http
POST /api/cache/clear
```

**Response:**
```json
{
  "message": "Cache limpo com sucesso",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/cache/clear
```

---

## Tratamento de Erros

### Erro de Validação (422)

```json
{
  "detail": [
    {
      "loc": ["body", "quadra"],
      "msg": "Quadra deve ter exatamente 4 números",
      "type": "value_error"
    }
  ],
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### Data Inválida (400)

```json
{
  "detail": "Formato de data inválido. Use YYYY-MM-DD",
  "error_code": "INVALID_DATE",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### Concurso Não Encontrado (404)

```json
{
  "detail": "Nenhum concurso encontrado para a data 2024-01-15",
  "error_code": "DRAW_NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### Erro Interno (500)

```json
{
  "detail": "Erro ao processar dados",
  "error_code": "DATA_PROCESSING_ERROR",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### Serviço Indisponível (503)

```json
{
  "detail": "Serviço temporariamente indisponível. Tente novamente em alguns instantes.",
  "error_code": "CIRCUIT_BREAKER_OPEN",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

---

## Rate Limiting

A API possui rate limiting configurado. Se você exceder o limite:

**Response (429):**
```json
{
  "error": "Rate limit exceeded: 60 per 1 minute"
}
```

Limite padrão: 60 requisições por minuto por IP.

---

## Documentação Interativa

Acesse a documentação interativa (Swagger UI):

```
http://localhost:8000/docs
```

Ou a documentação alternativa (ReDoc):

```
http://localhost:8000/redoc
```

---

## Exemplo Completo: Aplicação Python

```python
import requests
from datetime import datetime, timedelta

class MegaSenaClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Verifica status da API."""
        response = requests.get(f"{self.base_url}/api/health")
        return response.json()
    
    def get_estimate(self):
        """Obtém estimativa de números."""
        response = requests.get(f"{self.base_url}/api/estimate")
        response.raise_for_status()
        return response.json()
    
    def get_draw_by_date(self, date):
        """Busca concurso por data (YYYY-MM-DD)."""
        response = requests.get(f"{self.base_url}/api/draw/{date}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    def get_stats(self):
        """Obtém estatísticas do sistema."""
        response = requests.get(f"{self.base_url}/api/stats")
        return response.json()

# Uso
client = MegaSenaClient()

# Verifica saúde
health = client.health_check()
print(f"API Status: {health['status']}")

# Gera estimativa
estimate = client.get_estimate()
print(f"Sorte: {estimate['sorte']}")

# Busca concurso
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
draw = client.get_draw_by_date(yesterday)
if draw:
    print(f"Concurso {draw['numero_concurso']}: {draw['numeros']}")
else:
    print("Concurso não encontrado")
```

---

## Exemplo Completo: Aplicação JavaScript

```javascript
class MegaSenaClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/api/health`);
    return response.json();
  }

  async getEstimate() {
    const response = await fetch(`${this.baseUrl}/api/estimate`);
    if (!response.ok) throw new Error('Failed to get estimate');
    return response.json();
  }

  async getDrawByDate(date) {
    const response = await fetch(`${this.baseUrl}/api/draw/${date}`);
    if (response.status === 404) return null;
    if (!response.ok) throw new Error('Failed to get draw');
    return response.json();
  }

  async getStats() {
    const response = await fetch(`${this.baseUrl}/api/stats`);
    return response.json();
  }
}

// Uso
const client = new MegaSenaClient();

// Verifica saúde
client.healthCheck()
  .then(health => console.log('API Status:', health.status));

// Gera estimativa
client.getEstimate()
  .then(estimate => console.log('Sorte:', estimate.sorte));

// Busca concurso
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);
const dateStr = yesterday.toISOString().split('T')[0];

client.getDrawByDate(dateStr)
  .then(draw => {
    if (draw) {
      console.log(`Concurso ${draw.numero_concurso}:`, draw.numeros);
    } else {
      console.log('Concurso não encontrado');
    }
  });
```
