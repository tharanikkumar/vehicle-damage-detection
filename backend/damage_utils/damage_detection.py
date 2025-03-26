import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os

# Ensure uploads directory exists
UPLOADS_DIR = 'uploads'
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Load the damage detection model (Mask R-CNN with ResNet-101 backbone)
model = models.detection.maskrcnn_resnet50_fpn(weights=models.detection.MaskRCNN_ResNet50_FPN_Weights.DEFAULT)
model.eval()

# Load a pre-trained MobileNet model for car classification
car_model = models.mobilenet_v3_large(weights=models.MobileNet_V3_Large_Weights.DEFAULT)
car_model.eval()

# Image transformations for classification
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Damage label mapping with distinct colors
DAMAGE_LABELS = {
    1: ("scratch", (255, 215, 0)),  # Gold
    2: ("dent", (147, 112, 219)),  # Purple
    3: ("crack", (34, 139, 34)),  # Green
    4: ("lamp broken", (135, 206, 250)),  # Light blue
    5: ("glass shatter", (255, 99, 71)),  # Tomato red
    6: ("flat tire", (255, 165, 0)),  # Orange
    7: ("mirror broken", (255, 0, 255)),  # Magenta
    8: ("boot dent", (0, 191, 255)),  # Deep Sky Blue
    9: ("fog lamp broken", (255, 140, 0))  # Dark Orange
}

# Define car labels from ImageNet classes (example range)
CAR_LABEL_RANGE = list(range(817, 897))  # Labels for cars and trucks

def detect_damage(image_path):
    """Detects damage in the uploaded image."""
    try:
        if not os.path.exists(image_path):
            return {'error': 'Invalid image path'}
        
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Invalid image format'}

        # Check if image is a car (supports different angles)
        if not is_car_image(image_path):
            return {'message': 'Please upload a car image'}

        # Convert image format
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)

        # Perform damage detection
        transform_image = transforms.ToTensor()(pil_image).unsqueeze(0)
        with torch.no_grad():
            outputs = model(transform_image)

        damage_results = []
        masks = outputs[0]['masks'].detach().cpu().numpy()
        scores = outputs[0]['scores'].detach().cpu().numpy()
        labels = outputs[0]['labels'].detach().cpu().numpy()
        bboxes = outputs[0]['boxes'].detach().cpu().numpy()

        overlay = image.copy()
        alpha = 0.5  # Transparency factor

        for i in range(len(masks)):
            if scores[i] > 0.5:  # Confidence threshold
                mask = masks[i, 0]
                label_info = DAMAGE_LABELS.get(labels[i], ("unknown", (128, 128, 128)))
                label, color = label_info
                confidence = scores[i]
                bbox = [int(x) for x in bboxes[i]]

                damage_results.append({
                    'part': label,
                    'confidence': round(confidence * 100, 2),
                    'bbox': bbox
                })

                # Apply semi-transparent colored mask
                mask_area = mask > 0.5
                overlay[mask_area] = (overlay[mask_area] * (1 - alpha) + np.array(color) * alpha).astype(np.uint8)

                # Draw bounding box
                cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
                label_text = f"{label}|{confidence:.2f}"
                
                # Add background for text
                (w, h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                cv2.rectangle(image, (bbox[0], bbox[1] - 20), (bbox[0] + w, bbox[1]), color, -1)
                
                # Put label text
                cv2.putText(image, label_text, (bbox[0], bbox[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Blend overlay and original image
        final_image = cv2.addWeighted(image, 0.7, overlay, 0.3, 0)

        # Save marked image
        filename = os.path.basename(image_path)
        marked_image_path = os.path.join(UPLOADS_DIR, f'marked_{os.path.splitext(filename)[0]}.jpg')
        cv2.imwrite(marked_image_path, final_image)

        return {
            'damage_results': damage_results,
            'marked_image': marked_image_path
        }
    except Exception as e:
        return {'error': f"Error during damage detection: {str(e)}"}

def is_car_image(image_path):
    """Determines if the uploaded image contains a car using MobileNetV3."""
    try:
        image = Image.open(image_path).convert('RGB')
        input_tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = car_model(input_tensor)

        _, predicted = torch.max(output, 1)
        return predicted.item() in CAR_LABEL_RANGE
    except Exception:
        return False

def classify_image(image_path):
    return is_car_image(image_path)
