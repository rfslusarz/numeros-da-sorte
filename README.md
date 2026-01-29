# Números da Sorte - Mega-Sena

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![GitHub](https://img.shields.io/badge/GitHub-rfslusarz-181717?style=flat-square&logo=github)](https://github.com/rfslusarz/numeros-da-sorte)

## Descrição

Sistema web full-stack para análise estatística e estimativa probabilística de números da Mega-Sena, baseado em dados históricos reais dos últimos 2 anos obtidos através da API pública da Caixa Econômica Federal.

A aplicação consome dados de concursos anteriores, processa as frequências de cada número sorteado e gera sugestões de jogos (quadra, quina e sena) com base nos números mais recorrentes no período analisado.

## Objetivo do Projeto

Este projeto foi desenvolvido com propósito educacional e de portfólio, demonstrando competências em:

- Desenvolvimento de APIs RESTful com FastAPI
- Integração com APIs públicas externas
- Processamento e análise de dados históricos
- Desenvolvimento frontend com JavaScript Vanilla
- Arquitetura de software em camadas
- Boas práticas de organização de código

## Tecnologias Utilizadas

### Backend
- **Python 3.11+** - Linguagem de programação
- **FastAPI 0.104.1** - Framework web moderno e de alta performance
- **Uvicorn 0.24.0** - Servidor ASGI para aplicações assíncronas
- **Requests 2.31.0** - Biblioteca para requisições HTTP
- **Python-dateutil 2.8.2** - Manipulação avançada de datas

### Frontend
- **HTML5** - Estrutura semântica da aplicação
- **CSS3** - Estilização moderna com gradientes, animações e responsividade
- **JavaScript (Vanilla)** - Lógica de interação e comunicação com API
- **Fetch API** - Requisições assíncronas ao backend

## Estrutura do Projeto

```
numeros-da-sorte/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # Aplicação FastAPI principal
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── api.py                   # Definição dos endpoints REST
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── mega_sena_service.py     # Lógica de busca e processamento de dados
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── data_processor.py        # Funções de cálculo estatístico
│   ├── requirements.txt                  # Dependências Python
│   ├── start.bat                         # Script de inicialização (Windows)
│   └── start.sh                          # Script de inicialização (Linux/Mac)
├── frontend/
│   ├── index.html                        # Interface principal
│   ├── styles.css                        # Estilos da aplicação
│   └── script.js                         # Lógica de interação
├── docs/
│   └── screenshot.png                    # Captura de tela da aplicação
└── README.md
```

### Descrição das Camadas

- **Routes** - Define os endpoints da API REST e validação de requisições
- **Services** - Implementa a lógica de negócio e comunicação com APIs externas
- **Utils** - Funções auxiliares para processamento e análise de dados

## Como Executar o Projeto

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno
- Conexão com a internet (para consumo da API da Caixa)

### Instalação e Execução do Backend

1. Clone o repositório:
```bash
git clone https://github.com/rfslusarz/numeros-da-sorte.git
cd numeros-da-sorte
```

2. Navegue até a pasta do backend:
```bash
cd backend
```

3. Crie e ative um ambiente virtual:

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux/Mac:
```bash
python -m venv venv
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute o servidor:

Opção 1 - Script de inicialização (Windows):
```bash
start.bat
```

Opção 2 - Script de inicialização (Linux/Mac):
```bash
chmod +x start.sh
./start.sh
```

Opção 3 - Comando direto com Uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`

Documentação interativa da API (Swagger): `http://localhost:8000/docs`

### Instalação e Execução do Frontend

1. Navegue até a pasta do frontend:
```bash
cd frontend
```

2. Inicie um servidor HTTP local:

Opção 1 - Python:
```bash
python -m http.server 8080
```

Opção 2 - Node.js:
```bash
npx http-server -p 8080
```

Opção 3 - Live Server (VS Code):
- Instale a extensão "Live Server"
- Clique com botão direito em `index.html`
- Selecione "Open with Live Server"

3. Acesse a aplicação no navegador:
```
http://localhost:8080
```

Alternativamente, é possível abrir o arquivo `frontend/index.html` diretamente no navegador, desde que o backend esteja em execução.

## Funcionalidades

### Backend
- Consumo da API pública da Caixa Econômica Federal
- Filtragem automática dos concursos dos últimos 2 anos
- Cálculo de frequências e probabilidades estatísticas
- Geração de estimativas para quadra, quina e sena
- Sistema de cache para otimização de performance
- Tratamento robusto de erros e exceções
- Documentação automática com Swagger/OpenAPI

### Frontend
- Interface moderna e responsiva
- Geração de estimativas com um clique
- Busca de resultados de concursos por data
- Exibição visual dos números em formato de bolas
- Feedback visual de carregamento e tratamento de erros
- Design adaptável para diferentes dispositivos

## Endpoints da API

### GET /api/health
Verifica o status de saúde da API.

Resposta:
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00"
}
```

### GET /api/estimate
Retorna estimativa de números mais prováveis baseada em análise de frequência dos últimos 2 anos.

Resposta:
```json
{
  "data": "2024-01-15",
  "quadra": [5, 12, 23, 45],
  "quina": [5, 12, 23, 45, 58],
  "sorte": [5, 12, 23, 45, 58, 60]
}
```

### GET /api/draw/{date}
Retorna os números sorteados em uma data específica.

Parâmetros:
- `date` - Data no formato YYYY-MM-DD

Resposta de sucesso:
```json
{
  "data": "15/01/2024",
  "numero_concurso": "2650",
  "numeros": [5, 12, 23, 45, 58, 60]
}
```

Resposta de erro (404):
```json
{
  "detail": "Nenhum concurso encontrado para a data 2024-01-15"
}
```

## Metodologia de Cálculo

O sistema utiliza análise estatística de frequência para gerar as estimativas:

1. Busca todos os concursos realizados nos últimos 2 anos através da API pública da Caixa
2. Contabiliza a frequência de aparição de cada número (1 a 60) no período
3. Ordena os números do mais frequente para o menos frequente
4. Seleciona os números mais recorrentes para compor as sugestões:
   - **Quadra**: 4 números mais frequentes
   - **Quina**: 5 números mais frequentes
   - **Sorte (Sena)**: 6 números mais frequentes

## Aviso Legal

Este sistema fornece apenas estimativas estatísticas baseadas em dados históricos e foi desenvolvido exclusivamente para fins educacionais e de análise de dados.

**IMPORTANTE:**
- As estimativas não garantem ganhos ou aumentam probabilidades de acerto
- A Mega-Sena é um jogo de sorte com números sorteados aleatoriamente
- Cada sorteio é independente e não há relação causal entre sorteios anteriores e futuros
- Do ponto de vista matemático, todos os números de 1 a 60 possuem a mesma probabilidade em cada sorteio
- Este sistema é uma ferramenta de entretenimento e análise estatística
- Jogue com responsabilidade e dentro de suas possibilidades financeiras

### Limitações Técnicas
- Dependência de APIs públicas externas (sujeitas a disponibilidade)
- Análise limitada aos últimos 2 anos de concursos
- Método baseado em frequência simples, sem modelos preditivos complexos
- Requer conexão ativa com a internet

## Boas Práticas Aplicadas

- Arquitetura em camadas (Routes, Services, Utils)
- Separação de responsabilidades (SoC)
- Código modular e reutilizável
- Tratamento adequado de exceções
- Validação de dados de entrada
- Documentação automática de API
- Uso de ambiente virtual Python
- Organização clara de estrutura de pastas

## Exemplo de Tela

![Exemplo da aplicação](docs/screenshot.png)

## Observações

Este projeto faz parte do meu portfólio profissional e demonstra habilidades em desenvolvimento full-stack, integração de APIs, processamento de dados e criação de interfaces web responsivas.

Os dados e números apresentados nos exemplos são ilustrativos e servem apenas para demonstração do formato das respostas da API.


## Licença

Este projeto está disponível para uso educacional e de portfólio.
