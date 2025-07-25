from flask import Flask, request, jsonify, send_from_directory
import os
import cv2
import uuid
import numpy as np
from werkzeug.utils import secure_filename
from damage_utils.damage_detection import detect_damage
from damage_utils.cost_estimation import estimate_cost
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.static_folder, exist_ok=True)  # For marked images

# MySQL connection
db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    ssl_disabled=False
)

@app.route('/')
def home():
    return """
    <h2>🚗 Vehicle Damage Detection API</h2>
    <p>Use <code>/upload</code> endpoint to POST an image and detect car damage.</p>
    <p>Use <code>/car_brands</code> to get a list of supported brands.</p>
    """

@app.route('/car_brands', methods=['GET'])
def get_car_brands():
    return jsonify({
        'car_brands': ["Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Chevrolet", "Nissan", "Hyundai", "Kia"]
    })

@app.route('/static/<path:filename>')
def serve_static_file(filename):
    return send_from_directory(app.static_folder, filename)

def convert_to_python(obj):
    if isinstance(obj, dict):
        return {k: convert_to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_python(i) for i in obj]
    elif isinstance(obj, (np.float32, np.float64, float)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64, int)):
        return int(obj)
    return obj

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

        try:
            result = detect_damage(filepath)

            if "error" in result:
                return jsonify({'error': result["error"]}), 500

            if "message" in result and not result.get("damage_results"):
                return jsonify({'message': result["message"]})

            damage_list = result["damage_results"]
            marked_image_path = result['marked_image']  # This is the path to image file

            # ✅ Load the marked image from path returned by detect_damage
            marked_img = cv2.imread(marked_image_path)
            if marked_img is None:
                raise Exception("Failed to load marked image for saving.")

            # ✅ Save marked image to static folder for frontend access
            marked_filename = f"{uuid.uuid4().hex}_marked.jpg"
            marked_output_path = os.path.join(app.static_folder, marked_filename)
            cv2.imwrite(marked_output_path, marked_img)

            cost_summary = estimate_cost(damage_list, car_brand)

            # Save to DB
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO damage_reports (image_path, damage_result, cost_estimation) VALUES (%s, %s, %s)",
                (filepath, str(damage_list), str(cost_summary))
            )
            db.commit()

            return jsonify({
                'message': 'Damage detected.',
                'damage_result': convert_to_python(damage_list),
                'cost': convert_to_python(cost_summary),
                'original_image': f"uploads/{filename}",
                'marked_image': f"static/{marked_filename}",  # For frontend to fetch
                'car_brand': car_brand
            })

        except Exception as e:
            print(f"[ERROR]: {e}")
            return jsonify({'error': f'Error processing the uploaded image: {str(e)}'}), 500

    return jsonify({'error': 'File upload failed'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
