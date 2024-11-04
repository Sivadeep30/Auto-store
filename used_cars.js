document.addEventListener("DOMContentLoaded", function () {
    const addCarBtn = document.getElementById("addCarBtn");
    const addCarModal = document.getElementById("addCarModal");
    const closeModal = document.getElementById("closeModal");
    const addUsedCarForm = document.getElementById("addUsedCarForm");
    const usedCarsContainer = document.getElementById("usedCarsContainer");

    // Load all used cars on page load
    fetchUsedCars();

    // Show modal form
    addCarBtn.onclick = () => addCarModal.style.display = "block";

    // Close modal form
    closeModal.onclick = () => addCarModal.style.display = "none";

    // Handle form submission to add a new car
    addUsedCarForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(addUsedCarForm);  // Automatically includes all form fields
        formData.append("image", document.getElementById("image").files[0]); // Append the image file

        fetch("http://127.0.0.1:5000/add-used-car", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "Car added successfully!") {
                fetchUsedCars(); // Refresh display
                addCarModal.style.display = "none"; // Close modal
                addUsedCarForm.reset(); // Clear form
            }
        })
        .catch(error => console.error("Error adding car:", error));
    });

    // Fetch all used cars from the server
    function fetchUsedCars() {
        fetch("http://127.0.0.1:5000/get-used-cars")
        .then(response => response.json())
        .then(data => {
            populateUsedCars(data); // Pass the fetched data to populate the UI
        })
        .catch(error => console.error("Error fetching used cars:", error));
    }

    // Display car cards
    function populateUsedCars(cars) {
        usedCarsContainer.innerHTML = "";
        cars.forEach((car, index) => {
            const carCard = document.createElement("div");
            carCard.className = "car-card";
            carCard.innerHTML = `
                <h3>${car.carName}</h3>
                <p>Brand: ${car.brand}</p>
                <p>Rate: $${car.rate}</p>
                <p>Type: ${car.type}</p>
                <p>${car.description}</p>
                <img src="images/${car.imageUrl}" alt="${car.carName}" />
                <button onclick="deleteCar(${car.id})">Delete</button>
            `;
            usedCarsContainer.appendChild(carCard);
        });
    }

    // Delete car
    window.deleteCar = function (carId) {
        fetch(`http://127.0.0.1:5000/delete-used-car/${carId}`, {
            method: "DELETE"
        })
        .then(() => {
            fetchUsedCars(); // Refresh the list after deletion
        })
        .catch(error => console.error("Error deleting car:", error));
    };
});
