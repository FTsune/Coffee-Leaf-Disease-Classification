document.addEventListener('DOMContentLoaded', function() {
    // Select the form, image container, and prediction result div
    const form = document.getElementById('upload-form');
    const imageContainer = document.getElementById('image-container');
    const resultDiv = document.getElementById('prediction-result');

    // Add event listener to form submission
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission
        
        // Get the uploaded image file
        const imageInput = document.getElementById('image-input');
        const file = imageInput.files[0];
        if (!file) {
            alert('Please select an image file');
            return;
        }

        // Create FormData object to send file data to server
        const formData = new FormData();
        formData.append('file', file);

        // Send image data to server for prediction
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Display uploaded image
            const imageUrl = URL.createObjectURL(file);
            const imageElement = document.createElement('img');
            imageElement.src = imageUrl;
            imageContainer.innerHTML = ''; // Clear previous image
            imageContainer.appendChild(imageElement);

            // Display prediction result
            resultDiv.innerHTML = `Predicted class: <strong>${data.prediction}</strong>`;

        })
        .catch(error => {
            console.error('Error:', error);
            resultDiv.textContent = 'Error occurred during prediction';
        });
    });
});
