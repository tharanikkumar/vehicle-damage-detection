from flask import Flask, request, jsonify, send_from_directory
import os
import cv2
import uuid
import numpy as np
from werkzeug.utils import secure_filename
from damage_utils.damage_detection import detect_damage, classify_image
from damage_utils.cost_estimation import estimate_cost
from PIL import Image
import mysql.connector
import torch

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="vehicle_damage"
)

@app.route('/car_brands', methods=['GET'])
def get_car_brands():
    car_brands = ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Chevrolet", "Nissan", "Hyundai", "Kia"]
    return jsonify({'car_brands': car_brands})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

import random
import cv2
import numpy as np

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    car_brand = request.form.get('car_brand')
    if not car_brand:
        return jsonify({'error': 'Car brand not provided'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        is_car = classify_image(filepath)
        if not is_car:
            return jsonify({'message': 'Please upload a car image.'}), 400

        try:
            damage_result = detect_damage(filepath)
            if not damage_result or not damage_result.get('damage_results'):
                return jsonify({'message': 'Car is looking fine.'})

            damage_list = damage_result['damage_results']
            cost_estimation = estimate_cost(damage_list, car_brand)

            marked_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'marked_{uuid.uuid4()}.jpg')
            image = cv2.imread(filepath)

            for damage in damage_list:
                bbox = damage.get("bbox", [])
                mask = damage.get("mask", None)
                damage_type = damage["part"]
                confidence = damage["confidence"]

                if bbox:
                    color = tuple(np.random.randint(100, 255, size=3).tolist())  # Random color for different damages
                    cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)

                    label = f"{damage_type} | {confidence:.2f}"
                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    text_x, text_y = bbox[0], bbox[1] - 10
                    cv2.rectangle(image, (text_x, text_y - text_size[1] - 5), (text_x + text_size[0], text_y), color, -1)
                    cv2.putText(image, label, (text_x, text_y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

                if mask is not None:
                    mask = np.array(mask, dtype=np.uint8)
                    color_mask = np.zeros_like(image)
                    color_mask[:, :] = color
                    mask = np.expand_dims(mask, axis=-1)
                    image = cv2.addWeighted(image, 1.0, color_mask * mask, 0.5, 0)

            cv2.imwrite(marked_image_path, image)

            cursor = db.cursor()
            cursor.execute("INSERT INTO damage_reports (image_path, marked_image_path, car_brand, damage_result, cost_estimation) VALUES (%s, %s, %s, %s, %s)", 
                           (filepath, marked_image_path, car_brand, str(damage_list), str(cost_estimation)))
            db.commit()

            return jsonify({
                'message': 'Damage detected.',
                'damage': damage_list,
                'cost': cost_estimation,
                'original_image': f"uploads/{filename}",
                'marked_image': f"uploads/{os.path.basename(marked_image_path)}",
                'car_brand': car_brand
            })
        except Exception as e:
            print(f"[ERROR] Exception occurred: {str(e)}")
            return jsonify({'error': 'Error processing the uploaded image'}), 500

    return jsonify({'error': 'File upload failed'}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)