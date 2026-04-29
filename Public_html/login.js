// Wait for page load
document.addEventListener('DOMContentLoaded', function() {

    // Get form elements
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');

    // Handle form submit
    loginForm.addEventListener('submit', function(event) {
        // Prevent page refresh
        event.preventDefault();

        // Reset error messages
        usernameError.textContent = '';
        passwordError.textContent = '';

        // Get input values
        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        // Validation flag
        let isValid = true;

        // Validate username
        if (username === '') {
            usernameError.textContent = 'Username is required';
            isValid = false;
        } else if (username.length < 3) {
            usernameError.textContent = 'Username must be at least 3 characters';
            isValid = false;
        }

        // Validate password
        if (password === '') {
            passwordError.textContent = 'Password is required';
            isValid = false;
        } else if (password.length < 6) {
            passwordError.textContent = 'Password must be at least 6 characters';
            isValid = false;
        }

        // If valid
        if (isValid) {
            // Send to server
            loginUser(username, password);
        }
    });

    // Clear error on typing
    usernameInput.addEventListener('input', function() {
        if (usernameError.textContent !== '') {
            usernameError.textContent = '';
        }
    });

    passwordInput.addEventListener('input', function() {
        if (passwordError.textContent !== '') {
            passwordError.textContent = '';
        }
    });

    // Send login request
    async function loginUser(username, password) {
        try {
            // Show loading state
            console.log('Sending login request...');

            // Send POST request
            const response = await fetch('http://localhost:3000/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            });

            // Parse response
            const data = await response.json();

            // Check if successful
            if (response.ok) {
                console.log('Login successful!');

                // Store auth token
                localStorage.setItem('authToken', data.token);

                // Store username
                localStorage.setItem('username', username);

                // Show success message
                alert('Login successful! Welcome, ' + username);

                // Clear the form
                loginForm.reset();

                // Redirect to dashboard or home page
                // window.location.href = 'dashboard.html';

            } else {
                console.log('Login failed:', data.message);

                // Show error
                usernameError.textContent = data.message || 'Invalid credentials';
            }

        } catch (error) {
            // Network error
            console.error('Error:', error);
            usernameError.textContent = 'Unable to connect to server. Please try again later.';
        }
    }

    // Check if logged in
    function checkIfLoggedIn() {
        const token = localStorage.getItem('authToken');
        if (token) {
            // User has token
            console.log('User is already logged in');
            // Optionally redirect to dashboard
            // window.location.href = 'dashboard.html';
        }
    }

    // Check on page load
    checkIfLoggedIn();
});

// Logout function
function logout() {
    // Remove auth data
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    console.log('User logged out');
    // Redirect to login page
    window.location.href = 'login.html';
}

// Make authenticated request
async function authenticatedRequest(url, options = {}) {
    // Get token
    const token = localStorage.getItem('authToken');

    if (!token) {
        console.log('No token found, user not logged in');
        window.location.href = 'login.html';
        return;
    }

    // Add token to headers
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token,
        ...options.headers
    };

    try {
        const response = await fetch(url, {
            ...options,
            headers: headers
        });

        // If token invalid
        if (response.status === 401) {
            console.log('Token expired or invalid');
            logout();
            return;
        }

        return response;
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}
