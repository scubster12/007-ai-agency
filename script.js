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

    // Google Maps Initialization
    function initMap() {
        const officeLocation = { lat: 37.7749, lng: -122.4194 };
        const map = new google.maps.Map(document.getElementById("map"), {
            zoom: 15,
            center: officeLocation,
            styles: [
                {
                    "featureType": "all",
                    "elementType": "geometry",
                    "stylers": [{"color": "#1a0505"}]
                },
                {
                    "featureType": "all",
                    "elementType": "labels.text.fill",
                    "stylers": [{"color": "#ffffff"}]
                },
                {
                    "featureType": "all",
                    "elementType": "labels.text.stroke",
                    "stylers": [{"color": "#000000"}]
                },
                {
                    "featureType": "road",
                    "elementType": "geometry",
                    "stylers": [{"color": "#e94560"}]
                }
            ]
        });

        const marker = new google.maps.Marker({
            position: officeLocation,
            map: map,
            title: "007 AI Agency LLC",
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: "#e94560",
                fillOpacity: 1,
                strokeColor: "#ffffff",
                strokeWeight: 2
            }
        });

        // Info Window
        const contentString = `
            <div class="map-info-window">
                <h3>007 AI Agency LLC</h3>
                <p>1234 AI Boulevard<br>San Francisco, CA 94105</p>
                <p><a href="tel:+15550070007">+1 (555) 007-0007</a></p>
            </div>
        `;

        const infoWindow = new google.maps.InfoWindow({
            content: contentString
        });

        marker.addListener("click", () => {
            infoWindow.open(map, marker);
        });
    }

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

    // Form Validation and Enhancement
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.querySelector('#contact-form');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Basic form validation
                const name = form.querySelector('#name').value;
                const email = form.querySelector('#email').value;
                const message = form.querySelector('#message').value;
                
                if (!name || !email || !message) {
                    showError('All fields are required');
                    return;
                }
                
                if (!isValidEmail(email)) {
                    showError('Please enter a valid email address');
                    return;
                }
                
                // If validation passes, submit the form
                submitForm(form);
            });
        }
    });

    function isValidEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        
        const form = document.querySelector('#contact-form');
        form.insertBefore(errorDiv, form.firstChild);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    }

    async function submitForm(form) {
        try {
            const formData = new FormData(form);
            const response = await fetch('https://api.007ai.agency/submit-form', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                showSuccess('Thank you for your message. We will contact you shortly.');
                form.reset();
            } else {
                throw new Error('Form submission failed');
            }
        } catch (error) {
            showError('There was an error submitting the form. Please try again.');
        }
    }

    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        
        const form = document.querySelector('#contact-form');
        form.insertBefore(successDiv, form.firstChild);
        
        setTimeout(() => {
            successDiv.remove();
        }, 5000);
    }

    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach((element) => {
        observer.observe(element);
    });
});
