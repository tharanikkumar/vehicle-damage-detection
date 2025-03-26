import google.generativeai as genai
import json
import os
import re
from dotenv import load_dotenv

# Load API Key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: GOOGLE_API_KEY is not set. Check your .env file.")

genai.configure(api_key=API_KEY)

# ✅ List available models safely
try:
    models = genai.list_models()
    available_models = [model.name for model in models]
    print("✅ Available Gemini Models:", available_models)
except Exception as e:
    print("⚠️ Failed to list models:", str(e))
    available_models = []

# Function to estimate repair cost
def estimate_cost(damage_list, car_brand):
    try:
        if not isinstance(damage_list, list) or not damage_list:
            return {
                'total_cost': 0,
                'manual_estimate': "✅ No damage detected. Car looks fine.",
                'gemini_estimate': "ℹ️ No damage provided for AI estimation."
            }

        # Base repair costs based on severity
        severity_cost = {"mild": 100, "moderate": 300, "severe": 600}

        # Brand-based repair cost multipliers
        brand_factor = {
            "Toyota": 1.0, "Honda": 1.0, "Ford": 1.2, "BMW": 1.5, "Mercedes": 1.8,
            "Audi": 1.6, "Chevrolet": 1.1, "Nissan": 1.0, "Hyundai": 0.9, "Kia": 0.8
        }
        factor = brand_factor.get(car_brand, 1.0)
        total_cost = 0
        formatted_damage_list = []

        for damage in damage_list:
            severity = damage.get('severity', 'mild').lower()
            damage_type = damage.get('part', 'Unknown')
            confidence = damage.get('confidence', 0)
            bbox = damage.get('bbox', [])

            # Calculate affected area (assuming bbox format: [x1, y1, x2, y2])
            if len(bbox) == 4:
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                area = width * height
            else:
                area = 10000  # Default if bbox is missing

            # Base cost depends on area and severity
            base_cost = (area / 5000) * severity_cost.get(severity, 100)
            cost = base_cost * factor
            total_cost += cost

            formatted_damage_list.append({
                'part': damage_type,
                'severity': severity.capitalize(),
                'confidence': f"{confidence * 100:.1f}%",
                'affected_area': f"{area} pixels²",
                'estimated_cost': f"${cost:.2f}"
            })

        # ✅ Use Gemini AI for refined estimation
        gemini_estimate = "⚠️ Gemini AI cost estimation failed."
        try:
            model_name = "gemini-1.5-pro" if "gemini-1.5-pro" in available_models else "gemini-1.5-flash"
            model = genai.GenerativeModel(model_name)

            prompt = (
                f"Estimate the repair cost for a {car_brand} based on the following detected damages: "
                f"{json.dumps(formatted_damage_list, indent=2)} "
                "Consider industry-standard repair costs for bodywork, painting, part replacement, and labor charges. "
                "Provide a structured breakdown of costs with an estimated range."
            )
            response = model.generate_content(prompt)

            if response and hasattr(response, 'text'):
                ai_text = response.text.strip().replace("\n", " ")

                # Extract cost estimates using regex
                cost_matches = re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', ai_text)
                if cost_matches:
                    cost_range = f"{cost_matches[0]} - {cost_matches[-1]}" if len(cost_matches) > 1 else cost_matches[0]
                else:
                    cost_range = "Not Specified"

                # Format AI response
                gemini_estimate = f"💰 Estimated Cost Range: {cost_range}. Gemini AI Analysis: {ai_text}"
            else:
                gemini_estimate = "⚠️ Gemini AI response was empty."

        except Exception as e:
            gemini_estimate = f"⚠️ Gemini AI cost estimation failed: {str(e)}"

        return {
            'total_cost': round(total_cost, 2),
            'manual_estimate': f"📌 Calculated Cost: ${total_cost:.2f}",
            'gemini_estimate': gemini_estimate
        }

    except Exception as e:
        print(f"❌ Error during cost estimation: {str(e)}")
        return {
            'total_cost': 0,
            'manual_estimate': "❌ Estimation failed.",
            'gemini_estimate': "⚠️ Gemini AI cost estimation failed."
        }
