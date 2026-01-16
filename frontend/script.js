// Configuração da API
const API_BASE_URL = 'http://localhost:8000/api';

// Elementos do DOM
const generateBtn = document.getElementById('generate-btn');
const clearBtn = document.getElementById('clear-btn');
const searchBtn = document.getElementById('search-btn');
const dateInput = document.getElementById('date-input');
const currentDateElement = document.getElementById('current-date');
const quadraResult = document.getElementById('quadra-result');
const quinaResult = document.getElementById('quina-result');
const sorteResult = document.getElementById('sorte-result');
const drawResult = document.getElementById('draw-result');
const loadingElement = document.getElementById('loading');
const errorElement = document.getElementById('error');
let firstEstimateLoaded = false;

// Atualiza data atual ao carregar a página
function updateCurrentDate() {
    const now = new Date();
    const options = { 
        day: '2-digit', 
        month: 'long', 
        year: 'numeric',
        weekday: 'long'
    };
    const formattedDate = now.toLocaleDateString('pt-BR', options);
    currentDateElement.textContent = formattedDate;
}

// Exibe números em formato de bolas
function displayNumbers(container, numbers) {
    container.innerHTML = '';
    
    if (!numbers || numbers.length === 0) {
        container.innerHTML = '<p style="color: white; text-align: center;">Nenhum número disponível</p>';
        return;
    }
    
    numbers.forEach(num => {
        const ball = document.createElement('div');
        ball.className = 'number-ball';
        ball.textContent = num.toString().padStart(2, '0');
        container.appendChild(ball);
    });
}

// Exibe mensagem de erro
function showError(message) {
    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
    setTimeout(() => {
        errorElement.classList.add('hidden');
    }, 5000);
}

// Oculta mensagem de erro
function hideError() {
    errorElement.classList.add('hidden');
}

// Exibe loading
function showLoading() {
    loadingElement.classList.remove('hidden');
    loadingElement.textContent = firstEstimateLoaded
        ? 'Carregando...'
        : 'Carregando dados históricos (pode demorar alguns segundos na primeira vez)...';
    generateBtn.disabled = true;
}

// Oculta loading
function hideLoading() {
    loadingElement.classList.add('hidden');
    loadingElement.textContent = '';
    generateBtn.disabled = false;
}

// Busca estimativa de números
async function fetchEstimate() {
    showLoading();
    hideError();
    
    try {
        const response = await fetch(`${API_BASE_URL}/estimate`);
        
        if (!response.ok) {
            throw new Error(`Erro ao buscar estimativa: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Exibe os resultados
        displayNumbers(quadraResult, data.quadra || []);
        displayNumbers(quinaResult, data.quina || []);
        displayNumbers(sorteResult, data.sorte || []);
        firstEstimateLoaded = true;
        
    } catch (error) {
        console.error('Erro:', error);
        showError(`Erro ao gerar estimativa: ${error.message}`);
        
        // Limpa resultados em caso de erro
        quadraResult.innerHTML = '';
        quinaResult.innerHTML = '';
        sorteResult.innerHTML = '';
    } finally {
        hideLoading();
    }
}

// Busca concurso por data
async function fetchDrawByDate(date) {
    if (!date) {
        showError('Por favor, selecione uma data.');
        return;
    }
    
    hideError();
    drawResult.innerHTML = '<p style="color: #2c3e50;">Buscando...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/draw/${date}`);
        
        if (!response.ok) {
            if (response.status === 404) {
                drawResult.innerHTML = '<p style="color: #e74c3c;">Nenhum concurso encontrado para esta data.</p>';
                return;
            }
            throw new Error(`Erro ao buscar concurso: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Exibe os resultados
        let html = `<h4>Concurso ${data.numero_concurso}</h4>`;
        html += `<p style="color: #2c3e50; margin-bottom: 10px;">Data: ${data.data}</p>`;
        html += '<div class="numbers">';
        
        if (data.numeros && data.numeros.length > 0) {
            data.numeros.forEach(num => {
                html += `<div class="number-ball">${num.toString().padStart(2, '0')}</div>`;
            });
        }
        
        html += '</div>';
        drawResult.innerHTML = html;
        
    } catch (error) {
        console.error('Erro:', error);
        drawResult.innerHTML = `<p style="color: #e74c3c;">Erro ao buscar concurso: ${error.message}</p>`;
    }
}

// Event listeners
generateBtn.addEventListener('click', fetchEstimate);

clearBtn.addEventListener('click', () => {
    quadraResult.innerHTML = '';
    quinaResult.innerHTML = '';
    sorteResult.innerHTML = '';
    drawResult.innerHTML = '';
    dateInput.value = '';
    hideError();
});

searchBtn.addEventListener('click', () => {
    const selectedDate = dateInput.value;
    if (selectedDate) {
        fetchDrawByDate(selectedDate);
    } else {
        showError('Por favor, selecione uma data.');
    }
});

// Permite buscar pressionando Enter no campo de data
dateInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchBtn.click();
    }
});

// Inicializa a página
updateCurrentDate();

// Verifica se a API está disponível ao carregar
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            showError('API não está disponível. Verifique se o backend está rodando.');
        }
    } catch (error) {
        showError('Não foi possível conectar à API. Verifique se o backend está rodando em http://localhost:8000');
    }
}

// Verifica saúde da API após um pequeno delay
setTimeout(checkAPIHealth, 1000);
