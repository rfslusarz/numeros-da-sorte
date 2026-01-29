/**
 * API Client Module
 * Handles all communication with the backend API
 */

const API_CONFIG = {
    baseUrl: window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api'
        : '/api',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
};

/**
 * Sleep utility for retry logic
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Retry wrapper with exponential backoff
 */
async function retryWithBackoff(fn, attempts = API_CONFIG.retryAttempts) {
    for (let i = 0; i < attempts; i++) {
        try {
            return await fn();
        } catch (error) {
            if (i === attempts - 1) throw error;

            const delay = API_CONFIG.retryDelay * Math.pow(2, i);
            console.warn(`Request failed, retrying in ${delay}ms...`, error);
            await sleep(delay);
        }
    }
}

/**
 * Generic fetch wrapper with timeout and error handling
 */
async function fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), API_CONFIG.timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });

        clearTimeout(timeout);

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
        }

        return response.json();
    } catch (error) {
        clearTimeout(timeout);

        if (error.name === 'AbortError') {
            throw new Error('Request timeout - servidor não respondeu a tempo');
        }

        throw error;
    }
}

/**
 * API Client Class
 */
class APIClient {
    constructor(baseUrl = API_CONFIG.baseUrl) {
        this.baseUrl = baseUrl;
    }

    /**
     * Health check
     */
    async healthCheck() {
        return fetchWithTimeout(`${this.baseUrl}/health`);
    }

    /**
     * Get estimate
     */
    async getEstimate() {
        return retryWithBackoff(() =>
            fetchWithTimeout(`${this.baseUrl}/estimate`)
        );
    }

    /**
     * Get draw by date
     */
    async getDrawByDate(date) {
        return retryWithBackoff(() =>
            fetchWithTimeout(`${this.baseUrl}/draw/${date}`)
        );
    }

    /**
     * Get system stats
     */
    async getStats() {
        return fetchWithTimeout(`${this.baseUrl}/stats`);
    }

    /**
     * Clear cache
     */
    async clearCache() {
        return fetchWithTimeout(`${this.baseUrl}/cache/clear`, {
            method: 'POST'
        });
    }
}

// Export singleton instance
export const apiClient = new APIClient();
export { API_CONFIG };
