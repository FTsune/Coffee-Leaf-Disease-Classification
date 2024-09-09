from flask import Flask, request, render_template, jsonify
import os
import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
import heapq
import numpy as np
import cv2
from PIL import Image

app = Flask(__name__)

# Load the pre-trained ResNet50 model
model = models.resnet50(pretrained=True)
num_ftrs = model.fc.in_features

# Define class mapping
class_mapping = {
    0: 'Excessive Sunlight',
    1: 'Leaf Rust',
    2: 'Lichens',
    3: 'No Disease',
    4: 'Sooty Mold',
    5: 'Wilt'
}

num_classes = len(class_mapping)
model.fc = nn.Linear(num_ftrs, num_classes)
model.load_state_dict(torch.load('models/model-ResNet50.pth', map_location=torch.device('cpu')))
model.eval()

def pad_image(image):
    width, height = image.size
    max_dim = max(width, height)

    
    background_color = tuple(np.random.randint(0, 256, size=3))
    background = Image.new('RGB', (max_dim, max_dim), background_color)

    pos = ((max_dim - width) // 2, (max_dim - height) // 2)
    background.paste(image, pos)

    return background

def sobel_edge_detection(image):
    image = np.array(image)
    channels = []
    for i in range(3):  
        gray = image[:, :, i]
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel = np.sqrt(sobelx**2 + sobely**2)
        sobel = np.uint8(sobel)
        channels.append(sobel)
    sobel = np.stack(channels, axis=-1) 
    return Image.fromarray(sobel)

class SobelEdgeDetection(object):
    def __call__(self, img):
        return sobel_edge_detection(img)
    
# Image preprocessing
def preprocess_img(image):
    preprocess = transforms.Compose([
    transforms.Lambda(pad_image), 
    transforms.Resize(size=(512, 512)),
    transforms.CenterCrop(448),
    SobelEdgeDetection(),    
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
#     transforms.ColorJitter(brightness=0.1, contrast=0.2, saturation=0.2, hue=0.1), 
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    image = preprocess(image).unsqueeze(0)
    return image

# Define prediction function with confidence levels
def predict_image(image_tensor, model, class_mapping, threshold=0.5, topk=3):
    with torch.no_grad():
        output = model(image_tensor)
        probabilities = torch.sigmoid(output).cpu().numpy().flatten()

    confidence_levels = {class_mapping[i]: float(probabilities[i]) for i in range(len(class_mapping))}

    # Get the top 3 predictions based on confidence levels
    top_predictions = heapq.nlargest(topk, confidence_levels, key=confidence_levels.get)
    top_confidences = {cls: confidence_levels[cls] for cls in top_predictions}

    return top_predictions, top_confidences

@app.route('/')
def index():
    return render_template('index.html')

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
        predicted_diseases, confidence_levels = predict_image(image_tensor, model, class_mapping, threshold=0.5)

        # Return prediction result
        return jsonify({'prediction': predicted_diseases, 'confidences': confidence_levels})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
