/**
 * State Management Module
 * Manages application state and localStorage persistence
 */

const STATE_KEY = 'megasena_state';

class StateManager {
    constructor() {
        this.state = this.loadState();
        this.listeners = [];
    }

    /**
     * Load state from localStorage
     */
    loadState() {
        try {
            const saved = localStorage.getItem(STATE_KEY);
            return saved ? JSON.parse(saved) : this.getDefaultState();
        } catch (error) {
            console.error('Error loading state:', error);
            return this.getDefaultState();
        }
    }

    /**
     * Get default state
     */
    getDefaultState() {
        return {
            lastEstimate: null,
            lastEstimateDate: null,
            recentSearches: [],
            preferences: {
                autoRefresh: false,
                notifications: true
            },
            firstEstimateLoaded: false
        };
    }

    /**
     * Save state to localStorage
     */
    saveState() {
        try {
            localStorage.setItem(STATE_KEY, JSON.stringify(this.state));
        } catch (error) {
            console.error('Error saving state:', error);
        }
    }

    /**
     * Get state value
     */
    get(key) {
        return this.state[key];
    }

    /**
     * Set state value
     */
    set(key, value) {
        this.state[key] = value;
        this.saveState();
        this.notifyListeners(key, value);
    }

    /**
     * Update nested state
     */
    update(updates) {
        Object.assign(this.state, updates);
        this.saveState();
        this.notifyListeners('*', this.state);
    }

    /**
     * Add state change listener
     */
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }

    /**
     * Notify listeners of state changes
     */
    notifyListeners(key, value) {
        this.listeners.forEach(listener => {
            try {
                listener(key, value);
            } catch (error) {
                console.error('Error in state listener:', error);
            }
        });
    }

    /**
     * Add recent search
     */
    addRecentSearch(date) {
        const searches = this.state.recentSearches || [];

        // Remove duplicates
        const filtered = searches.filter(s => s !== date);

        // Add to beginning
        filtered.unshift(date);

        // Keep only last 10
        this.state.recentSearches = filtered.slice(0, 10);
        this.saveState();
    }

    /**
     * Clear all data
     */
    clear() {
        this.state = this.getDefaultState();
        this.saveState();
        this.notifyListeners('*', this.state);
    }
}

// Export singleton instance
export const stateManager = new StateManager();
