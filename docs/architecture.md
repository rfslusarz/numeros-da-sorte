# Arquitetura do Sistema

## Visão Geral

O sistema Números da Sorte é uma aplicação web full-stack que analisa dados históricos da Mega-Sena para gerar estimativas estatísticas de números mais prováveis.

## Diagrama de Arquitetura

```mermaid
graph TB
    subgraph "Cliente"
        Browser[Navegador Web]
    end
    
    subgraph "Frontend"
        Nginx[Nginx Server]
        HTML[HTML/CSS/JS]
    end
    
    subgraph "Backend"
        API[FastAPI Application]
        Routes[API Routes]
        Services[Business Logic]
        Utils[Utilities]
    end
    
    subgraph "Cache Layer"
        Redis[(Redis Cache)]
        Memory[Memory Cache]
    end
    
    subgraph "External"
        CaixaAPI[API Caixa - Mega-Sena]
    end
    
    Browser --> Nginx
    Nginx --> HTML
    HTML --> API
    API --> Routes
    Routes --> Services
    Services --> Utils
    Services --> Redis
    Services --> Memory
    Services --> CaixaAPI
    
    style Browser fill:#e1f5ff
    style API fill:#fff4e1
    style Redis fill:#ffe1e1
    style CaixaAPI fill:#e1ffe1
```

## Componentes Principais

### Frontend

**Tecnologias:**
- HTML5
- CSS3
- JavaScript (ES6+)
- Nginx (servidor web)

**Responsabilidades:**
- Interface do usuário
- Validação de entrada
- Comunicação com API
- Exibição de resultados

### Backend

**Tecnologias:**
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic

**Camadas:**

#### 1. API Layer (`app/routes/`)
- Define endpoints REST
- Validação de requisições
- Tratamento de erros
- Documentação automática (Swagger)

#### 2. Service Layer (`app/services/`)
- Lógica de negócio
- Integração com APIs externas
- Gerenciamento de cache
- Circuit breaker

#### 3. Utils Layer (`app/utils/`)
- Processamento de dados
- Logging estruturado
- Cache management
- Circuit breaker

### Cache

**Implementações:**
- **Redis**: Cache distribuído (produção)
- **Memory**: Cache em memória (desenvolvimento/fallback)

**Estratégia:**
- TTL configurável
- Invalidação automática
- Fallback transparente

### Proteções

#### Circuit Breaker
```mermaid
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: Threshold de falhas atingido
    Open --> HalfOpen: Timeout de recuperação
    HalfOpen --> Closed: Requisição bem-sucedida
    HalfOpen --> Open: Requisição falhou
```

**Estados:**
- **Closed**: Operação normal
- **Open**: Bloqueando requisições
- **Half-Open**: Testando recuperação

## Fluxo de Dados

### Geração de Estimativa

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant A as API
    participant S as Service
    participant C as Cache
    participant E as API Externa
    
    U->>F: Clica em "Gerar Estimativa"
    F->>A: GET /api/estimate
    A->>S: get_estimate()
    S->>C: Verifica cache
    alt Cache hit
        C-->>S: Retorna dados
    else Cache miss
        S->>E: Busca dados históricos
        E-->>S: Retorna concursos
        S->>S: Processa dados
        S->>C: Armazena em cache
    end
    S-->>A: Retorna estimativa
    A-->>F: JSON response
    F-->>U: Exibe números
```

### Busca por Data

```mermaid
sequenceDiagram
    participant U as Usuário
    participant F as Frontend
    participant A as API
    participant S as Service
    participant C as Cache
    participant E as API Externa
    
    U->>F: Insere data e busca
    F->>A: GET /api/draw/{date}
    A->>A: Valida formato
    A->>S: get_draw_by_date(date)
    S->>C: Verifica cache
    alt Cache hit
        C-->>S: Retorna concurso
    else Cache miss
        S->>S: Busca em dados processados
        alt Encontrado
            S->>C: Armazena em cache
        else Não encontrado
            S->>E: Busca na API
            E-->>S: Retorna concurso
            S->>C: Armazena em cache
        end
    end
    S-->>A: Retorna dados
    A-->>F: JSON response
    F-->>U: Exibe números
```

## Segurança

### Headers de Segurança
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security

### Rate Limiting
- Limite configurável por minuto
- Baseado em IP do cliente
- Resposta 429 quando excedido

### CORS
- Origens permitidas configuráveis
- Credenciais habilitadas
- Métodos e headers específicos

## Monitoramento

### Logging
- Formato JSON estruturado
- Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Contexto adicional em cada log
- Rotação automática

### Métricas
- Tempo de resposta por endpoint
- Taxa de erro
- Status do circuit breaker
- Tipo de cache em uso

### Health Checks
- `/health`: Status básico
- `/api/health`: Status detalhado com métricas
- `/api/stats`: Estatísticas do sistema

## Escalabilidade

### Horizontal
- Stateless application
- Cache compartilhado (Redis)
- Load balancer ready

### Vertical
- ThreadPoolExecutor para paralelização
- Async/await para I/O
- Cache para reduzir carga

## Deploy

### Docker
- Multi-stage builds
- Imagens otimizadas
- Health checks integrados
- Volumes para persistência

### Orquestração
- Docker Compose para desenvolvimento
- Kubernetes ready (futuro)

## Melhorias Futuras

1. **Autenticação/Autorização**
   - JWT tokens
   - Rate limiting por usuário

2. **Observabilidade**
   - Prometheus metrics
   - Grafana dashboards
   - Distributed tracing

3. **Performance**
   - CDN para frontend
   - Database para histórico
   - GraphQL API

4. **Features**
   - Análise de padrões
   - ML predictions
   - Notificações
