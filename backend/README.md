# Backend - API Mega-Sena

API REST desenvolvida em Python com FastAPI para estimativa probabilística de números da Mega-Sena.

## Estrutura

```
backend/
├── app/
│   ├── main.py                    # Aplicação FastAPI principal
│   ├── routes/
│   │   └── api.py                 # Endpoints da API
│   ├── services/
│   │   └── mega_sena_service.py   # Serviço de busca e processamento
│   └── utils/
│       └── data_processor.py      # Processamento de dados e cálculos
├── requirements.txt
└── README.md
```

## Instalação

1. Certifique-se de ter Python 3.11 ou superior instalado.

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Execução

Para rodar o servidor de desenvolvimento:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O servidor estará disponível em:
- API: `http://localhost:8000`
- Documentação interativa: `http://localhost:8000/docs`
- Documentação alternativa: `http://localhost:8000/redoc`

## Endpoints

### GET /api/health
Verifica o status da API.

### GET /api/estimate
Retorna estimativa de números mais prováveis baseada em dados históricos dos últimos 2 anos.

### GET /api/draw/{date}
Retorna os números sorteados em uma data específica (formato: YYYY-MM-DD).

## Funcionalidades

- Consumo de API pública da Caixa para dados da Mega-Sena
- Filtragem automática dos últimos 2 anos de concursos
- Cálculo de frequências e probabilidades
- Geração de estimativas para quadra, quina e sena
- Cache de dados para otimização (válido por 1 hora)
- Tratamento robusto de erros

## Dependências

- **fastapi**: Framework web moderno
- **uvicorn**: Servidor ASGI
- **requests**: Requisições HTTP
- **pandas**: Processamento de dados
- **python-dateutil**: Manipulação de datas

## Notas Técnicas

- Os dados são buscados da API oficial da Caixa
- O cache é atualizado automaticamente a cada hora
- A filtragem por data considera automaticamente os últimos 2 anos
- Os números são ordenados por frequência e depois ordenados em ordem crescente para exibição
