import streamlit as st
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(page_title="Smart Compost Coach")

st.markdown("""

<style>

.hero-card{
    background: linear-gradient(
        135deg,
        #FFE9BD,
        #FFD580
    );
    border-radius:20px;
    padding:25px;
    margin-bottom:20px;
}

.hero-title{
    font-size:42px;
    font-weight:700;
    color:#2E2E2E;
    line-height:1.1;
}

.hero-subtitle{
    color:#666666;
    margin-top:8px;
    font-size:18px;
}

.upload-card{
    background:white;
    border-radius:50px;
    padding:15px 25px;
    border:2px solid #F0F0F0;
    margin-top:20px;
}

</style>

""", unsafe_allow_html=True)

st.markdown("""

<div class="hero-card">
    <div class="hero-title">
        🌱 Smart Compost Coach
    </div>
    <div class="hero-subtitle">
        Analyze your compost and get instant AI feedback.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📷 Analyze your compost")

camera_photo = st.camera_input("Take a photo")

uploaded_file = st.file_uploader(
"",
type=["jpg", "jpeg", "png"]
)


if camera_photo:
    image_file = camera_photo
else:
    image_file = uploaded_file

if st.button("Analyze Compost"):

    if image_file is None:
        st.warning("Please take or upload a compost photo.")

    else:
        image = Image.open(image_file)

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """
You are an expert compost advisor.

Analyze the compost image and return ONLY the following format:

Health Score: [0-100]
Moisture: [Dry / Optimal / Wet]
Balance: [Carbon Rich / Balanced / Nitrogen Rich]
Ready In: [Short estimate only]

Problems:
- item
- item

Recommendations:
- item
- item
- item

Rules:
- Keep answers short.
- Maximum 2 problems.
- Maximum 3 recommendations.
- Do not write paragraphs.
"""

        try:
            response = model.generate_content([prompt, image])

            st.subheader("🌱 Compost Analysis")
            st.write(response.text)

            with st.expander("📷 Uploaded Photo"):
                st.image(image, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {e}")
