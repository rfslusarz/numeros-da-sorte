# Números da Sorte - Mega-Sena

Sistema web para estimativa probabilística de números da Mega-Sena baseado em dados históricos reais dos últimos 2 anos.

## Estrutura do Projeto

```
numeros-da-sorte/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Aplicação FastAPI principal
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── api.py           # Endpoints da API
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── mega_sena_service.py  # Serviço de busca e processamento
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── data_processor.py     # Processamento de dados e cálculos
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── README.md
├── docs/
│   └── screenshot.png
└── README.md
```

## Requisitos

### Backend
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Frontend
- Navegador moderno (Chrome, Firefox, Edge, Safari)
- Servidor HTTP local (Live Server, Python http.server, etc.)

## Instalação e Execução

### Backend

1. Navegue até a pasta do backend:
```bash
cd backend
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

3. Ative o ambiente virtual:

No Windows:
```bash
venv\Scripts\activate
```

No Linux/Mac:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute o servidor:

**Opção 1 – usando o script de inicialização (recomendado no Windows)**
```bash
cd backend
start.bat
```

**Opção 2 – manualmente com Uvicorn**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O backend estará disponível em: `http://localhost:8000`

Documentação interativa da API: `http://localhost:8000/docs`

### Frontend

1. Navegue até a pasta do frontend:
```bash
cd frontend
```

2. Inicie um servidor HTTP local:

**Opção 1: Python (se já tiver Python instalado)**
```bash
python -m http.server 8080
```

**Opção 2: Node.js (se tiver Node.js instalado)**
```bash
npx http-server -p 8080
```

**Opção 3: Live Server (extensão do VS Code)**
- Instale a extensão "Live Server" no VS Code
- Clique com botão direito em `index.html` e selecione "Open with Live Server"

3. Acesse no navegador:
```text
http://localhost:8080
```

Se preferir, também é possível abrir diretamente o arquivo [`frontend/index.html`](frontend/index.html) no navegador, desde que o backend esteja rodando em `http://localhost:8000`.

## Exemplo de Tela

![Exemplo da aplicação](docs/screenshot.png)

## Endpoints da API

### GET /api/health
Verifica o status da API.

**Resposta:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T10:30:00"
}
```

### GET /api/estimate
Retorna estimativa de números mais prováveis baseada em dados históricos dos últimos 2 anos.

**Resposta:**
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

**Parâmetros:**
- `date`: Data no formato YYYY-MM-DD

**Resposta:**
```json
{
  "data": "15/01/2024",
  "numero_concurso": "2650",
  "numeros": [5, 12, 23, 45, 58, 60]
}
```

**Erro 404:**
```json
{
  "detail": "Nenhum concurso encontrado para a data 2024-01-15"
}
```

## Funcionalidades

### Backend
- Consumo de API pública da Caixa para dados da Mega-Sena
- Filtragem automática dos últimos 2 anos de concursos
- Cálculo de frequências e probabilidades
- Geração de estimativas para quadra, quina e sena
- Cache de dados para otimização
- Tratamento de erros robusto

### Frontend
- Interface moderna e responsiva
- Geração de estimativas com um clique
- Busca de concursos por data
- Exibição visual dos números em formato de bolas
- Feedback visual de carregamento e erros
- Design adaptável para diferentes tamanhos de tela

## Observações Importantes

### Como o sistema calcula os números

- O sistema busca os concursos anteriores da Mega-Sena na API pública da Caixa (últimos ~2 anos).
- Para cada concurso, pega os números sorteados e monta uma lista de resultados históricos.
- Em cima desses dados ele:
  - Conta quantas vezes cada número de 1 a 60 apareceu nesse período.
  - Usa essas contagens como uma medida simples de “força” ou frequência de cada número.
  - Ordena os números do mais frequente para o menos frequente.
  - Monta:
    - **Quadra**: 4 números mais frequentes.
    - **Quina**: 5 números mais frequentes.
    - **Sorte** (sena): 6 números mais frequentes.

Em outras palavras, ele faz uma **estimativa baseada apenas na frequência histórica**: números que mais saíram nos últimos concursos são os que ele sugere.

Do ponto de vista matemático, em cada novo sorteio da Mega-Sena todos os números de 1 a 60 continuam tendo a mesma chance teórica. O fato de um número ter saído mais vezes no passado **não garante** que ele terá mais chance no próximo sorteio. O sistema é uma ferramenta de **análise estatística e entretenimento**, não uma garantia de aumento de probabilidade de ganho.

### Aviso Legal
Este sistema fornece apenas **estimativas estatísticas** baseadas em dados históricos. Os resultados são calculados através de análise de frequência dos números sorteados nos últimos 2 anos.

**IMPORTANTE:**
- As estimativas não garantem ganhos
- A Mega-Sena é um jogo de sorte e os números são sorteados aleatoriamente
- Cada sorteio é independente e não há relação causal entre sorteios anteriores e futuros
- Este sistema é apenas uma ferramenta de entretenimento e análise estatística
- Use com responsabilidade e dentro de suas possibilidades financeiras

### Limitações
- Os dados são obtidos de APIs públicas e podem estar sujeitos a disponibilidade
- O sistema considera apenas os últimos 2 anos de concursos
- A análise é baseada em frequência simples, não em modelos preditivos complexos
- Requer conexão com a internet para buscar dados atualizados

> As datas e números apresentados nos exemplos de resposta acima são ilustrativos e servem apenas para demonstração do formato retornado pela API.

## Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e rápido
- **Uvicorn**: Servidor ASGI de alta performance
- **Requests**: Biblioteca para requisições HTTP
- **Python 3.11+**: Linguagem de programação

### Frontend
- **HTML5**: Estrutura da página
- **CSS3**: Estilização moderna com gradientes, animações e layout responsivo
- **JavaScript (Vanilla)**: Lógica e interação com a API
- **Fetch API**: Comunicação com o backend

## Desenvolvimento

### Estrutura de Código

O código está organizado em camadas:

- **Routes** (`app/routes/api.py`): Define os endpoints da API
- **Services** (`app/services/mega_sena_service.py`): Lógica de negócio e comunicação com APIs externas
- **Utils** (`app/utils/data_processor.py`): Funções auxiliares para processamento de dados

### Melhorias Futuras
- Implementar cache mais robusto (Redis)
- Adicionar testes unitários e de integração
- Melhorar tratamento de erros de rede
- Adicionar mais métricas estatísticas
- Implementar histórico de estimativas

## Suporte

Para problemas ou dúvidas:
1. Verifique se o backend está rodando na porta 8000
2. Verifique se o frontend está acessando a URL correta da API
3. Verifique a conexão com a internet (necessária para buscar dados)
4. Consulte os logs do backend para mais detalhes sobre erros


