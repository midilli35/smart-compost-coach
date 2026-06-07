import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import math

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(
    page_title="Smart Compost Coach",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

:root {
  --mustard:   #FFD580;
  --cream:     #FFE9BD;
  --royal:     #464CE6;
  --peri:      #7C80ED;
  --lavender:  #B2B4F4;
  --mist:      #E8E8FC;
  --sage:      #B8CCB6;
  --pale-sage: #DBE5DA;
  --orange:    #E8650A;
  --orange-dk: #C8560A;
  --dark:      #2A2A2A;
  --mid:       #555555;
  --light:     #888888;
  --page-bg:   #F7F4EE;
}

/* Page background */
.stApp, .main, .block-container {
  background: var(--page-bg) !important;
  font-family: 'DM Sans', sans-serif !important;
}

.block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 520px !important;
}

/* Hide Streamlit chrome */
header[data-testid="stHeader"] { display: none !important; }
.stFileUploader label { display: none !important; }
footer { display: none !important; }

/* ── HERO CARD ── */
.hero-card {
  background: linear-gradient(140deg, var(--cream) 0%, var(--mustard) 100%);
  border-radius: 24px;
  padding: 22px 22px 18px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}
.hero-pattern {
  position: absolute;
  top: 0; right: 0;
  width: 140px; height: 100%;
  opacity: 0.18;
  pointer-events: none;
}
.hero-title {
  font-family: 'Fraunces', serif;
  font-size: 28px;
  font-weight: 600;
  color: var(--dark);
  line-height: 1.2;
  position: relative;
  z-index: 1;
}
.hero-sub {
  font-size: 13px;
  color: #666;
  margin-top: 6px;
  position: relative;
  z-index: 1;
}

/* ── UPLOAD ZONE ── */
.upload-zone {
  border: 1.5px dashed #C8B88A;
  border-radius: 18px;
  padding: 26px 16px;
  text-align: center;
  background: #FFFDF7;
  margin-bottom: 14px;
  cursor: pointer;
}
.upload-title {
  font-size: 14px;
  color: var(--mid);
  margin-top: 10px;
}
.upload-title strong { color: var(--royal); }
.upload-hint {
  font-size: 11px;
  color: #AAA;
  margin-top: 4px;
}

/* ── ANALYZE BUTTON ── */
div[data-testid="stButton"] > button {
  width: 100% !important;
  padding: 15px 24px !important;
  background: var(--orange) !important;
  color: white !important;
  border: none !important;
  border-radius: 16px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 16px !important;
  font-weight: 600 !important;
  letter-spacing: 0.02em !important;
  cursor: pointer !important;
  transition: background 0.2s, transform 0.1s !important;
  box-shadow: none !important;
}
div[data-testid="stButton"] > button:hover {
  background: var(--orange-dk) !important;
  transform: translateY(-1px) !important;
  border: none !important;
}
div[data-testid="stButton"] > button:active {
  transform: scale(0.98) !important;
}

/* ── HEALTH CARD ── */
.health-card {
  background: var(--mustard);
  border-radius: 22px;
  padding: 20px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 18px;
}
.health-text-block h4 {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #7A5E20;
  font-weight: 600;
  margin: 0;
}
.health-score-num {
  font-family: 'Fraunces', serif;
  font-size: 52px;
  color: var(--dark);
  line-height: 1;
  margin: 2px 0;
}
.health-score-num span {
  font-size: 20px;
  color: #7A5E20;
}
.health-status-label {
  font-size: 12px;
  color: #7A5E20;
  font-weight: 500;
}

/* ── METRIC CARDS ── */
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}
.metric-card {
  background: white;
  border-radius: 16px;
  padding: 14px 14px 12px;
  border: 1px solid #EDE8DC;
}
.metric-label {
  font-size: 11px;
  color: var(--light);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 4px;
}
.metric-value {
  font-family: 'Fraunces', serif;
  font-size: 20px;
  color: var(--dark);
}

/* ── MATURITY CARD ── */
.maturity-card {
  background: white;
  border-radius: 18px;
  padding: 16px 18px;
  margin-bottom: 16px;
  border: 1px solid #EDE8DC;
}
.maturity-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
}
.maturity-label {
  font-size: 11px;
  color: var(--light);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.maturity-value {
  font-family: 'Fraunces', serif;
  font-size: 15px;
  color: var(--royal);
}
.maturity-track {
  height: 8px;
  background: var(--mist);
  border-radius: 99px;
  overflow: hidden;
  margin-bottom: 10px;
}
.maturity-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--peri), var(--royal));
  border-radius: 99px;
  transition: width 1.2s cubic-bezier(0.4,0,0.2,1);
}
.maturity-dots {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}
.mdot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--mist);
  display: inline-block;
  flex-shrink: 0;
}
.mdot.filled { background: var(--peri); }
.mdot.active { background: var(--royal); transform: scale(1.3); }

/* ── SIDE-BY-SIDE PANELS ── */
.panels-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}
.panel-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #EDE8DC;
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.panel-card:hover { box-shadow: 0 4px 16px rgba(70,76,230,0.1); }
.panel-header {
  padding: 12px 14px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.panel-header.problems { border-bottom: 2px solid var(--cream); }
.panel-header.recs { border-bottom: 2px solid var(--mist); }
.panel-title { font-size: 12px; font-weight: 600; color: var(--dark); }
.panel-badge {
  margin-left: auto;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 99px;
}
.badge-amber { background: #FFF0C8; color: #9A6700; }
.badge-blue  { background: var(--mist); color: var(--royal); }
.panel-preview {
  padding: 8px 14px 12px;
  font-size: 12px;
  color: var(--mid);
  line-height: 1.5;
}
.panel-item {
  display: flex;
  gap: 7px;
  margin-bottom: 5px;
  align-items: flex-start;
}

/* ── EXPANDED DETAIL CARD ── */
.detail-card {
  background: white;
  border-radius: 18px;
  border: 2px solid var(--mist);
  padding: 16px 18px;
  margin-bottom: 12px;
  box-shadow: 4px 4px 0 var(--mist);
}
.detail-title {
  font-family: 'Fraunces', serif;
  font-size: 15px;
  color: var(--royal);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.detail-item {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  align-items: flex-start;
  font-size: 13px;
  color: var(--mid);
  line-height: 1.5;
}
.bullet-circle {
  flex-shrink: 0;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-top: 4px;
}
.bullet-tri {
  flex-shrink: 0;
  margin-top: 4px;
  width: 0; height: 0;
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
  border-left: 8px solid;
}

/* ── PHOTO CARD ── */
.photo-card {
  background: white;
  border-radius: 18px;
  border: 1px solid #EDE8DC;
  overflow: hidden;
  margin-bottom: 12px;
}
.photo-card-header {
  padding: 12px 16px;
  border-bottom: 1px solid #EDE8DC;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--light);
  font-weight: 600;
}


/* ── JOURNEY + CHECK-IN ── */
.journey-card {
  background: white;
  border-radius: 18px;
  padding: 18px;
  border: 1px solid #EDE8DC;
  margin-bottom: 16px;
}
.journey-title {
  font-family: 'Fraunces', serif;
  font-size: 16px;
  color: var(--dark);
  margin-bottom: 12px;
}
.journey-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 12px;
  color: var(--light);
}
.journey-step.active {
  color: var(--royal);
  font-weight: 700;
}
.journey-track {
  height: 10px;
  background: var(--mist);
  border-radius: 999px;
  overflow: hidden;
}
.journey-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--peri), var(--royal));
  border-radius: 999px;
  transition: width 1s ease;
}
.check-card {
  background: #FFFDF7;
  border: 1px solid #EDE8DC;
  border-radius: 18px;
  padding: 16px 18px;
  margin-bottom: 16px;
}
.check-title {
  font-family: 'Fraunces', serif;
  font-size: 16px;
  color: var(--dark);
  margin-bottom: 4px;
}
.check-sub {
  font-size: 12px;
  color: var(--mid);
  margin-bottom: 10px;
}

/* ── FILE UPLOADER STYLE ── */
.stFileUploader [data-testid="stFileUploaderDropzone"] {
  background: #FFFDF7 !important;
  border: 1.5px dashed #C8B88A !important;
  border-radius: 18px !important;
}

/* Hide default streamlit metrics label formatting */
[data-testid="stMetricLabel"] { display: none !important; }

/* Warning / error */
.stAlert { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SVG ILLUSTRATIONS
# ─────────────────────────────────────────────

HERO_SVG = """
<svg viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:44px;height:44px;margin-bottom:8px">
  <circle cx="22" cy="22" r="20" fill="#FFD580" opacity="0.5"/>
  <path d="M22 34 L22 20" stroke="#5A8A40" stroke-width="2" stroke-linecap="round"/>
  <path d="M22 24 Q16 20 14 14 Q20 13 24 18 Q26 20 22 24Z" fill="#7ABD5A"/>
  <path d="M22 28 Q28 24 30 18 Q24 16 20 22 Q19 24 22 28Z" fill="#5A8A40"/>
</svg>"""

HERO_PATTERN = """
<svg class="hero-pattern" viewBox="0 0 140 160" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="20" cy="20" r="18" stroke="#7A5E20" stroke-width="1.5" fill="none"/>
  <circle cx="70" cy="10" r="10" stroke="#7A5E20" stroke-width="1.2" fill="none"/>
  <path d="M10 60 Q30 40 50 60 Q70 80 90 60" stroke="#7A5E20" stroke-width="1.2" fill="none"/>
  <circle cx="110" cy="40" r="6" stroke="#7A5E20" stroke-width="1" fill="none"/>
  <path d="M50 100 Q70 80 90 100 Q110 120 130 100" stroke="#7A5E20" stroke-width="1" fill="none"/>
  <circle cx="30" cy="130" r="14" stroke="#7A5E20" stroke-width="1.2" fill="none"/>
  <circle cx="100" cy="130" r="8" stroke="#7A5E20" stroke-width="1" fill="none"/>
  <path d="M5 90 L15 90 M10 85 L10 95" stroke="#7A5E20" stroke-width="1.2"/>
  <path d="M120 70 L130 70 M125 65 L125 75" stroke="#7A5E20" stroke-width="1"/>
</svg>"""

UPLOAD_SVG = """
<svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:52px;height:52px;margin:0 auto 10px">
  <circle cx="26" cy="26" r="24" fill="#FFF0CC"/>
  <path d="M18 30 Q14 30 13 26 Q12 20 17 19 Q17 13 22 12 Q27 11 29 16 Q34 15 35 19 Q39 19 39 24 Q39 30 34 30"
        stroke="#C8A020" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M22 34 L26 28 L30 34" stroke="#C8A020" stroke-width="1.5"
        stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  <line x1="26" y1="28" x2="26" y2="40" stroke="#C8A020" stroke-width="1.5" stroke-linecap="round"/>
</svg>"""

WORM_SVG = """
<svg viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:72px;height:72px;flex-shrink:0">
  <circle cx="36" cy="36" r="32" fill="#FFE9BD"/>
  <rect x="12" y="48" width="48" height="14" rx="4" fill="#C8A060" opacity="0.4"/>
  <rect x="12" y="54" width="48" height="8" rx="3" fill="#A07840" opacity="0.3"/>
  <path d="M20 50 Q22 44 26 45 Q30 46 28 50 Q26 54 30 53 Q34 52 34 48 Q34 44 38 44"
        stroke="#E86040" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="38" cy="43" r="3" fill="#E86040"/>
  <circle cx="39" cy="42" r="1" fill="white"/>
  <path d="M48 47 L48 38" stroke="#5A8A40" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M48 41 Q44 38 43 34 Q47 33 49 37Z" fill="#7ABD5A"/>
  <path d="M48 44 Q52 41 53 37 Q49 36 47 40Z" fill="#5A8A40"/>
  <circle cx="24" cy="38" r="1.5" fill="#D4A020" opacity="0.6"/>
  <circle cx="58" cy="42" r="1" fill="#7ABD5A" opacity="0.7"/>
  <circle cx="16" cy="44" r="1" fill="#E86040" opacity="0.5"/>
</svg>"""

MOISTURE_SVG = """
<svg viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:26px;height:26px;margin-bottom:6px">
  <path d="M13 4 Q10 8 8 12 Q6 16 8 20 Q10 24 13 24 Q16 24 18 20 Q20 16 18 12 Q16 8 13 4Z"
        fill="#B2D4F4" stroke="#464CE6" stroke-width="1.2"/>
  <path d="M10 18 Q12 22 13 22" stroke="white" stroke-width="1" stroke-linecap="round" opacity="0.8"/>
</svg>"""

BALANCE_SVG = """
<svg viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:26px;height:26px;margin-bottom:6px">
  <rect x="4" y="14" width="7" height="8" rx="2" fill="#B8CCB6" stroke="#5A8A40" stroke-width="1.2"/>
  <rect x="15" y="10" width="7" height="12" rx="2" fill="#FFD580" stroke="#C8A020" stroke-width="1.2"/>
  <path d="M2 22 L24 22" stroke="#ccc" stroke-width="1"/>
</svg>"""

WARNING_SVG = """<svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px;flex-shrink:0">
  <circle cx="8" cy="8" r="6.5" stroke="#E8A020" stroke-width="1.3"/>
  <path d="M8 5 L8 9" stroke="#E8A020" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="8" cy="11.5" r="1" fill="#E8A020"/>
</svg>"""

CHECK_SVG = """<svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px;flex-shrink:0">
  <circle cx="8" cy="8" r="6.5" stroke="#7C80ED" stroke-width="1.3"/>
  <path d="M5 8 L7 10 L11 6" stroke="#7C80ED" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────


def journey_state(score):
    """Return stage label and progress percentage based on health score."""
    if score < 40:
        return "Başlangıç", 25
    if score < 70:
        return "Aktif", 50
    if score < 90:
        return "Olgunlaşma", 75
    return "Hazır", 100

def score_label(score):
    if score >= 80: return "Mükemmel — Neredeyse Hazır"
    if score >= 60: return "Orta — Geliştirilmeli"
    if score >= 40: return "Zayıf — Dikkat Gerekli"
    return "Kritik — Hemen Müdahale"

def parse_months(ready_in_str):
    """Extract a rough 0-1 progress from ready_in text."""
    text = ready_in_str.lower()
    nums = [int(s) for s in text.split() if s.isdigit()]
    if nums:
        low = nums[0]
        high = nums[-1] if len(nums) > 1 else low
        avg = (low + high) / 2
        progress = max(0.05, min(0.95, 1 - (avg / 12)))
        return progress, avg
    return 0.3, 4

def dots_html(progress, total=20):
    filled = max(1, round(progress * total))
    dots = []
    for i in range(total):
        if i < filled - 1:
            dots.append('<span class="mdot filled"></span>')
        elif i == filled - 1:
            dots.append('<span class="mdot active"></span>')
        else:
            dots.append('<span class="mdot"></span>')
    return "".join(dots)

def tri(color): 
    return f'<span class="bullet-tri" style="border-left-color:{color}"></span>'

def circle(color):
    return f'<span class="bullet-circle" style="background:{color}"></span>'

PALETTE = ["#464CE6", "#7C80ED", "#B2B4F4"]


# ─────────────────────────────────────────────
# PAGE: HERO
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero-card">
  {HERO_PATTERN}
  <div style="position:relative;z-index:1">
    {HERO_SVG}
    <div class="hero-title">Smart Compost<br><em>Coach</em></div>
    <div class="hero-sub">Fotoğrafını yükle, kompostunu analiz et.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PAGE: UPLOAD SECTION
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="upload-zone">
  {UPLOAD_SVG}
  <div class="upload-title"><strong>Fotoğraf seç</strong> veya sürükle bırak</div>
  <div class="upload-hint">JPG, PNG • Kompost yığınının üstten çekilmiş fotoğrafı</div>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Fotoğraf Yükle",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

if st.button("🔍  Kompostu Analiz Et"):
    if uploaded_file is None:
        st.warning("Lütfen önce bir kompost fotoğrafı yükleyin.")
    else:
        image = Image.open(uploaded_file)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = """
Analyze the compost image and return ONLY valid JSON with this exact structure:
{
  "health_score": 0,
  "moisture": "",
  "balance": "",
  "ready_in": "",
  "problems": [],
  "recommendations": []
}
Rules:
* health_score: integer 0-100
* moisture: one of — Kuru, Optimal, Islak
* balance: one of — Karbon Fazla, Dengeli, Azot Fazla
* ready_in: short Turkish time estimate e.g. "3-6 ay"
* max 2 problems (in Turkish)
* max 3 recommendations (in Turkish)
* no explanation outside JSON
"""

        with st.spinner("Kompostun analiz ediliyor..."):
            try:
                response = model.generate_content([prompt, image])
                clean = response.text.strip().replace("```json","").replace("```","")
                data = json.loads(clean)

                score = data["health_score"]
                progress, avg_months = parse_months(data.get("ready_in","4 ay"))
                bar_pct = int(progress * 100)

                # ── HEALTH CARD ──
                st.markdown(f"""
<div class="health-card">
  {WORM_SVG}
  <div class="health-text-block">
    <h4>Health Score</h4>
    <div class="health-score-num">{score}<span>/100</span></div>
    <div class="health-status-label">{score_label(score)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

                # ── METRICS ──
                st.markdown(f"""
<div class="metrics-grid">
  <div class="metric-card">
    {MOISTURE_SVG}
    <div class="metric-label">Nem Durumu</div>
    <div class="metric-value">{data["moisture"]}</div>
  </div>
  <div class="metric-card">
    {BALANCE_SVG}
    <div class="metric-label">Karbon/Azot</div>
    <div class="metric-value" style="font-size:17px">{data["balance"]}</div>
  </div>
</div>
""", unsafe_allow_html=True)

                # ── MATURITY BAR ──
                st.markdown(f"""
<div class="maturity-card">
  <div class="maturity-header">
    <span class="maturity-label">Tahmini Olgunlaşma</span>
    <span class="maturity-value">{data["ready_in"]}</span>
  </div>
  <div class="maturity-track">
    <div class="maturity-fill" style="width:{bar_pct}%"></div>
  </div>
  <div class="maturity-dots">{dots_html(progress)}</div>
</div>
""", unsafe_allow_html=True)

                # ── COMPOST JOURNEY ──
                current_stage, journey_pct = journey_state(score)

                start_class = "active" if current_stage == "Başlangıç" else ""
                active_class = "active" if current_stage == "Aktif" else ""
                mature_class = "active" if current_stage == "Olgunlaşma" else ""
                ready_class = "active" if current_stage == "Hazır" else ""

                st.markdown(f"""
<div class="journey-card">
  <div class="journey-title">🌱 Compost Journey</div>

  <div class="journey-row">
    <span class="journey-step {start_class}">🌱 Başlangıç</span>
    <span class="journey-step {active_class}">🪱 Aktif</span>
    <span class="journey-step {mature_class}">🌿 Olgunlaşma</span>
    <span class="journey-step {ready_class}">✅ Hazır</span>
  </div>

  <div class="journey-track">
    <div class="journey-fill" style="width:{journey_pct}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)

                # ── DAILY CHECK-IN ──
                st.markdown("""
<div class="check-card">
  <div class="check-title">✅ Günlük Kontrol</div>
  <div class="check-sub">Bugünkü küçük görev: kompostu havalandırmayı unutma.</div>
</div>
""", unsafe_allow_html=True)

                turned_today = st.radio(
                    "Bugün kompostu çevirdin mi?",
                    ["Henüz Değil", "Evet"],
                    horizontal=True
                )

                if turned_today == "Evet":
                    st.success("Harika! Kompostun daha sağlıklı hale geliyor 🌱")
                    st.balloons()
                else:
                    st.info("Kompostu çevirmek havalanmayı artırır ve ayrışmayı hızlandırır.")

                # ── SIDE-BY-SIDE PANELS ──
                probs = data.get("problems", [])
                recs  = data.get("recommendations", [])

                prob_items = "".join([
                    f'<div class="panel-item">{tri("#E8A020")}<span>{p}</span></div>'
                    for p in probs[:2]
                ])
                rec_items = "".join([
                    f'<div class="panel-item">{tri("#7C80ED")}<span>{r}</span></div>'
                    for r in recs[:2]
                ])

                st.markdown(f"""
<div class="panels-row">
  <div class="panel-card">
    <div class="panel-header problems">
      {WARNING_SVG}
      <span class="panel-title">Sorunlar</span>
      <span class="panel-badge badge-amber">{len(probs)}</span>
    </div>
    <div class="panel-preview">{prob_items}</div>
  </div>
  <div class="panel-card">
    <div class="panel-header recs">
      {CHECK_SVG}
      <span class="panel-title">Öneriler</span>
      <span class="panel-badge badge-blue">{len(recs)}</span>
    </div>
    <div class="panel-preview">{rec_items}</div>
  </div>
</div>
""", unsafe_allow_html=True)

                # ── EXPANDED: ALL PROBLEMS ──
                if probs:
                    items_html = "".join([
                        f'<div class="detail-item">{circle(["#E8A020","#FFB84D"][i%2])}<span>{p}</span></div>'
                        for i, p in enumerate(probs)
                    ])
                    st.markdown(f"""
<div class="detail-card">
  <div class="detail-title">
    {WARNING_SVG}
    Olası Sorunlar
  </div>
  {items_html}
</div>
""", unsafe_allow_html=True)

                # ── EXPANDED: ALL RECS ──
                if recs:
                    items_html = "".join([
                        f'<div class="detail-item">{circle(PALETTE[i%3])}<span>{r}</span></div>'
                        for i, r in enumerate(recs)
                    ])
                    st.markdown(f"""
<div class="detail-card">
  <div class="detail-title">
    {CHECK_SVG}
    Öneriler
  </div>
  {items_html}
</div>
""", unsafe_allow_html=True)

                # ── UPLOADED PHOTO ──
                st.markdown("""
<div class="photo-card">
  <div class="photo-card-header">Yüklenen Fotoğraf</div>
""", unsafe_allow_html=True)
                st.image(image, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Analiz sırasında hata oluştu: {e}")
