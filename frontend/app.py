import streamlit as st
import requests
from PIL import Image
import io

# Set page configuration
st.set_page_config(page_title="Vehicle Damage Detection", layout="wide")

# Custom Styling
st.markdown("""
    <style>
        .title {
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            color: #FF5733;
        }
        .subtitle {
            font-size: 18px;
            text-align: center;
            color: #4A4A4A;
        }
        .report {
            font-size: 16px;
            font-weight: bold;
            color: #008080;
        }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<p class="title">🚗 Vehicle Damage Detection & Cost Estimation</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Upload a car image to detect damages and estimate repair costs.</p>', unsafe_allow_html=True)
st.write("---")

# Fetch available car brands from backend
response = requests.get("http://localhost:5050/car_brands")
car_brands = response.json().get("car_brands", []) if response.status_code == 200 else []

# Sidebar for selection
with st.sidebar:
    st.header("🛠️ Select Options")
    selected_brand = st.selectbox("Select Car Brand", car_brands)
    uploaded_file = st.file_uploader("Upload Car Image", type=["jpg", "png", "jpeg"])
    submit_button = st.button("🔍 Process Image")

# Process the uploaded image
if submit_button and uploaded_file and selected_brand:
    with st.spinner("Processing... Please wait ⏳"):
        files = {"file": uploaded_file.getvalue()}
        data = {"car_brand": selected_brand}

        try:
            response = requests.post("http://localhost:5050/upload", files=files, data=data)
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Damage Detection Completed!")

                # Show results
                st.markdown('<p class="report">🔎 Damage Report</p>', unsafe_allow_html=True)
                st.json(data["damage"])
                st.markdown(f"💰 Estimated Cost: **${data['cost']}**")

                # Display original and marked images side by side
                col1, col2 = st.columns(2)
                original_image = requests.get(f"http://localhost:5050/{data['original_image']}")
                marked_image = requests.get(f"http://localhost:5050/{data['marked_image']}")

                with col1:
                    st.image(Image.open(io.BytesIO(original_image.content)), caption="Original Image", use_container_width=True)
                with col2:
                    st.image(Image.open(io.BytesIO(marked_image.content)), caption="Marked Image", use_container_width=True)

            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"⚠️ Failed to connect to the backend: {e}")
