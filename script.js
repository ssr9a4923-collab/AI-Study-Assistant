// AI Study Assistant - Custom JavaScript
// Enhanced interactivity and animations

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all interactive components
    initializeAnimations();
    initializeFormValidation();
    initializeTooltips();
    initializeThemeToggle();
    initializeScrollEffects();
    
    console.log('AI Study Assistant loaded successfully!');
});

// Initialize entrance animations
function initializeAnimations() {
    // Animate elements on page load
    const animatedElements = document.querySelectorAll('.card, .feature-card, .hero-section');
    
    animatedElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease-out';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Enhanced form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        
        inputs.forEach(input => {
            // Real-time validation
            input.addEventListener('input', function() {
                validateField(this);
            });
            
            // Add visual feedback
            input.addEventListener('focus', function() {
                this.parentNode.classList.add('field-focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentNode.classList.remove('field-focused');
                validateField(this);
            });
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    const isRequired = field.hasAttribute('required');
    
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Validate based on field type
    let isValid = true;
    
    if (isRequired && !value) {
        isValid = false;
    } else if (fieldType === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        isValid = emailRegex.test(value);
    } else if (fieldType === 'password' && value) {
        isValid = value.length >= 6;
    }
    
    // Apply validation styling
    if (value) {
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');
    }
    
    return isValid;
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Theme toggle functionality (optional enhancement)
function initializeThemeToggle() {
    // This could be expanded to include dark mode
    const themeToggle = document.querySelector('#theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
        });
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }
}

// Scroll effects
function initializeScrollEffects() {
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 100) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });
    
    // Parallax effect for hero section
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const parallax = heroSection.querySelector('::before');
            if (parallax) {
                parallax.style.transform = `translateY(${scrolled * 0.5}px)`;
            }
        });
    }
}

// Enhanced button interactions
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn') || e.target.closest('.btn')) {
        const button = e.target.classList.contains('btn') ? e.target : e.target.closest('.btn');
        
        // Create ripple effect
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
});

// Auto-save functionality for forms
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea');
        const formId = form.id || 'form_' + Math.random().toString(36).substr(2, 9);
        
        // Load saved data
        inputs.forEach(input => {
            const savedValue = localStorage.getItem(`autosave_${formId}_${input.name}`);
            if (savedValue && !input.value) {
                input.value = savedValue;
            }
        });
        
        // Save data on input
        inputs.forEach(input => {
            let saveTimeout;
            input.addEventListener('input', function() {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => {
                    localStorage.setItem(`autosave_${formId}_${this.name}`, this.value);
                    showAutoSaveIndicator();
                }, 1000);
            });
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            inputs.forEach(input => {
                localStorage.removeItem(`autosave_${formId}_${input.name}`);
            });
        });
    });
}

function showAutoSaveIndicator() {
    let indicator = document.querySelector('.autosave-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'autosave-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--success-green);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 1050;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        indicator.innerHTML = '<i class="bi bi-check-circle"></i> Auto-saved';
        document.body.appendChild(indicator);
    }
    
    indicator.style.opacity = '1';
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Enhanced loading states
function showLoadingState(element) {
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    element.disabled = true;
}

function hideLoadingState(element) {
    if (element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        delete element.dataset.originalContent;
    }
    element.disabled = false;
}

// Global error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // Could implement user-friendly error reporting here
});

// Network status monitoring
window.addEventListener('online', function() {
    showNetworkStatus('online');
});

window.addEventListener('offline', function() {
    showNetworkStatus('offline');
});

function showNetworkStatus(status) {
    const statusElement = document.createElement('div');
    statusElement.className = `alert alert-${status === 'online' ? 'success' : 'warning'} alert-dismissible fade show`;
    statusElement.style.cssText = 'position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 1060; min-width: 300px;';
    statusElement.innerHTML = `
        <i class="bi bi-${status === 'online' ? 'wifi' : 'wifi-off'}"></i>
        You are now ${status}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(statusElement);
    
    setTimeout(() => {
        statusElement.remove();
    }, 3000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm) {
            const submitButton = activeForm.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.click();
            }
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const modalInstance = bootstrap.Modal.getInstance(openModal);
            modalInstance.hide();
        }
    }
});

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            const timing = performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            console.log(`Page load time: ${loadTime}ms`);
            
            // Report slow loading (over 3 seconds)
            if (loadTime > 3000) {
                console.warn('Slow page load detected');
            }
        }, 0);
    });
}

// Initialize auto-save when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAutoSave);
} else {
    initializeAutoSave();
}