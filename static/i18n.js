/**
 * Language Manager for TWOM War Journal
 * Handles UI translations and language switching
 * Version 2.0 - Improved error handling and loading states
 */

// Define API_BASE for use in this module
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : `http://${window.location.hostname}:5000`;

class LanguageManager {
    constructor() {
        this.currentLang = this.detectLanguage();
        this.labels = {};
        this.onLanguageChangeCallbacks = [];
        this.fallbackLabels = {
            'title': 'War Journal',
            'subtitle': 'This War of Mine',
            'loading_text': 'Loading entry...',
            'error_title': 'Error'
        };
    }

    /**
     * Detect user's preferred language
     */
    detectLanguage() {
        // Check localStorage first
        const saved = localStorage.getItem('twom_lang');
        if (saved && this.isValidLanguage(saved)) {
            return saved;
        }

        // Check browser language
        const browserLang = navigator.language || navigator.userLanguage;

        // Map browser language codes to our supported languages
        if (browserLang.startsWith('zh')) {
            return 'zh-hk';
        }

        return 'en'; // Default
    }

    /**
     * Validate language code
     */
    isValidLanguage(lang) {
        return lang === 'en' || lang === 'zh-hk';
    }

    /**
     * Load UI labels from the API with improved error handling
     */
    async loadTranslations() {
        // Show loading indicator
        document.body.classList.add('loading-translations');

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

            const response = await fetch(
                `${API_BASE}/api/ui-labels?lang=${this.currentLang}`,
                { signal: controller.signal }
            );

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.labels = data.labels;

            return true;
        } catch (error) {
            console.error('Failed to load translations:', error);

            // Fallback to English if API fails and we're not already trying English
            if (this.currentLang !== 'en') {
                console.warn('Falling back to English translations');
                this.currentLang = 'en';
                return this.loadTranslations();
            }

            // If English also fails, use hardcoded fallbacks
            console.warn('Using fallback labels');
            this.labels = { ...this.fallbackLabels };

            return false;
        } finally {
            document.body.classList.remove('loading-translations');
        }
    }

    /**
     * Get current language
     */
    getCurrentLang() {
        return this.currentLang;
    }

    /**
     * Set language and update UI
     */
    async setLanguage(lang) {
        if (!this.isValidLanguage(lang)) {
            console.error('Invalid language:', lang);
            return;
        }

        this.currentLang = lang;
        localStorage.setItem('twom_lang', lang);

        // Reload translations
        await this.loadTranslations();

        // Update UI
        this.updateUI();

        // Update language switcher buttons
        this.updateLanguageSwitcher();

        // Notify callbacks
        this.onLanguageChangeCallbacks.forEach(callback => callback(lang));
    }

    /**
     * Update all UI elements with data-i18n attributes
     */
    updateUI() {
        document.documentElement.lang = this.currentLang;

        const missingTranslations = [];

        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            const text = this.labels[key];

            if (!text) {
                console.warn(`Translation missing for key: ${key}`);
                missingTranslations.push(key);

                // Keep existing text as fallback
                return;
            }

            if (el.placeholder !== undefined) {
                el.placeholder = text;
            } else {
                el.textContent = text;
            }
        });

        // Report missing translations in dev mode
        if (missingTranslations.length > 0 && window.location.hostname === 'localhost') {
            console.table(missingTranslations.map(key => ({ key, status: 'missing' })));
        }
    }

    /**
     * Update language switcher button states
     */
    updateLanguageSwitcher() {
        document.querySelectorAll('.lang-btn').forEach(btn => {
            if (btn.dataset.lang === this.currentLang) {
                btn.classList.add('active');
                btn.setAttribute('aria-pressed', 'true');
            } else {
                btn.classList.remove('active');
                btn.setAttribute('aria-pressed', 'false');
            }
        });
    }

    /**
     * Register a callback for language changes
     */
    onLanguageChange(callback) {
        this.onLanguageChangeCallbacks.push(callback);
    }

    /**
     * Initialize the language manager
     */
    async initialize() {
        const success = await this.loadTranslations();

        if (!success) {
            console.warn('Translations loaded with fallbacks');
        }

        this.updateUI();
        this.updateLanguageSwitcher();

        return success;
    }
}

// Export for use in main script
window.LanguageManager = LanguageManager;
