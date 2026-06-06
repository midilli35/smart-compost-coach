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

    if uploaded_file is None:
        st.warning("Please upload a compost photo.")

    else:

        image = Image.open(uploaded_file)

        model = genai.GenerativeModel("gemini-2.0-flash")

        prompt = """
        You are an expert compost advisor.

        Analyze this compost image and provide:

        1. Compost Stage
        2. Moisture Condition
        3. Compost Health Score (0-100)
        4. Possible Issues
        5. Recommendations
        6. Estimated Time Until Ready

        Keep the response concise and practical.
        """

        response = model.generate_content(
            [prompt, image]
        )

        st.subheader("🤖 AI Compost Analysis")
        st.write(response.text)

        st.image(image, caption="Uploaded Compost Image")
