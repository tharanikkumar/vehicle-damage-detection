import streamlit as st
import requests
from PIL import Image, UnidentifiedImageError
import io
from fpdf import FPDF
import base64
import os

BACKEND_URL = "https://vehicle-damage-detection-2.onrender.com"

st.set_page_config(page_title="Vehicle Damage Detection", layout="wide")

st.markdown("""
    <style>
        .title { font-size: 40px; font-weight: bold; text-align: center; color: #2e8b57; margin-top: 20px; }
        .subtitle { font-size: 20px; text-align: center; color: #555; margin-bottom: 30px; }
        .section-title { font-size: 22px; font-weight: 600; margin-top: 40px; margin-bottom: 10px; color: #2e8b57; }
        .cost-box {
            background: #f0fff0; padding: 15px; border-left: 5px solid #4CAF50;
            border-radius: 5px; margin: 10px 0; font-size: 16px; color: #222;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Vehicle Damage Detection</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload a car image to detect damages and get cost estimation in ₹</div>', unsafe_allow_html=True)

if "result" not in st.session_state:
    st.session_state.result = None
if "original_bytes" not in st.session_state:
    st.session_state.original_bytes = None
if "marked_bytes" not in st.session_state:
    st.session_state.marked_bytes = None

# Input
try:
    brands = requests.get(f"{BACKEND_URL}/car_brands").json()
    brand_options = [""] + brands.get("car_brands", [])
except:
    brand_options = [""]

selected_brand = st.selectbox("Select Car Brand", brand_options)
uploaded_file = st.file_uploader("Upload Car Image", type=["jpg", "jpeg", "png"])
submit_button = st.button("🔍 Detect Damage & Estimate")

def generate_pdf(damage_data, marked_img_bytes, original_img_bytes, cost_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Vehicle Damage Detection Report", ln=True, align="C")
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 10, "Original Image", ln=0, align="C")
    pdf.cell(0, 10, "Marked Image", ln=1, align="C")

    try:
        with open("original_temp.jpg", "wb") as f:
            f.write(original_img_bytes)
        Image.open("original_temp.jpg").verify()

        with open("marked_temp.jpg", "wb") as f:
            f.write(marked_img_bytes)
        Image.open("marked_temp.jpg").verify()

        pdf.image("original_temp.jpg", x=10, y=40, w=90)
        pdf.image("marked_temp.jpg", x=110, y=40, w=90)
        pdf.ln(100)
    except UnidentifiedImageError:
        raise RuntimeError("❌ Invalid image format for PDF generation.")

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Detected Damages", ln=True)
    pdf.set_font("Arial", '', 12)
    img = Image.open(io.BytesIO(original_img_bytes)).convert("RGB")
    for idx, dmg in enumerate(damage_data):
        part = dmg.get("part", "")
        conf = dmg.get("confidence", 0)
        bbox = dmg.get("bbox", [])
        pdf.cell(0, 10, f"{idx+1}. {part} - Confidence: {conf:.2f}%", ln=True)

        if len(bbox) == 4:
            crop = img.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            crop.thumbnail((120, 120))
            path = f"crop_{idx}.jpg"
            crop.save(path)
            y = pdf.get_y()
            if y > 250: pdf.add_page()
            pdf.image(path, x=15, y=y, w=50)
            pdf.ln(55)
            os.remove(path)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Estimated Repair Cost", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, cost_data.get("manual_estimate", "").replace("₹", "Rs."))
    pdf.ln(5)
    pdf.multi_cell(0, 10, cost_data.get("gemini_estimate", "").replace("₹", "Rs."))

    pdf.output("report.pdf")
    with open("report.pdf", "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    os.remove("original_temp.jpg")
    os.remove("marked_temp.jpg")
    os.remove("report.pdf")
    return encoded

# Upload handler
if submit_button and uploaded_file and selected_brand:
    with st.spinner("⏳ Processing..."):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        data = {"car_brand": selected_brand}
        try:
            res = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)
            if res.status_code == 200:
                result = res.json()
                if "damage_result" in result:
                    uploaded_file.seek(0)
                    st.session_state.original_bytes = uploaded_file.read()
                    marked_url = f"{BACKEND_URL}/{result['marked_image']}"
                    st.session_state.marked_bytes = requests.get(marked_url).content
                    st.session_state.result = result
                    st.success("✅ Analysis complete!")
                else:
                    st.warning(result.get("message", "No damage found."))
            else:
                st.error("❌ Server error.")
        except Exception as e:
            st.error(f"⚠️ Backend error: {e}")

# Show result
if st.session_state.result:
    result = st.session_state.result
    original = st.session_state.original_bytes
    marked = st.session_state.marked_bytes

    col1, col2 = st.columns(2)
    with col1:
        st.image(original, caption="Original", use_container_width=True)
    with col2:
        st.image(marked, caption="Marked", use_container_width=True)

    try:
        pdf_base64 = generate_pdf(result["damage_result"], marked, original, result["cost"])
        st.download_button("📄 Download PDF Report", base64.b64decode(pdf_base64), file_name="VehicleDamageReport.pdf")
    except Exception as e:
        st.error(f"PDF error: {e}")

    st.markdown('<div class="section-title">💰 Cost Estimation</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cost-box">{result["cost"].get("manual_estimate")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cost-box">{result["cost"].get("gemini_estimate")}</div>', unsafe_allow_html=True)
