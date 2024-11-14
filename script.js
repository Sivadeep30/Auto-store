
// Function to toggle the dropdown menu visibility
function toggleDropdown() {
    const dropdown = document.getElementById("loginDropdown");
    dropdown.style.display = dropdown.style.display === "none" ? "block" : "none";
}

// Function to hide the dropdown after selecting an option
function hideDropdown() {
    const dropdown = document.getElementById("loginDropdown");
    dropdown.style.display = "none";
}

// Attach the hideDropdown function to each link in the dropdown
document.querySelectorAll("#loginDropdown a").forEach(link => {
    link.addEventListener("click", hideDropdown);
});

// Function to toggle the navbar menu for mobile view
function toggleMenu() {
    const navLinks = document.querySelector(".nav-links");
    navLinks.classList.toggle("active");
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


    document.addEventListener("DOMContentLoaded", () => {
        const userEmail = localStorage.getItem("userEmail");

        if (userEmail) {
            // Hide login button and show profile button
            document.querySelector(".dropdown").style.display = "none";
            document.getElementById("profileMenu").style.display = "block";
        } else {
            // Show login button if user is not logged in
            document.querySelector(".dropdown").style.display = "block";
            document.getElementById("profileMenu").style.display = "none";
        }
    });

