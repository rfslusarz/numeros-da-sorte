/**
 * UI Module
 * Handles all DOM manipulation and user interface updates
 */

/**
 * Display numbers as balls
 */
export function displayNumbers(container, numbers) {
    if (!container) {
        console.error('Container element not found');
        return;
    }

    container.innerHTML = '';

    if (!numbers || numbers.length === 0) {
        container.innerHTML = '<p style="color: white; text-align: center;">Nenhum número disponível</p>';
        return;
    }

    numbers.forEach(num => {
        const ball = document.createElement('div');
        ball.className = 'number-ball';
        ball.textContent = num.toString().padStart(2, '0');
        ball.setAttribute('role', 'listitem');
        ball.setAttribute('aria-label', `Número ${num}`);
        container.appendChild(ball);
    });
}

/**
 * Show error message
 */
export function showError(message, duration = 5000) {
    const errorElement = document.getElementById('error');
    if (!errorElement) return;

    errorElement.textContent = message;
    errorElement.classList.remove('hidden');
    errorElement.setAttribute('role', 'alert');
    errorElement.setAttribute('aria-live', 'assertive');

    if (duration > 0) {
        setTimeout(() => hideError(), duration);
    }
}

/**
 * Hide error message
 */
export function hideError() {
    const errorElement = document.getElementById('error');
    if (!errorElement) return;

    errorElement.classList.add('hidden');
    errorElement.removeAttribute('role');
    errorElement.removeAttribute('aria-live');
}

/**
 * Show loading state
 */
export function showLoading(message = 'Carregando...') {
    const loadingElement = document.getElementById('loading');
    const generateBtn = document.getElementById('generate-btn');

    if (loadingElement) {
        loadingElement.textContent = message;
        loadingElement.classList.remove('hidden');
        loadingElement.setAttribute('role', 'status');
        loadingElement.setAttribute('aria-live', 'polite');
    }

    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.setAttribute('aria-busy', 'true');
    }
}

/**
 * Hide loading state
 */
export function hideLoading() {
    const loadingElement = document.getElementById('loading');
    const generateBtn = document.getElementById('generate-btn');

    if (loadingElement) {
        loadingElement.classList.add('hidden');
        loadingElement.textContent = '';
        loadingElement.removeAttribute('role');
        loadingElement.removeAttribute('aria-live');
    }

    if (generateBtn) {
        generateBtn.disabled = false;
        generateBtn.setAttribute('aria-busy', 'false');
    }
}

/**
 * Update current date display
 */
export function updateCurrentDate() {
    const currentDateElement = document.getElementById('current-date');
    if (!currentDateElement) return;

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

/**
 * Display draw result
 */
export function displayDrawResult(data) {
    const drawResult = document.getElementById('draw-result');
    if (!drawResult) return;

    let html = `<h4>Concurso ${data.numero_concurso}</h4>`;
    html += `<p style="color: #2c3e50; margin-bottom: 10px;">Data: ${data.data}</p>`;
    html += '<div class="numbers" role="list" aria-label="Números sorteados">';

    if (data.numeros && data.numeros.length > 0) {
        data.numeros.forEach(num => {
            html += `<div class="number-ball" role="listitem" aria-label="Número ${num}">${num.toString().padStart(2, '0')}</div>`;
        });
    }

    html += '</div>';
    drawResult.innerHTML = html;
}

/**
 * Clear all results
 */
export function clearResults() {
    const containers = [
        'quadra-result',
        'quina-result',
        'sorte-result',
        'draw-result'
    ];

    containers.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.innerHTML = '';
    });

    const dateInput = document.getElementById('date-input');
    if (dateInput) dateInput.value = '';

    hideError();
}

/**
 * Show notification
 */
export function showNotification(message, type = 'info') {
    // Create notification element if it doesn't exist
    let notification = document.getElementById('notification');

    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
        `;
        document.body.appendChild(notification);
    }

    // Set color based on type
    const colors = {
        info: '#3498db',
        success: '#27ae60',
        warning: '#f39c12',
        error: '#e74c3c'
    };

    notification.style.backgroundColor = colors[type] || colors.info;
    notification.textContent = message;
    notification.classList.remove('hidden');

    // Auto-hide after 3 seconds
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}
