document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Cookie Consent Management
    function initCookieConsent() {
        const banner = document.createElement('div');
        banner.className = 'cookie-banner';
        banner.innerHTML = `
            <div class="cookie-content">
                <p class="cookie-text">We use cookies to enhance your experience. By continuing to visit this site you agree to our use of cookies.</p>
                <div class="cookie-buttons">
                    <button class="cookie-btn cookie-accept">Accept</button>
                    <button class="cookie-btn cookie-decline">Decline</button>
                </div>
            </div>
        `;
        document.body.appendChild(banner);

        // Show banner if consent not given
        if (!localStorage.getItem('cookieConsent')) {
            setTimeout(() => banner.classList.add('show'), 1000);
        }

        // Handle consent choices
        banner.querySelector('.cookie-accept').addEventListener('click', () => {
            localStorage.setItem('cookieConsent', 'accepted');
            banner.classList.remove('show');
        });

        banner.querySelector('.cookie-decline').addEventListener('click', () => {
            localStorage.setItem('cookieConsent', 'declined');
            banner.classList.remove('show');
        });
    }

    // Form Validation
    function validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                showError(field, 'This field is required');
            } else {
                clearError(field);
            }
        });

        // Email validation
        const emailField = form.querySelector('input[type="email"]');
        if (emailField && emailField.value.trim()) {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(emailField.value)) {
                isValid = false;
                showError(emailField, 'Please enter a valid email address');
            }
        }

        // Consent validation
        const termsConsent = form.querySelector('#termsConsent');
        const dataProcessing = form.querySelector('#dataProcessing');
        
        if (termsConsent && !termsConsent.checked) {
            isValid = false;
            showError(termsConsent, 'You must accept the Terms and Conditions');
        }
        
        if (dataProcessing && !dataProcessing.checked) {
            isValid = false;
            showError(dataProcessing, 'You must accept the Data Processing agreement');
        }

        return isValid;
    }

    function showError(field, message) {
        clearError(field);
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.color = 'var(--accent-color)';
        errorDiv.style.fontSize = '0.8rem';
        errorDiv.style.marginTop = '0.3rem';
        field.parentNode.appendChild(errorDiv);
        field.style.borderColor = 'var(--accent-color)';
    }

    function clearError(field) {
        const errorDiv = field.parentNode.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.remove();
        }
        field.style.borderColor = '';
    }

    // Handle form submission
    function handleFormSubmission(event) {
        event.preventDefault();
        const form = event.target;

        if (validateForm(form)) {
            // Collect form data
            const formData = new FormData(form);
            const data = {
                name: formData.get('name'),
                email: formData.get('email'),
                company: formData.get('company'),
                useCase: formData.get('useCase'),
                message: formData.get('message'),
                marketingConsent: formData.get('marketingConsent') === 'on'
            };

            // Store opt-in preference
            localStorage.setItem('marketingOptIn', data.marketingConsent);

            // Here you would typically send the data to your server
            console.log('Form submitted:', data);
            
            // Show success message
            const successMsg = document.createElement('div');
            successMsg.className = 'success-message';
            successMsg.textContent = 'Thank you for your interest! We will contact you soon.';
            successMsg.style.color = '#4CAF50';
            successMsg.style.padding = '1rem';
            successMsg.style.marginTop = '1rem';
            successMsg.style.backgroundColor = 'rgba(76, 175, 80, 0.1)';
            successMsg.style.borderRadius = '4px';
            
            form.appendChild(successMsg);
            form.reset();

            // Remove success message after 5 seconds
            setTimeout(() => successMsg.remove(), 5000);
        }
    }

    // Form submission handler
    const contactForm = document.querySelector('.contact form');
    contactForm.addEventListener('submit', handleFormSubmission);

    // Add subtle animation to service cards
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'scale(1.05)';
            card.style.boxShadow = '0 10px 20px rgba(233, 69, 96, 0.2)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'scale(1)';
            card.style.boxShadow = 'none';
        });
    });

    // Navigation menu toggle for mobile (responsive)
    const navToggle = document.createElement('div');
    navToggle.classList.add('nav-toggle');
    navToggle.innerHTML = '&#9776;'; // Hamburger menu icon
    navToggle.style.display = 'none'; // Hidden by default

    // Add responsive styles
    const responsiveStyle = document.createElement('style');
    responsiveStyle.textContent = `
        @media screen and (max-width: 768px) {
            .nav-toggle {
                display: block;
                position: fixed;
                top: 15px;
                right: 15px;
                font-size: 30px;
                color: white;
                z-index: 1001;
                cursor: pointer;
            }

            nav ul {
                display: none;
                flex-direction: column;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(26, 26, 46, 0.95);
                justify-content: center;
                align-items: center;
            }

            nav ul.active {
                display: flex;
            }

            nav ul li {
                margin: 1rem 0;
            }
        }
    `;
    document.head.appendChild(responsiveStyle);

    // Add navigation toggle functionality
    navToggle.addEventListener('click', () => {
        const navMenu = document.querySelector('nav ul');
        navMenu.classList.toggle('active');
    });

    // Insert nav toggle into header
    document.querySelector('header').insertBefore(navToggle, document.querySelector('nav'));

    initCookieConsent();

    // Form handling
    document.getElementById('demoForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const form = this;
        const submitButton = form.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.innerHTML = 'Sending...';
        
        fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: {
                'Accept': 'application/json'
            },
        })
        .then(response => response.json())
        .then(data => {
            submitButton.innerHTML = 'Message Sent!';
            form.reset();
            setTimeout(() => {
                submitButton.innerHTML = originalButtonText;
            }, 3000);
        })
        .catch(error => {
            submitButton.innerHTML = 'Error! Try Again';
            console.error('Error:', error);
            setTimeout(() => {
                submitButton.innerHTML = originalButtonText;
            }, 3000);
        });
    });
});
