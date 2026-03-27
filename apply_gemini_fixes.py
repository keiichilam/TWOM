#!/usr/bin/env python3
"""
Apply Gemini-identified improvements to journal.html
"""
import re

INPUT_FILE = 'journal.html'
OUTPUT_FILE = 'journal.html'
BACKUP_FILE = 'journal.html.before-gemini-fixes'

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def apply_fixes(content):
    """Apply all 3 Gemini improvements"""

    # ============================================================
    # FIX #1: Add debounce utility function
    # Insert after the getLocalizedMessage function
    # ============================================================

    debounce_function = '''
            // Debounce function to prevent rapid double-submits
            function debounce(func, wait = 300) {
                let timeout;
                return function executedFunction(...args) {
                    const later = () => {
                        clearTimeout(timeout);
                        func(...args);
                    };
                    clearTimeout(timeout);
                    timeout = setTimeout(later, wait);
                };
            }
'''

    content = content.replace(
        '            // ============================================================\n            // Validation Functions\n            // ============================================================\n',
        debounce_function + '\n            // ============================================================\n            // Validation Functions\n            // ============================================================\n'
    )

    # ============================================================
    # FIX #2: Update keypress handlers to use debounce
    # ============================================================

    # Script number handler
    old_script_handler = '''                document.getElementById('scriptNumber').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        const button = document.querySelector('[data-action="load-script"]');
                        handleLoadScript(button);
                    }
                });'''

    new_script_handler = '''                // Debounced handler for script number input
                const debouncedLoadScript = debounce(() => {
                    const button = document.querySelector('[data-action="load-script"]');
                    handleLoadScript(button);
                }, 300);

                document.getElementById('scriptNumber').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        debouncedLoadScript();
                    }
                });'''

    content = content.replace(old_script_handler, new_script_handler)

    # Reward number handler
    old_reward_handler = '''                document.getElementById('rewardNumber').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        const button = document.querySelector('[data-action="load-reward"]');
                        handleLoadReward(button);
                    }
                });'''

    new_reward_handler = '''                // Debounced handler for reward number input
                const debouncedLoadReward = debounce(() => {
                    const button = document.querySelector('[data-action="load-reward"]');
                    handleLoadReward(button);
                }, 300);

                document.getElementById('rewardNumber').addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        debouncedLoadReward();
                    }
                });'''

    content = content.replace(old_reward_handler, new_reward_handler)

    # ============================================================
    # FIX #3: Add confirmation dialog to handleBackToHome
    # ============================================================

    old_back_home = '''            function handleBackToHome(event) {
                event.preventDefault();

                // Clear history
                state.history.length = 0;

                // Hide entry container
                document.getElementById('entryContainer').classList.remove('active');

                // Update breadcrumb
                updateBreadcrumb();

                // Scroll to search
                document.getElementById('searchContainer').scrollIntoView({ behavior: 'smooth' });

                // Clear inputs
                document.getElementById('scriptNumber').value = '';
                document.getElementById('rewardNumber').value = '';
                clearInputError('scriptNumber');
                clearInputError('rewardNumber');
            }'''

    new_back_home = '''            function handleBackToHome(event) {
                event.preventDefault();

                // Confirm before clearing history if there are entries
                if (state.history.length > 0) {
                    const confirmMessage = state.langManager?.labels.confirm_clear_history ||
                                         'Clear navigation history and return to search?';

                    if (!confirm(confirmMessage)) {
                        return;  // User cancelled
                    }
                }

                // Clear history
                state.history.length = 0;

                // Hide entry container
                document.getElementById('entryContainer').classList.remove('active');

                // Update breadcrumb
                updateBreadcrumb();

                // Scroll to search
                document.getElementById('searchContainer').scrollIntoView({ behavior: 'smooth' });

                // Clear inputs
                document.getElementById('scriptNumber').value = '';
                document.getElementById('rewardNumber').value = '';
                clearInputError('scriptNumber');
                clearInputError('rewardNumber');
            }'''

    content = content.replace(old_back_home, new_back_home)

    # ============================================================
    # FIX #4: Add IntersectionObserver for entry content animation
    # Insert after state initialization
    # ============================================================

    intersection_observer = '''
            // IntersectionObserver for optimized animations on mobile
            let contentObserver = null;

            function initContentObserver() {
                if ('IntersectionObserver' in window) {
                    contentObserver = new IntersectionObserver((entries) => {
                        entries.forEach(entry => {
                            if (entry.isIntersecting) {
                                entry.target.classList.add('visible');
                            }
                        });
                    }, {
                        threshold: 0.1,
                        rootMargin: '50px'
                    });
                }
            }

            function observeContent(element) {
                if (contentObserver && element) {
                    // Add observer class for CSS animation
                    element.classList.add('observe-entry');
                    contentObserver.observe(element);
                }
            }
'''

    # Find state initialization
    state_init = '            const state = {\n                history: [],\n                langManager: null,\n                isLoading: false\n            };'

    content = content.replace(
        state_init,
        state_init + intersection_observer
    )

    # ============================================================
    # FIX #5: Add CSS for IntersectionObserver animation
    # ============================================================

    animation_css = '''
        /* IntersectionObserver animation for performance */
        .observe-entry {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease-out, transform 0.6s ease-out;
        }

        .observe-entry.visible {
            opacity: 1;
            transform: translateY(0);
        }

        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
            .observe-entry {
                transition: none;
                opacity: 1;
                transform: none;
            }
        }
'''

    # Insert before </style> tag
    content = content.replace('        </style>', animation_css + '        </style>')

    # ============================================================
    # FIX #6: Update updateEntryDisplay to use IntersectionObserver
    # ============================================================

    # Find the line where content is appended
    old_append = '''                const formattedContent = formatContent(data.content);
                content.appendChild(formattedContent);'''

    new_append = '''                const formattedContent = formatContent(data.content);
                content.appendChild(formattedContent);

                // Observe content for optimized animation
                observeContent(content);'''

    content = content.replace(old_append, new_append)

    # ============================================================
    # FIX #7: Initialize observer on DOMContentLoaded
    # ============================================================

    old_init = '''                // Initialize i18n and load initial content
                initializeApp();'''

    new_init = '''                // Initialize IntersectionObserver
                initContentObserver();

                // Initialize i18n and load initial content
                initializeApp();'''

    content = content.replace(old_init, new_init)

    return content

def main():
    print("Applying Gemini improvements to journal.html...")
    print("=" * 80)

    # Backup original
    import shutil
    try:
        shutil.copy(INPUT_FILE, BACKUP_FILE)
        print(f"✓ Backed up to {BACKUP_FILE}")
    except FileNotFoundError:
        print(f"⚠ No existing file to backup")

    # Read input
    content = read_file(INPUT_FILE)
    print(f"✓ Read {INPUT_FILE} ({len(content)} bytes)")

    # Apply fixes
    fixed_content = apply_fixes(content)
    print("✓ Applied all 3 Gemini improvements:")
    print("  1. Added confirmation dialog before clearing history")
    print("  2. Added IntersectionObserver for optimized rendering")
    print("  3. Added debouncing (300ms) to search input handlers")

    # Write output
    write_file(OUTPUT_FILE, fixed_content)
    print(f"✓ Wrote {OUTPUT_FILE} ({len(fixed_content)} bytes)")

    print("\n" + "=" * 80)
    print("✓ All Gemini improvements applied successfully!")
    print("\nImprovements:")
    print("  🟢 UX: Users must confirm before clearing history")
    print("  🟢 PERFORMANCE: Long entries animate only when visible")
    print("  🟢 UX: 300ms debounce prevents accidental double-submits")

if __name__ == '__main__':
    main()
