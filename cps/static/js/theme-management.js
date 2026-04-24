/**
 * Theme Management System for GetMyEbook
 * Handles Light, Dark, and System theme preferences.
 */

(function() {
    const THEME_STORAGE_KEY = 'getmyebook-theme';
    const THEMES = {
        LIGHT: 'light',
        DARK: 'dark',
        SYSTEM: 'system'
    };

    /**
     * Get the theme from local storage or default to system
     */
    function getSavedTheme() {
        return localStorage.getItem(THEME_STORAGE_KEY) || THEMES.SYSTEM;
    }

    /**
     * Determine which theme should be applied (e.g. if system, check OS)
     */
    function getCurrentEffectiveTheme() {
        const savedTheme = getSavedTheme();
        if (savedTheme === THEMES.SYSTEM) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? THEMES.DARK : THEMES.LIGHT;
        }
        return savedTheme;
    }

    /**
     * Apply the theme to the document
     */
    function applyTheme() {
        const effectiveTheme = getCurrentEffectiveTheme();
        document.documentElement.setAttribute('data-theme', effectiveTheme);
        
        // Update active class in dropdown if it exists
        const savedTheme = getSavedTheme();
        document.querySelectorAll('.theme-option').forEach(opt => {
            opt.classList.toggle('active', opt.dataset.theme === savedTheme);
        });

        // Update the icon in the toggle button
        const toggleIcon = document.querySelector('.theme-toggle-btn i');
        if (toggleIcon) {
            if (savedTheme === THEMES.DARK) {
                toggleIcon.className = 'fas fa-moon';
            } else if (savedTheme === THEMES.LIGHT) {
                toggleIcon.className = 'fas fa-sun';
            } else {
                toggleIcon.className = 'fas fa-desktop';
            }
        }
    }

    /**
     * Save theme preference
     */
    function setTheme(theme) {
        localStorage.setItem(THEME_STORAGE_KEY, theme);
        applyTheme();
        
        // Close dropdown
        const dropdown = document.getElementById('theme-dropdown');
        if (dropdown) dropdown.classList.remove('show');
    }

    /**
     * Toggle dropdown visibility
     */
    function toggleThemeDropdown(event) {
        if (event) event.stopPropagation();
        const dropdown = document.getElementById('theme-dropdown');
        if (dropdown) dropdown.classList.toggle('show');
    }

    // Public API
    window.themeManager = {
        setTheme,
        toggleThemeDropdown,
        init: function() {
            // Initial apply
            applyTheme();

            // Listen for system changes if system theme is selected
            window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
                if (getSavedTheme() === THEMES.SYSTEM) {
                    applyTheme();
                }
            });

            // Close dropdown when clicking outside
            window.addEventListener('click', (e) => {
                const dropdown = document.getElementById('theme-dropdown');
                const toggle = document.querySelector('.theme-toggle-btn');
                if (dropdown && dropdown.classList.contains('show')) {
                    if (!dropdown.contains(e.target) && !toggle.contains(e.target)) {
                        dropdown.classList.remove('show');
                    }
                }
            });
        }
    };

    // Run initialization
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', window.themeManager.init);
    } else {
        window.themeManager.init();
    }
})();
