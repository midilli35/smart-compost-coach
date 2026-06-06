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

    st.subheader("🤖 Analysis Result")

    st.success("Active Compost Stage")

    st.metric("Health Score", "82/100")
    st.metric("Estimated Maturity", "7-10 Days")

    st.write("### Recommendation")
    st.write("• Turn compost within 2 days")
    st.write("• Add dry leaves if moisture increases")
    st.write("• Monitor odor levels")

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Compost Image")
