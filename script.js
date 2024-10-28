// Toggle the mobile menu
function toggleMenu() {
    const navLinks = document.querySelector('.nav-links');
    navLinks.classList.toggle('active');
}

// Toggle dropdown menu for Login
function toggleDropdown() {
    const dropdown = document.getElementById('loginDropdown');
    dropdown.style.display = dropdown.style.display === 'none' || dropdown.style.display === '' ? 'block' : 'none';
}

// Load footer dynamically
fetch('footer.html')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.text();
    })
    .then(data => {
        document.getElementById('footer-container').innerHTML = data;
    })
    .catch(error => console.error('Error loading footer:', error));

// Basic form validation and submission handling
document.addEventListener('DOMContentLoaded', function () {
    const userLoginForm = document.getElementById('userLoginForm');
    const adminLoginForm = document.getElementById('adminLoginForm');

    if (userLoginForm) {
        userLoginForm.addEventListener('submit', function (event) {
            event.preventDefault();
            // Handle user login logic here
            alert('User login submitted!');
            // Redirect or handle login success
            // For example: window.location.href = 'profile.html';
        });
    }

    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', function (event) {
            event.preventDefault();
            // Handle admin login logic here
            alert('Admin login submitted!');
            // Redirect or handle login success
            // For example: window.location.href = 'admin_dashboard.html';
        });
    }
});
