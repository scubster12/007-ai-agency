document.addEventListener('DOMContentLoaded', () => {
    // Load saved preferences
    loadPreferences();
    
    // Initialize form handlers
    initializeFormHandlers();
    
    // Load mock active sessions
    loadActiveSessions();
    
    // Update privacy dashboard
    updatePrivacyDashboard();
});

// Load saved preferences from localStorage
function loadPreferences() {
    const preferences = JSON.parse(localStorage.getItem('userPreferences')) || {
        marketingEmails: false,
        productUpdates: true,
        securityAlerts: true,
        analyticsConsent: false,
        personalization: false,
        cookiePreference: 'essential'
    };

    // Set form values
    Object.keys(preferences).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = preferences[key];
            } else if (element.type === 'radio') {
                const radio = document.querySelector(`input[name="cookiePreference"][value="${preferences[key]}"]`);
                if (radio) radio.checked = true;
            }
        }
    });
}

// Initialize all form handlers
function initializeFormHandlers() {
    const form = document.getElementById('preferencesForm');
    const exportBtn = document.getElementById('exportData');
    const deleteBtn = document.getElementById('deleteData');

    // Form submission
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        savePreferences();
    });

    // Export data
    exportBtn.addEventListener('click', exportUserData);

    // Delete data
    deleteBtn.addEventListener('click', requestDataDeletion);
}

// Save preferences to localStorage
function savePreferences() {
    const preferences = {
        marketingEmails: document.getElementById('marketingEmails').checked,
        productUpdates: document.getElementById('productUpdates').checked,
        securityAlerts: document.getElementById('securityAlerts').checked,
        analyticsConsent: document.getElementById('analyticsConsent').checked,
        personalization: document.getElementById('personalization').checked,
        cookiePreference: document.querySelector('input[name="cookiePreference"]:checked').value
    };

    localStorage.setItem('userPreferences', JSON.stringify(preferences));
    localStorage.setItem('lastConsentUpdate', new Date().toISOString());
    
    // Show success message
    showNotification('Preferences saved successfully');
    
    // Update dashboard
    updatePrivacyDashboard();
}

// Export user data
function exportUserData() {
    const userData = {
        preferences: JSON.parse(localStorage.getItem('userPreferences')),
        lastAccess: localStorage.getItem('lastAccess'),
        lastConsent: localStorage.getItem('lastConsentUpdate'),
        cookieConsent: localStorage.getItem('cookieConsent')
    };

    const dataStr = JSON.stringify(userData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = '007ai_user_data.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showNotification('Data export started');
}

// Request data deletion
function requestDataDeletion() {
    if (confirm('Are you sure you want to request deletion of all your data? This action cannot be undone.')) {
        // Here you would typically send a request to your backend
        localStorage.setItem('deletionRequest', new Date().toISOString());
        localStorage.setItem('pendingRequests', 
            (parseInt(localStorage.getItem('pendingRequests') || '0') + 1).toString()
        );
        
        showNotification('Data deletion request submitted');
        updatePrivacyDashboard();
    }
}

// Load mock active sessions
function loadActiveSessions() {
    const sessionsContainer = document.getElementById('activeSessions');
    const currentSession = {
        device: 'Current Browser',
        location: 'Unknown',
        lastActive: new Date().toLocaleString()
    };

    sessionsContainer.innerHTML = `
        <div class="session-card">
            <div class="session-info">
                <h4>${currentSession.device}</h4>
                <p>Location: ${currentSession.location}</p>
                <p>Last Active: ${currentSession.lastActive}</p>
            </div>
            <button class="session-action" onclick="terminateSession('current')">
                Terminate
            </button>
        </div>
    `;
}

// Update privacy dashboard
function updatePrivacyDashboard() {
    document.getElementById('lastAccess').textContent = 
        new Date(localStorage.getItem('lastAccess') || new Date()).toLocaleString();
    
    document.getElementById('lastConsent').textContent = 
        new Date(localStorage.getItem('lastConsentUpdate') || new Date()).toLocaleString();
    
    document.getElementById('pendingRequests').textContent = 
        localStorage.getItem('pendingRequests') || '0';
}

// Show notification
function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Terminate session
function terminateSession(sessionId) {
    if (confirm('Are you sure you want to terminate this session?')) {
        showNotification('Session terminated');
        // Here you would typically send a request to your backend
        // For demo purposes, we'll just reload the page
        window.location.reload();
    }
}
