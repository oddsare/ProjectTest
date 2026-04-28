// Wait for the page to fully load before running code
document.addEventListener('DOMContentLoaded', function() {

    // Get references to HTML elements
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');

    // Listen for form submission
    loginForm.addEventListener('submit', function(event) {
        // Prevent the form from submitting normally (page refresh)
        event.preventDefault();

        // Reset error messages
        usernameError.textContent = '';
        passwordError.textContent = '';

        // Get the input values
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

        // If all validations pass
        if (isValid) {
            // Send credentials to server
            loginUser(username, password);
        }
    });

    // Real-time validation: Clear error when user starts typing
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

    // Function to send login credentials to server
    async function loginUser(username, password) {
        try {
            // Show loading state (you could disable button here)
            console.log('Sending login request...');

            // Send POST request to server
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

            // Parse the JSON response
            const data = await response.json();

            // Check if login was successful
            if (response.ok) {
                // Server returned success (status 200)
                console.log('Login successful!');

                // Store the JWT token in localStorage
                // This token proves the user is authenticated
                localStorage.setItem('authToken', data.token);

                // Optionally store username (not sensitive data)
                localStorage.setItem('username', username);

                // Show success message
                alert('Login successful! Welcome, ' + username);

                // Clear the form
                loginForm.reset();

                // Redirect to dashboard or home page
                // window.location.href = 'dashboard.html';

            } else {
                // Server returned error (401, 400, etc.)
                console.log('Login failed:', data.message);

                // Show error message from server
                usernameError.textContent = data.message || 'Invalid credentials';
            }

        } catch (error) {
            // Network error or server is down
            console.error('Error:', error);
            usernameError.textContent = 'Unable to connect to server. Please try again later.';
        }
    }

    // Helper function: Check if user is already logged in
    function checkIfLoggedIn() {
        const token = localStorage.getItem('authToken');
        if (token) {
            // User has a token, verify it's still valid
            // In production, you'd verify with server
            console.log('User is already logged in');
            // Optionally redirect to dashboard
            // window.location.href = 'dashboard.html';
        }
    }

    // Check on page load
    checkIfLoggedIn();
});

// Logout function (can be called from other pages)
function logout() {
    // Remove all stored authentication data
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    console.log('User logged out');
    // Redirect to login page
    window.location.href = 'login.html';
}

// Function to make authenticated requests to server
async function authenticatedRequest(url, options = {}) {
    // Get the stored token
    const token = localStorage.getItem('authToken');

    if (!token) {
        console.log('No token found, user not logged in');
        window.location.href = 'login.html';
        return;
    }

    // Add token to request headers
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

        // If token is invalid/expired, server returns 401
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
