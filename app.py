import streamlit as st
import google.generativeai as genai
from PIL import Image

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

st.set_page_config(page_title="Smart Compost Coach")

st.title("🌱 Smart Compost Coach")

st.write("Upload a compost photo and get AI-powered recommendations.")

uploaded_file = st.file_uploader(
    "Upload Compost Photo",
    type=["jpg", "jpeg", "png"]
)

if st.button("Analyze Compost"):

    if uploaded_file is None:
        st.warning("Please upload a compost photo.")

    else:

        image = Image.open(uploaded_file)

        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """
        You are an expert compost advisor.

        Analyze this compost image and provide:

        1. Compost Stage
        2. Moisture Level (Dry / Optimal / Wet)
        3. Compost Health Score (0-100)
        4. Carbon-Nitrogen Balance Assessment
        5. Potential Problems
        6. Recommended Actions
        7. Estimated Time Until Compost Maturity

        Keep the response concise and structured.
        """

        try:

            response = model.generate_content(
                [prompt, image]
            )

            st.subheader("🤖 AI Compost Analysis")
            st.write(response.text)

            st.image(
                image,
                caption="Uploaded Compost Image",
                use_container_width=True
            )

        except Exception as e:

            st.error(f"Error: {e}")
