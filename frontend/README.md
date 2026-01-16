# Frontend - Números da Sorte

Interface web simples e moderna para interagir com a API de estimativa da Mega-Sena.

## Estrutura

```
frontend/
├── index.html      # Estrutura HTML
├── styles.css      # Estilização
├── script.js       # Lógica JavaScript
└── README.md
```

## Execução

### Opção 1: Python HTTP Server
```bash
python -m http.server 8080
```

### Opção 2: Node.js HTTP Server
```bash
npx http-server -p 8080
```

### Opção 3: Live Server (VS Code)
1. Instale a extensão "Live Server" no VS Code
2. Clique com botão direito em `index.html`
3. Selecione "Open with Live Server"

### Opção 4: Abrir diretamente
Simplesmente abra o arquivo `index.html` no navegador (algumas funcionalidades podem não funcionar devido a políticas CORS).

## Acesso

Após iniciar o servidor, acesse:
```
http://localhost:8080
```

## Funcionalidades

- Exibição da data atual automaticamente
- Botão "Gerar" para obter estimativas
- Busca de concursos por data
- Exibição visual dos números em formato de bolas
- Feedback de carregamento e erros
- Design responsivo

## Configuração

Por padrão, o frontend está configurado para se conectar ao backend em:
```
http://localhost:8000
```

Para alterar, edite a constante `API_BASE_URL` no arquivo `script.js`.

## Requisitos

- Navegador moderno (Chrome, Firefox, Edge, Safari)
- Backend rodando e acessível na URL configurada
- Conexão com a internet (para buscar dados atualizados)
