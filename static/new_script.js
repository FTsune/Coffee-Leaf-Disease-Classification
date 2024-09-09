document.addEventListener('DOMContentLoaded', function() {
  const imageContainer = document.getElementById('image-container');
  const imageInput = document.getElementById('image-input');
  const uploadText = document.getElementById('upload-text');
  const uploadImage = document.getElementById('upload-image');
  const closeIcon = document.getElementById('close-icon');
  const resultDiv = document.getElementById('prediction-result');
  const aboutUsDiv = document.getElementById('about-us');
  const leafDiv = document.getElementById('leaf-classification'); 
  const navLinks = document.querySelectorAll('.nav-link');

  imageContainer.addEventListener('click', function(event) {
      if (event.target !== closeIcon) {
          imageInput.click();
      }
  });

  imageInput.addEventListener('change', function() {
      const file = this.files[0];
      if (!file) {
          alert('Please select an image file');
          return;
      }

      uploadText.textContent = file.name;

      const formData = new FormData();
      formData.append('file', file);
      fetch('/predict', {
          method: 'POST',
          body: formData
      })
      .then(response => response.json())
      .then(data => {
          const imageUrl = URL.createObjectURL(file);
          const imageElement = document.createElement('img');
          imageElement.src = imageUrl;
          imageContainer.innerHTML = '';
          const newUploadText = document.createElement('p');
          newUploadText.id = 'upload-text';
          newUploadText.textContent = file.name;
          imageContainer.appendChild(newUploadText);
          imageContainer.appendChild(imageElement);
          imageContainer.appendChild(closeIcon);
          closeIcon.style.display = 'block';

          const predictionText = document.getElementById('prediction-text');
          let otherPredictionsText = document.getElementById('other-predictions');
    
          if (!otherPredictionsText) {
            otherPredictionsText = document.createElement('p');
            otherPredictionsText.id = 'other-predictions';
            resultDiv.appendChild(otherPredictionsText);
          } else {
            otherPredictionsText.textContent = 'Other Predictions:';
            while (otherPredictionsText.lastChild) {
              otherPredictionsText.removeChild(otherPredictionsText.lastChild);
            }
          }
    
          const predictions = data.prediction;
          const confidences = data.confidences;
          const sortedPredictions = predictions.map((prediction, index) => ({
            prediction,
            confidence: confidences[prediction]
          })).sort((a, b) => b.confidence - a.confidence);
    
          const threshold = 0.5; // Set your desired threshold here
          const aboveThresholdPredictions = sortedPredictions.filter(({ confidence }) => confidence >= threshold);
          const belowThresholdPredictions = sortedPredictions.filter(({ confidence }) => confidence < threshold).slice(0, 3);
    
          if (aboveThresholdPredictions.length > 0) {
            const aboveThresholdPrediction = aboveThresholdPredictions[0];
            predictionText.textContent = `Prediction: ${aboveThresholdPrediction.prediction} (${(aboveThresholdPrediction.confidence * 100).toFixed(2)}%)`;
          } else {
            predictionText.textContent = 'No predictions above the threshold.';
          }
    
          belowThresholdPredictions.forEach(({ prediction, confidence }) => {
            const p = document.createElement('p');
            p.textContent = `${prediction} (${(confidence * 100).toFixed(2)}%)`;
            otherPredictionsText.appendChild(p);
          });
        })
        .catch(error => {
          console.error('Error:', error);
          resultDiv.textContent = 'Error occurred during prediction';
        });
    });

  closeIcon.addEventListener('click', function(event) {
      event.stopPropagation();
      imageContainer.innerHTML = '';
      uploadText.textContent = 'Upload an image file';
      imageContainer.appendChild(uploadText);
      imageContainer.appendChild(uploadImage);
      imageContainer.appendChild(imageInput);
      closeIcon.style.display = 'none';
      resultDiv.innerHTML = '';
  });

  navLinks.forEach(link => {
      link.addEventListener('click', function() {
          const target = this.getAttribute('href').substring(1);
          if (target === 'test') {
              imageContainer.style.display = 'block';
              resultDiv.style.display = 'block';
              aboutUsDiv.style.display = 'none';
              leafDiv.style.display = 'none';
          } else if (target === 'leaf') {
              imageContainer.style.display = 'none';
              resultDiv.style.display = 'none';
              aboutUsDiv.style.display = 'none';
              leafDiv.style.display = 'block';
          } else if (target === 'about') {
              imageContainer.style.display = 'none';
              resultDiv.style.display = 'none';
              aboutUsDiv.style.display = 'block'; 
              leafDiv.style.display = 'none';
          }
      });
  });
});
