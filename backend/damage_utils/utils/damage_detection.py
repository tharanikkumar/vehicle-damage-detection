import cv2
import numpy as np
import torch
from mmcv import Config
from torchvision import models, transforms
from PIL import Image

# Load the damage detection model (assuming YOLOv5 or a similar model)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', source='github', trust_repo=True) # Use YOLOv5 small model for demonstration
model.eval()

# Load a pre-trained car classification model (ResNet)
car_model = models.resnet50(pretrained=True)
car_model.eval()

# Image transformations for car classification
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def detect_damage(image_path):
    """
    Detect damages on the car image and return the marked image and damage details.
    """
    image = cv2.imread(image_path)
    if image is None:
        return {'error': 'Invalid image path or format'}

    # Car Image Classification
    if not is_car_image(image_path):
        return {'message': 'Please upload a car image'}

    # Perform damage detection using YOLOv5
    results = model(image_path)

    # Process detection results
    damage_results = []
    for det in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = map(float, det)
        label = results.names[int(cls)]
        
        # Filtering for car damage-related labels (example)
        if label in ["car", "truck", "bus"]:  # You can add more relevant classes
            severity = int(conf * 100) // 20  # Example severity calculation
            damage_results.append({
                'part': label,
                'severity': severity,
                'confidence': round(conf * 100, 2),
                'bbox': (int(x1), int(y1), int(x2), int(y2))
            })

    # Check if no damage is detected
    if not damage_results:
        return {'message': 'Car is looking fine'}

    # Mark detected damages on the image
    marked_image = mark_damaged_parts(image, damage_results)
    marked_image_path = 'uploads/marked_image.jpg'
    cv2.imwrite(marked_image_path, marked_image)

    return {'damage_results': damage_results, 'marked_image': marked_image_path}

def is_car_image(image_path):
    """
    Classify whether the uploaded image is a car or not.
    """
    try:
        image = Image.open(image_path).convert('RGB')
        input_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = car_model(input_tensor)

        # Get the predicted label (ImageNet class index for 'car' ranges from 817 to 864)
        _, predicted = torch.max(output, 1)
        car_label_range = list(range(817, 865))

        return predicted.item() in car_label_range

    except Exception as e:
        print(f"Error during classification: {str(e)}")
        return False

def mark_damaged_parts(image, damage_results):
    """
    Marks damaged parts on the image with bounding boxes and severity labels.
    """
    for damage in damage_results:
        x1, y1, x2, y2 = damage['bbox']
        color = (0, 0, 255)  # Red color for damaged parts
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 3)
        label = f"{damage['part']} (Severity: {damage['severity']})"
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return image
