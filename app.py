import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

genai.configure(
    api_key=st.secrets["GEMINI_API_KEY"]
)

st.set_page_config(
    page_title="Smart Compost Coach",
    layout="centered"
)

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
    font-size:38px;
    font-weight:700;
    color:#2E2E2E;
}

.hero-subtitle{
    color:#666666;
    margin-top:8px;
    font-size:16px;
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

uploaded_file = st.file_uploader(
    "📷 Take or Upload Photo",
    type=["jpg", "jpeg", "png"]
)

if st.button("Analyze Compost"):

    if uploaded_file is None:

        st.warning("Please upload a compost photo.")

    else:

        image = Image.open(uploaded_file)

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        prompt = """
Return ONLY valid JSON.

{
  "health_score": 0,
  "moisture": "",
  "balance": "",
  "ready_in": "",
  "problems": [],
  "recommendations": []
}

Rules:
- health_score must be between 0 and 100
- maximum 2 problems
- maximum 3 recommendations
- no explanation outside JSON
"""

        try:

            response = model.generate_content(
                [prompt, image]
            )

            st.write(response.text)
            
            data = json.loads(response.text)

            st.subheader("🌱 Compost Status")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "🌱 Health",
                    f"{data['health_score']}/100"
                )

            with col2:
                st.metric(
                    "💧 Moisture",
                    data["moisture"]
                )

            with col3:
                st.metric(
                    "⚖️ Balance",
                    data["balance"]
                )

            st.info(
                f"⏳ Ready In: {data['ready_in']}"
            )

            with st.expander("⚠ Potential Problems"):

                for item in data["problems"]:
                    st.write(f"• {item}")

            with st.expander("💡 Recommendations"):

                for item in data["recommendations"]:
                    st.write(f"• {item}")

            with st.expander("📷 Uploaded Photo"):

                st.image(
                    image,
                    use_container_width=True
                )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )
