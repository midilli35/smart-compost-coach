import streamlit as st
import google.generativeai as genai
from PIL import Image

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

st.set_page_config(page_title="Smart Compost Coach")

st.title("🌱 Smart Compost Coach")

uploaded_file = st.file_uploader(
    "Upload Compost Photo",
    type=["jpg", "jpeg", "png"]
)

if st.button("Analyze Compost"):

    model = genai.GenerativeModel("gemini-2.5-flash")

    response = model.generate_content(
        "Say hello in one sentence."
    )

    st.write(response.text)
