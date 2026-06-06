import streamlit as st
import google.generativeai as genai

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

st.set_page_config(page_title="Smart Compost Coach")

st.title("🌱 Smart Compost Coach")

st.write("Gemini API Test")

if st.button("Analyze Compost"):

    model = genai.GenerativeModel("gemini-2.0-flash")

    response = model.generate_content(
        "Say hello in one sentence."
    )

    st.subheader("🤖 AI Test")
    st.write(response.text)
