from flask import Flask, request, render_template, jsonify
import os
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

app = Flask(__name__)

# Load the pre-trained ResNet50 model
model = models.resnet50(pretrained=True)
num_ftrs = model.fc.in_features
model.fc = torch.nn.Linear(num_ftrs, 6)  # Assuming 6 output classes
model.load_state_dict(torch.load('models/new_model.pth', map_location=torch.device('cpu')))
model.eval()

#Image preprocessing
def preprocess_img(image):
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        )
    ])

    image = preprocess(image).unsqueeze(0)
    return image

class_mapping = {
    0: 'Cercospora',
    1: 'Coffee Wilt',
    2: 'Healthy',
    3: 'Leaf Rust',
    4: 'Yellow Leaf Disease',
    5: 'Green Algae'
}

@app.route('/')
def index():
    return render_template('index.html')

# Define prediction function
def predict(image):
    # Preprocess the input image
    image_tensor = preprocess_img(image)
    
    # Perform inference using the loaded model
    with torch.no_grad():
        output = model(image_tensor)
        _, predicted = torch.max(output, 1)
        predicted_disease = class_mapping[predicted]
        return predicted_disease.item()  
    
# Define route for image upload and prediction
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'})

    try:
        # Open and preprocess the uploaded image
        image = Image.open(file).convert('RGB')
        image_tensor = preprocess_img(image)

        # Perform prediction
        with torch.no_grad():
            output = model(image_tensor)
            _, predicted = torch.max(output, 1)
            predicted_class = predicted.item()  # Get the predicted class index
            
            # Map the predicted class to the corresponding disease label
            predicted_disease = class_mapping.get(predicted_class, 'Unknown')
            
        # Return prediction result
        return jsonify({'prediction': predicted_disease})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)