import google.generativeai as genai
import json
import os
import re
from dotenv import load_dotenv
from pathlib import Path

# Load API Key
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: GOOGLE_API_KEY is not set. Check your .env file.")

genai.configure(api_key=API_KEY)

# List Gemini models
try:
    models = genai.list_models()
    available_models = [model.name for model in models]
    print("✅ Available Gemini Models:", available_models)
except Exception as e:
    print("⚠️ Failed to list models:", str(e))
    available_models = []

USD_TO_INR = 83.0

def estimate_cost(damage_list, car_brand):
    try:
        if not isinstance(damage_list, list) or not damage_list:
            return {
                'total_cost': 0,
                'manual_estimate': "✅ No damage detected. Car looks fine.",
                'gemini_estimate': "ℹ️ No damage provided for AI estimation."
            }

        severity_cost = {"mild": 75, "moderate": 200, "severe": 400}
        brand_factor = {
            "Toyota": 1.0, "Honda": 1.0, "Ford": 1.2, "BMW": 1.5, "Mercedes": 1.8,
            "Audi": 1.6, "Chevrolet": 1.1, "Nissan": 1.0, "Hyundai": 0.9, "Kia": 0.8
        }
        factor = brand_factor.get(car_brand, 1.0)
        total_cost_inr = 0
        formatted_damage_list = []

        for damage in damage_list:
            severity = damage.get('severity', 'mild').lower()
            damage_type = damage.get('part', 'Unknown')
            confidence = damage.get('confidence', 0)
            bbox = damage.get('bbox', [])

            if len(bbox) == 4:
                width = bbox[2] - bbox[0]
                height = bbox[3] - bbox[1]
                area = width * height
            else:
                area = 5000  # Fallback

            base_cost_usd = (area / 6000) * severity_cost.get(severity, 75)
            cost_inr = base_cost_usd * factor * USD_TO_INR
            total_cost_inr += cost_inr

            formatted_damage_list.append({
                'part': damage_type,
                'severity': severity.capitalize(),
                'confidence': f"{confidence:.1%}",
                'affected_area': f"{int(area)} pixels²",
                'estimated_cost': f"₹{cost_inr:.2f}"
            })

        gemini_estimate = "⚠️ Gemini AI cost estimation failed."
        try:
            model_name = "gemini-1.5-pro" if "gemini-1.5-pro" in available_models else "gemini-1.5-flash"
            model = genai.GenerativeModel(model_name)

            prompt = (
                f"Estimate fair repair costs in INR (₹) for a {car_brand} car based on these detected damage areas:\n\n"
                f"{json.dumps(formatted_damage_list, indent=2)}\n\n"
                "Provide a realistic cost breakdown (parts, labor, paint) in bullet points. "
                "Give a sensible INR range based on Indian standards for mid-range repair shops."
            )

            response = model.generate_content(prompt)
            if response and hasattr(response, 'text'):
                ai_text = response.text.strip()

                # Extract and sort ₹ values for realistic range
                cost_matches = re.findall(r'₹\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?', ai_text)
                numeric_values = sorted([int(re.sub(r"[^\d]", "", c)) for c in cost_matches])
                if numeric_values:
                    cost_range = f"₹{numeric_values[0]:,} - ₹{numeric_values[-1]:,}" if len(numeric_values) > 1 else f"₹{numeric_values[0]:,}"
                else:
                    cost_range = "Not Specified"

                gemini_estimate = (
                    f"**Estimated Cost Range:** {cost_range}\n\n"
                    f"🔍 **Gemini AI Breakdown:**\n\n"
                    f"{ai_text.replace('•', '👉').replace('*', '').strip()}"
                )
            else:
                gemini_estimate = "⚠️ Gemini AI response was empty."

        except Exception as e:
            gemini_estimate = f"⚠️ Gemini AI cost estimation failed: {str(e)}"

        return {
    'total_cost': round(total_cost_inr),
    'manual_estimate': f"**Total Estimated Cost Range: ₹{numeric_values[0]:,} - ₹{numeric_values[-1]:,}**" if numeric_values else "Estimated range not available.",
    'gemini_estimate': (
        f"🔍 **Gemini AI Breakdown:**\n\n"
        f"{ai_text.replace('•', '👉').replace('*', '').strip()}"
    ) if response and hasattr(response, 'text') else "⚠️ Gemini AI response was empty."
}


    except Exception as e:
        print(f"❌ Error during cost estimation: {str(e)}")
        return {
            'total_cost': 0,
            'manual_estimate': "❌ Estimation failed.",
            'gemini_estimate': "⚠️ Gemini AI cost estimation failed."
        }
