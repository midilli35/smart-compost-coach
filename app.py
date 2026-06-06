import streamlit as st

st.set_page_config(page_title="Smart Compost Coach")

st.title("🌱 Smart Compost Coach")

st.write("Upload a compost photo and get AI-inspired recommendations.")

uploaded_file = st.file_uploader(
    "Upload Compost Photo",
    type=["jpg", "jpeg", "png"]
)

days = st.number_input(
    "Days Since Compost Started",
    min_value=0,
    value=15
)

smell = st.radio(
    "Bad Smell Present?",
    ["No", "Yes"]
)

turned = st.number_input(
    "Days Since Last Turning",
    min_value=0,
    value=3
)

if st.button("Analyze Compost"):
if st.button("Analyze Compost"):

    if days < 10:
        st.success("Fresh Compost")

    elif days < 25:
        st.success("Active Compost")

    else:
        st.success("Maturing Compost")
  
