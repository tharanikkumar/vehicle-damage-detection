import os
import cv2
import numpy as np
from PIL import Image
from inference_sdk import InferenceHTTPClient

UPLOADS_DIR = 'uploads'
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Roboflow config
client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="UBP6gDsmvPFrDbUncyUP"
)

DAMAGE_COLORS = {
    "scratch": (255, 215, 0),
    "dent": (147, 112, 219),
    "crack": (34, 139, 34),
    "lamp broken": (135, 206, 250),
    "glass shatter": (255, 99, 71),
    "flat tire": (255, 165, 0)
}

def detect_damage(image_path):
    try:
        if not os.path.exists(image_path):
            return {'error': 'Invalid image path'}

        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Invalid image format'}

        # Send to Roboflow model
        result = client.run_workflow(
            workspace_name="seai-sq6is",
            workflow_id="custom-workflow",
            images={"image": image_path},
            use_cache=False
        )

        if not result or not isinstance(result, list):
            return {'error': 'No result returned from Roboflow.'}

        predictions = result[0].get("predictions", {}).get("predictions", [])
        if not predictions:
            return {'message': 'Car is looking fine.'}

        overlay = image.copy()
        damage_results = []

        for pred in predictions:
            label = pred.get("class", "unknown")
            confidence = round(pred.get("confidence", 0) * 100, 2)
            x, y, width, height = map(int, [pred["x"], pred["y"], pred["width"], pred["height"]])

            x1, y1 = x - width // 2, y - height // 2
            x2, y2 = x + width // 2, y + height // 2

            color = DAMAGE_COLORS.get(label.lower(), (128, 128, 128))
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)

            label_text = f"{label}|{confidence:.1f}%"
            (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(overlay, (x1, y1 - text_h - 10), (x1 + text_w, y1), color, -1)
            cv2.putText(overlay, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            damage_results.append({
                "part": label,
                "confidence": confidence / 100,
                "bbox": [x1, y1, x2, y2]
            })

        marked_path = os.path.join(UPLOADS_DIR, f"marked_{os.path.basename(image_path)}")
        cv2.imwrite(marked_path, overlay)

        return {
            "damage_results": damage_results,
            "marked_image": marked_path
        }

    except Exception as e:
        return {'error': f"Detection error: {str(e)}"}
