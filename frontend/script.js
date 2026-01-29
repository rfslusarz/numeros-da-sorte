/**
 * Main Application Script
 * Coordinates all modules and handles user interactions
 */

import { apiClient } from './js/api.js';
import {
    displayNumbers,
    showError,
    hideError,
    showLoading,
    hideLoading,
    updateCurrentDate,
    displayDrawResult,
    clearResults,
    showNotification
} from './js/ui.js';
import { stateManager } from './js/state.js';
import {
    isValidDateFormat,
    isFutureDate,
    parseErrorMessage
} from './js/utils.js';

// DOM Elements
const elements = {
    generateBtn: document.getElementById('generate-btn'),
    clearBtn: document.getElementById('clear-btn'),
    searchBtn: document.getElementById('search-btn'),
    dateInput: document.getElementById('date-input'),
    quadraResult: document.getElementById('quadra-result'),
    quinaResult: document.getElementById('quina-result'),
    sorteResult: document.getElementById('sorte-result')
};

/**
 * Fetch and display estimate
 */
async function fetchEstimate() {
    const firstLoad = !stateManager.get('firstEstimateLoaded');
    const loadingMessage = firstLoad
        ? 'Carregando dados históricos (pode demorar alguns segundos na primeira vez)...'
        : 'Carregando...';

    showLoading(loadingMessage);
    hideError();

    try {
        const data = await apiClient.getEstimate();

        // Display results
        displayNumbers(elements.quadraResult, data.quadra || []);
        displayNumbers(elements.quinaResult, data.quina || []);
        displayNumbers(elements.sorteResult, data.sorte || []);

        // Update state
        stateManager.update({
            lastEstimate: data,
            lastEstimateDate: new Date().toISOString(),
            firstEstimateLoaded: true
        });

        if (stateManager.get('preferences').notifications) {
            showNotification('Estimativa gerada com sucesso!', 'success');
        }

    } catch (error) {
        console.error('Error fetching estimate:', error);
        const message = parseErrorMessage(error);
        showError(`Erro ao gerar estimativa: ${message}`);

        // Clear results on error
        elements.quadraResult.innerHTML = '';
        elements.quinaResult.innerHTML = '';
        elements.sorteResult.innerHTML = '';
    } finally {
        hideLoading();
    }
}

/**
 * Fetch and display draw by date
 */
async function fetchDrawByDate(date) {
    if (!date) {
        showError('Por favor, selecione uma data.');
        return;
    }

    // Validate date format
    if (!isValidDateFormat(date)) {
        showError('Formato de data inválido. Use YYYY-MM-DD');
        return;
    }

    // Check if date is in the future
    if (isFutureDate(date)) {
        showError('Não é possível buscar concursos futuros.');
        return;
    }

    hideError();
    const drawResult = document.getElementById('draw-result');
    drawResult.innerHTML = '<p style="color: #2c3e50;">Buscando...</p>';

    try {
        const data = await apiClient.getDrawByDate(date);

        // Display result
        displayDrawResult(data);

        // Add to recent searches
        stateManager.addRecentSearch(date);

        if (stateManager.get('preferences').notifications) {
            showNotification('Concurso encontrado!', 'success');
        }

    } catch (error) {
        console.error('Error fetching draw:', error);
        const message = parseErrorMessage(error);

        if (error.message && error.message.includes('404')) {
            drawResult.innerHTML = '<p style="color: #e74c3c;">Nenhum concurso encontrado para esta data.</p>';
        } else {
            drawResult.innerHTML = `<p style="color: #e74c3c;">Erro ao buscar concurso: ${message}</p>`;
        }
    }
}

/**
 * Check API health on startup
 */
async function checkAPIHealth() {
    try {
        await apiClient.healthCheck();
        console.log('API is healthy');
    } catch (error) {
        showError(
            'Não foi possível conectar à API. Verifique se o backend está rodando em http://localhost:8000',
            0  // Don't auto-hide
        );
    }
}

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Generate estimate button
    if (elements.generateBtn) {
        elements.generateBtn.addEventListener('click', fetchEstimate);
    }

    // Clear button
    if (elements.clearBtn) {
        elements.clearBtn.addEventListener('click', () => {
            clearResults();
            showNotification('Resultados limpos', 'info');
        });
    }

    // Search button
    if (elements.searchBtn) {
        elements.searchBtn.addEventListener('click', () => {
            const selectedDate = elements.dateInput.value;
            fetchDrawByDate(selectedDate);
        });
    }

    // Date input - Enter key
    if (elements.dateInput) {
        elements.dateInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                elements.searchBtn.click();
            }
        });

        // Set max date to today
        const today = new Date().toISOString().split('T')[0];
        elements.dateInput.setAttribute('max', today);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + G: Generate estimate
        if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
            e.preventDefault();
            elements.generateBtn.click();
        }

        // Ctrl/Cmd + L: Clear results
        if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
            e.preventDefault();
            elements.clearBtn.click();
        }
    });
}

/**
 * Initialize application
 */
function init() {
    console.log('Initializing Números da Sorte application...');

    // Update current date
    updateCurrentDate();

    // Initialize event listeners
    initializeEventListeners();

    // Check API health after a delay
    setTimeout(checkAPIHealth, 1000);

    // Load last estimate if available
    const lastEstimate = stateManager.get('lastEstimate');
    if (lastEstimate) {
        displayNumbers(elements.quadraResult, lastEstimate.quadra || []);
        displayNumbers(elements.quinaResult, lastEstimate.quina || []);
        displayNumbers(elements.sorteResult, lastEstimate.sorte || []);
    }

    console.log('Application initialized successfully');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
