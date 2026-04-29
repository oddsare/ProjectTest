// Shared authentication utilities

// Auto-detect API base
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? '' // Local Flask dev server
    : window.location.hostname.includes('railway.app')
    ? '' // Railway deployment (root path)
    : '/~group4sp26'; // Turing server

// Show/hide loading state
function setLoading(isLoading) {
    const submitBtn = document.querySelector('button[type="submit"]');
    if (!submitBtn) return;

    const btnText = submitBtn.querySelector('.btn-text');
    const spinner = submitBtn.querySelector('.spinner');

    if (isLoading) {
        submitBtn.disabled = true;
        if (btnText) btnText.classList.add('hidden');
        if (spinner) spinner.classList.remove('hidden');
    } else {
        submitBtn.disabled = false;
        if (btnText) btnText.classList.remove('hidden');
        if (spinner) spinner.classList.add('hidden');
    }
}

// Show alert
function showAlert(message, type = 'info') {
    const alert = document.getElementById('alert');
    if (!alert) return;

    alert.textContent = message;
    alert.className = `alert ${type}`;
    alert.classList.remove('hidden');

    // Auto-hide after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            hideAlert();
        }, 5000);
    }
}

// Hide alert
function hideAlert() {
    const alert = document.getElementById('alert');
    if (alert) {
        alert.classList.add('hidden');
    }
}

// Check if authenticated
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/api/profile`, {
            credentials: 'include'
        });

        if (!response.ok) {
            // Not logged in
            if (window.location.pathname.includes('dashboard') ||
                window.location.pathname.includes('profile')) {
                window.location.href = 'login_improved.html';
            }
            return false;
        }

        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        return false;
    }
}

// Logout function
async function logout() {
    try {
        const response = await fetch(`${API_BASE}/api/logout`, {
            method: 'POST',
            credentials: 'include'
        });

        if (response.ok) {
            localStorage.removeItem('username');
            window.location.href = 'login_improved.html';
        }
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Format date
function formatDate(date) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-US', options);
}

// Format relative time
function formatRelativeTime(date) {
    const now = new Date();
    const diff = now - new Date(date);
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
}

// Initialize tooltips
function initTooltips() {
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Initialize global features
    initTooltips();

    // Add global keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Escape key to hide alerts
        if (e.key === 'Escape') {
            hideAlert();
        }
    });
});
