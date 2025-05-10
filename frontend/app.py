import streamlit as st
import requests
from PIL import Image
import io
from fpdf import FPDF
import base64

st.set_page_config(page_title="Vehicle Damage Detection", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
        .title {
            font-size: 40px;
            font-weight: bold;
            text-align: center;
            color: #2e8b57 ;
            margin-top: 20px;
        }
        .subtitle {
            font-size: 20px;
            text-align: center;
            color: #555;
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 22px;
            font-weight: 600;
            margin-top: 40px;
            margin-bottom: 10px;
            color: #2e8b57 ;
        }
        .cost-box {
            background: #f0fff0;
            padding: 15px;
            border-left: 5px solid #4CAF50;
            border-radius: 5px;
            margin: 10px 0;
            font-size: 16px;
            color: #222;
        }
        div.stButton > button:first-child {
            background-color: #2e8b57;
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 0.6em 1.5em;
            transition: 0.3s;
        }
        div.stButton > button:hover {
            background-color: #256d45;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Vehicle Damage Detection</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload a car image to detect damages and get cost estimation in ₹</div>', unsafe_allow_html=True)

# --- Preserve State
if "result" not in st.session_state:
    st.session_state.result = None
if "original_bytes" not in st.session_state:
    st.session_state.original_bytes = None
if "marked_bytes" not in st.session_state:
    st.session_state.marked_bytes = None

# --- Input Fields ---
try:
    brands = requests.get("http://backend:5050/car_brands").json()
    brand_options = [""] + brands.get("car_brands", [])
except:
    brand_options = [""]

selected_brand = st.selectbox("Select Car Brand", brand_options)
uploaded_file = st.file_uploader("Upload Car Image", type=["jpg", "jpeg", "png"])
submit_button = st.button("🔍 Detect Damage & Estimate")

# --- PDF Generator
def generate_pdf(damage_data, marked_img_bytes, original_img_bytes, cost_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(220, 50, 50)
    pdf.cell(0, 10, "Vehicle Damage Detection Report", ln=True, align="C")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 12)
    pdf.ln(5)
    pdf.cell(95, 10, "Original Image", ln=0, align="C")
    pdf.cell(0, 10, "Marked Image", ln=1, align="C")

    with open("original_temp.jpg", "wb") as f:
        f.write(original_img_bytes)
    with open("marked_temp.jpg", "wb") as f:
        f.write(marked_img_bytes)

    pdf.image("original_temp.jpg", x=10, y=40, w=90)
    pdf.image("marked_temp.jpg", x=110, y=40, w=90)
    pdf.ln(100)

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

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Estimated Repair Cost", ln=True)
    pdf.set_font("Arial", '', 12)
    manual_estimate = cost_data.get("manual_estimate", "N/A").replace("₹", "Rs.")
    gemini_estimate = cost_data.get("gemini_estimate", "N/A").replace("₹", "Rs.").replace("**", "").replace("🔍", "")
    pdf.multi_cell(0, 10, manual_estimate)
    pdf.ln(5)
    pdf.multi_cell(0, 10, gemini_estimate)

    pdf.output("VehicleDamageReport.pdf")
    with open("VehicleDamageReport.pdf", "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- Submit
if submit_button and uploaded_file and selected_brand:
    with st.spinner("⏳ Processing image and analyzing damage..."):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        data = {"car_brand": selected_brand}

        try:
            response = requests.post("http://backend:5050/upload", files=files, data=data)
            if response.status_code == 200:
                result = response.json()
                if "damage_result" in result:
                    uploaded_file.seek(0)
                    st.session_state.original_bytes = uploaded_file.read()
                    st.session_state.marked_bytes = requests.get(f"http://backend:5050/{result['marked_image']}").content
                    st.session_state.result = result
                    st.success("Damage Detection Completed!")
                else:
                    st.warning(result.get("message", "Unexpected format"))
            else:
                st.error(f"❌ Server Error: {response.status_code}")
        except Exception as e:
            st.error(f"⚠️ Could not connect to backend: {e}")

# --- Display Stored Result
if st.session_state.result:
    result = st.session_state.result
    original_bytes = st.session_state.original_bytes
    marked_bytes = st.session_state.marked_bytes

    col1, col2 = st.columns(2)
    with col1:
        st.image(original_bytes, caption="Original Image", use_container_width=True)
    with col2:
        st.image(Image.open(io.BytesIO(marked_bytes)), caption="Marked Image", use_container_width=True)

    pdf_base64 = generate_pdf(result["damage_result"], marked_bytes, original_bytes, result["cost"])
    pdf_bytes = base64.b64decode(pdf_base64)

    colr1, colr2 = st.columns([6, 1])
    with colr1:
        st.markdown('<div class="section-title">🔧 Damage Report</div>', unsafe_allow_html=True)
    with colr2:
        st.download_button(
            label="📄 PDF Report",
            data=pdf_bytes,
            file_name="VehicleDamageReport.pdf",
            mime="application/pdf"
        )

    for idx, dmg in enumerate(result["damage_result"]):
        part = dmg.get("part", "")
        conf = dmg.get("confidence", 0)
        bbox = dmg.get("bbox", [])
        st.markdown(f"**{idx+1}. {part}** (Confidence: `{conf:.2f}%`)")
        if len(bbox) == 4:
            img = Image.open(io.BytesIO(original_bytes)).convert("RGB")
            crop = img.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            crop.thumbnail((150, 150))
            st.image(crop, caption=f"{part} Preview", use_container_width=False)

    st.markdown('<div class="section-title">💰 Cost Estimation</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cost-box">{result["cost"].get("manual_estimate", "N/A")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cost-box">{result["cost"].get("gemini_estimate", "N/A")}</div>', unsafe_allow_html=True)
