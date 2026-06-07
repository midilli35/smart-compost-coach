import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import re
from datetime import date, timedelta

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.set_page_config(
    page_title="Smart Compost Coach",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
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
  --dark:      #242428;
  --mid:       #5A5A66;
  --light:     #8A8A98;
  --page-bg:   #F7F4EE;
  --line:      #EDE8DC;
}

.stApp, .main, .block-container {
  background: var(--page-bg) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.block-container {
  padding-top: 1.2rem !important;
  padding-bottom: 3rem !important;
  max-width: 540px !important;
}
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
.stAlert { border-radius: 16px !important; }
.stFileUploader label { display: none !important; }

/* Allow fixed positioning to work inside Streamlit */
.stApp > iframe, [data-testid="stAppViewContainer"] {
  overflow: visible !important;
}

/* Hero */
.hero-card {
  background: linear-gradient(140deg, var(--cream) 0%, var(--mustard) 100%);
  border-radius: 26px;
  padding: 22px 22px 18px;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(232,101,10,0.08);
}
.hero-pattern {
  position: absolute;
  top: 0; right: 0;
  width: 150px; height: 100%;
  opacity: 0.16;
  pointer-events: none;
}
.hero-title {
  font-size: 30px;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--dark);
  line-height: 1.08;
  position: relative;
  z-index: 1;
}
.hero-sub {
  font-size: 13px;
  color: #666;
  margin-top: 8px;
  position: relative;
  z-index: 1;
}

/* Cards */
.card {
  background: white;
  border-radius: 22px;
  padding: 18px;
  border: 1px solid var(--line);
  margin-bottom: 14px;
  box-shadow: 0 8px 26px rgba(70,76,230,0.045);
}
.card.soft {
  background: #FFFDF7;
}
.card-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--dark);
  margin-bottom: 6px;
  letter-spacing: -0.02em;
}
.card-sub {
  font-size: 12px;
  color: var(--mid);
  line-height: 1.45;
  margin-bottom: 12px;
}
.card-head {
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
  gap:12px;
  margin-bottom:10px;
}
.icon-chip {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--cream);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* My Compost */
.compost-summary {
  display:grid;
  grid-template-columns: 1.15fr .85fr;
  gap:12px;
  margin-top:12px;
}
.summary-main {
  background: linear-gradient(140deg, #FFF2CC, #FFD580);
  border: 1px solid #F2D18C;
  border-radius: 20px;
  padding: 16px;
}
.summary-side {
  background: #F0F1FF;
  border: 1px solid #DADCFB;
  border-radius: 20px;
  padding: 16px;
}
.summary-label {
  font-size: 10px;
  color: var(--light);
  text-transform: uppercase;
  letter-spacing: .06em;
  font-weight: 800;
}
.summary-value {
  font-size: 30px;
  font-weight: 800;
  color: var(--dark);
  letter-spacing: -.06em;
  line-height: 1.05;
  margin-top: 4px;
}
.summary-note {
  font-size: 11px;
  color: var(--mid);
  margin-top: 6px;
}
.meta-row {
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-top:12px;
}
.meta-pill {
  background:#F8F6EF;
  border:1px solid var(--line);
  color:var(--mid);
  border-radius:999px;
  padding:7px 10px;
  font-size:11px;
  font-weight:700;
}

/* Journey */
.journey-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--light);
  margin: 12px 0 10px;
}
.journey-step.active {
  color: var(--royal);
  font-weight: 800;
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

/* Check-in */
.check-card {
  background: #FFFDF7;
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 18px;
  margin-bottom: 14px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.035);
}
.check-title {
  font-size: 17px;
  font-weight: 800;
  color: var(--dark);
  margin-bottom: 4px;
  letter-spacing: -0.02em;
}
.check-sub {
  font-size: 12px;
  color: var(--mid);
  margin-bottom: 12px;
}
.success-note {
  background: var(--mist);
  border: 1px solid #DADCFB;
  color: var(--royal);
  border-radius: 18px;
  padding: 14px 16px;
  font-size: 13px;
  font-weight: 700;
  margin-top: 10px;
  margin-bottom: 14px;
  box-shadow: 4px 4px 0 rgba(178,180,244,0.45);
}
.info-note {
  background: #FFF7E6;
  border: 1px solid #F2E2B8;
  color: #7A5E20;
  border-radius: 18px;
  padding: 14px 16px;
  font-size: 13px;
  margin-top: 10px;
  margin-bottom: 14px;
}

/* Buttons */
div[data-testid="stButton"] > button {
  width: 100% !important;
  padding: 13px 18px !important;
  border-radius: 999px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 14px !important;
  font-weight: 800 !important;
  border: 1.5px solid var(--royal) !important;
  color: var(--royal) !important;
  background: white !important;
  transition: transform 0.12s ease, box-shadow 0.12s ease !important;
  box-shadow: none !important;
}
div[data-testid="stButton"] > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 8px 18px rgba(70,76,230,0.12) !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
  background: var(--orange) !important;
  color: white !important;
  border-color: var(--orange) !important;
}

/* Upload */
.upload-zone {
  border: 1.5px dashed #C8B88A;
  border-radius: 18px;
  padding: 12px 14px;
  background: #FFFDF7;
  margin-bottom: 10px;
}
.upload-title {
  font-size: 14px;
  color: var(--mid);
  font-weight: 800;
}
.upload-hint {
  font-size: 11px;
  color: #AAA;
  margin-top: 3px;
}
.stFileUploader [data-testid="stFileUploaderDropzone"] {
  background: #FFFDF7 !important;
  border: 1.5px dashed #C8B88A !important;
  border-radius: 18px !important;
  min-height: 58px !important;
  padding: 10px !important;
}

/* Health */
.health-card {
  background: var(--mustard);
  border-radius: 24px;
  padding: 20px;
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 10px 24px rgba(232,101,10,0.08);
}
.health-icon-small {
  width:56px;
  height:56px;
  border-radius:50%;
  background:#FFE9BD;
  display:flex;
  align-items:center;
  justify-content:center;
  flex-shrink:0;
}
.health-text-block h4 {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #7A5E20;
  font-weight: 800;
  margin: 0;
}
.health-score-num {
  font-size: 52px;
  font-weight: 800;
  color: var(--dark);
  line-height: 1;
  margin: 2px 0;
  letter-spacing: -0.06em;
}
.health-score-num span {
  font-size: 20px;
  color: #7A5E20;
  letter-spacing: -0.02em;
}
.health-status-label {
  font-size: 12px;
  color: #7A5E20;
  font-weight: 700;
}

/* Metrics */
.metrics-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}
.metric-card {
  background: white;
  border-radius: 18px;
  padding: 14px;
  border: 1px solid var(--line);
  box-shadow: 0 8px 22px rgba(70,76,230,0.04);
}
.metric-label {
  font-size: 10px;
  color: var(--light);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 800;
  margin-bottom: 4px;
}
.metric-value {
  font-size: 20px;
  font-weight: 800;
  color: var(--dark);
  letter-spacing: -0.04em;
}

/* Maturity */
.maturity-card {
  background: white;
  border-radius: 20px;
  padding: 16px 18px;
  margin-bottom: 14px;
  border: 1px solid var(--line);
  box-shadow: 0 8px 22px rgba(70,76,230,0.04);
}
.maturity-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 10px;
}
.maturity-label {
  font-size: 10px;
  color: var(--light);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 800;
}
.maturity-value {
  font-size: 14px;
  color: var(--royal);
  font-weight: 800;
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
}
.mdot.filled { background: var(--peri); }
.mdot.active { background: var(--royal); transform: scale(1.3); }

/* Summary cards */
.panels-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}
.panel-card {
  background: white;
  border-radius: 18px;
  border: 1px solid var(--line);
  overflow: hidden;
  box-shadow: 0 10px 26px rgba(70,76,230,0.045);
}
.panel-header {
  padding: 12px 14px 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.panel-header.problems { border-bottom: 2px solid var(--cream); }
.panel-header.recs { border-bottom: 2px solid var(--mist); }
.panel-title { font-size: 13px; font-weight: 800; color: var(--dark); }
.panel-badge {
  margin-left: auto;
  font-size: 10px;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 99px;
}
.badge-amber { background: #FFF0C8; color: #9A6700; }
.badge-blue  { background: var(--mist); color: var(--royal); }
.panel-preview {
  padding: 8px 14px 12px;
  font-size: 12px;
  color: var(--mid);
  line-height: 1.55;
}
.panel-item {
  display: flex;
  gap: 7px;
  margin-bottom: 6px;
  align-items: flex-start;
}
.bullet-tri {
  flex-shrink: 0;
  margin-top: 5px;
  width: 0; height: 0;
  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
  border-left: 8px solid;
}
.bullet-circle {
  flex-shrink: 0;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-top: 5px;
}

/* Bottom sheet simulation */
.sheet-card {
  background: white;
  border-radius: 26px 26px 18px 18px;
  border: 2px solid var(--mist);
  padding: 18px 18px 16px;
  margin: 14px 0;
  box-shadow: 0 -6px 0 rgba(178,180,244,0.35), 0 18px 38px rgba(70,76,230,0.10);
  animation: sheetUp 0.28s ease-out;
}
@keyframes sheetUp {
  from { transform: translateY(28px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}
.sheet-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.sheet-title {
  font-size: 18px;
  font-weight: 800;
  color: var(--royal);
  letter-spacing: -0.03em;
}
.sheet-x {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #F6F6FF;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--royal);
  font-weight: 800;
}
.sheet-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: flex-start;
  font-size: 13px;
  color: var(--mid);
  line-height: 1.5;
}
.sheet-mini-grid {
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:12px;
}
.sheet-mini {
  background:#F8F8FF;
  border:1px solid var(--mist);
  border-radius:16px;
  padding:14px;
}
.sheet-mini-label {
  font-size:10px;
  color:var(--light);
  text-transform:uppercase;
  letter-spacing:.06em;
  font-weight:800;
}
.sheet-mini-value {
  font-size:18px;
  color:var(--dark);
  font-weight:800;
  margin-top:4px;
}

/* Photo */
.photo-card {
  background: white;
  border-radius: 18px;
  border: 1px solid var(--line);
  overflow: hidden;
  margin-bottom: 12px;
}
.photo-card-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--line);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--light);
  font-weight: 800;

/* Modal Overlay */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(30, 30, 50, 0.52);
  backdrop-filter: blur(3px);
  z-index: 9998;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 48px;
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}
.modal-box {
  background: white;
  border-radius: 28px;
  width: min(500px, 92vw);
  max-height: 82vh;
  overflow-y: auto;
  padding: 22px 20px 24px;
  position: relative;
  box-shadow: 0 24px 60px rgba(30,30,80,0.22), 0 2px 8px rgba(70,76,230,0.10);
  animation: slideDown 0.25s cubic-bezier(0.4,0,0.2,1);
  z-index: 9999;
}
@keyframes slideDown {
  from { transform: translateY(-28px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.modal-title {
  font-size: 19px;
  font-weight: 800;
  color: var(--royal);
  letter-spacing: -0.03em;
}
.modal-close-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #F0F1FF;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  color: var(--royal);
  font-weight: 800;
  flex-shrink: 0;
  transition: background 0.15s;
}
.modal-close-btn:hover {
  background: var(--mist);
}
}
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

SPROUT_SVG = """
<svg viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:30px;height:30px">
  <path d="M22 34 L22 19" stroke="#5A8A40" stroke-width="2.2" stroke-linecap="round"/>
  <path d="M22 22 Q15 18 14 11 Q21 11 25 17 Q26 20 22 22Z" fill="#7ABD5A"/>
  <path d="M22 27 Q29 22 31 15 Q24 14 20 21 Q19 24 22 27Z" fill="#5A8A40"/>
</svg>"""

MOISTURE_SVG = """
<svg viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:26px;height:26px;margin-bottom:6px">
  <path d="M13 4 Q10 8 8 12 Q6 16 8 20 Q10 24 13 24 Q16 24 18 20 Q20 16 18 12 Q16 8 13 4Z"
        fill="#B2D4F4" stroke="#464CE6" stroke-width="1.2"/>
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

def score_label(score):
    if score >= 80:
        return "Mükemmel — Neredeyse Hazır"
    if score >= 60:
        return "Orta — Geliştirilmeli"
    if score >= 40:
        return "Zayıf — Dikkat Gerekli"
    return "Kritik — Hemen Müdahale"


def parse_months(ready_in_str):
    text = ready_in_str.lower().replace("-", " ")
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


def turning_interval_days(compost_type):
    if "Sıcak" in compost_type:
        return 3
    if "Bahçe" in compost_type:
        return 7
    return 10


def turning_message(days_until):
    if days_until < 0:
        return f"{abs(days_until)} gün gecikti"
    if days_until == 0:
        return "Bugün"
    if days_until == 1:
        return "Yarın"
    return f"{days_until} gün sonra"


def last_turn_message(days_since_turn):
    if days_since_turn == 0:
        return "Bugün"
    if days_since_turn == 1:
        return "Dün"
    return f"{days_since_turn} gün önce"


def journey_from_age(age_days, compost_type):
    total_days = 90 if "Sıcak" in compost_type else 180
    pct = max(8, min(95, int((age_days / total_days) * 100)))
    if pct < 25:
        stage = "Başlangıç"
    elif pct < 65:
        stage = "Aktif"
    elif pct < 90:
        stage = "Olgunlaşma"
    else:
        stage = "Hazır"
    return stage, pct


def make_short_label(text, max_words=3):
    words = re.sub(r"[.!?]", "", str(text)).split()
    return " ".join(words[:max_words])

PALETTE = ["#464CE6", "#7C80ED", "#B2B4F4"]

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
today = date.today()
if "sheet" not in st.session_state:
    st.session_state.sheet = None
if "care_done" not in st.session_state:
    st.session_state.care_done = False
if "edit_open" not in st.session_state:
    st.session_state.edit_open = False
if "analysis_open" not in st.session_state:
    st.session_state.analysis_open = False
if "compost_type" not in st.session_state:
    st.session_state.compost_type = "Ev tipi / soğuk kompost"
if "start_date" not in st.session_state:
    st.session_state.start_date = today - timedelta(days=22)
if "last_turn_date" not in st.session_state:
    st.session_state.last_turn_date = today - timedelta(days=3)
if "material_amount" not in st.session_state:
    st.session_state.material_amount = 2.0
if "ai_data" not in st.session_state:
    st.session_state.ai_data = None
if "ai_image" not in st.session_state:
    st.session_state.ai_image = None

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="hero-card">
  {HERO_PATTERN}
  <div style="position:relative;z-index:1">
    {HERO_SVG}
    <div class="hero-title">Smart Compost<br>Coach</div>
    <div class="hero-sub">Kompostunu takip et, fotoğrafla analiz et.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RULE-BASED VALUES
# ─────────────────────────────────────────────
compost_type = st.session_state.compost_type
start_date = st.session_state.start_date
last_turn_date = st.session_state.last_turn_date
material_amount = st.session_state.material_amount

age_days = max(0, (date.today() - start_date).days)
interval = turning_interval_days(compost_type)
days_since_turn = max(0, (date.today() - last_turn_date).days)
last_turn_text = last_turn_message(days_since_turn)
next_turn_date = last_turn_date + timedelta(days=interval)
days_until_turn = (next_turn_date - date.today()).days
turn_label = turning_message(days_until_turn)
rule_stage, rule_journey_pct = journey_from_age(age_days, compost_type)

# ─────────────────────────────────────────────
# ANALYSIS MODAL OVERLAY
# ─────────────────────────────────────────────
if st.session_state.analysis_open:
    # Render the overlay backdrop + modal box via HTML
    st.markdown("""
<div class="modal-overlay">
  <div class="modal-box">
    <div class="modal-header">
      <div class="modal-title">📷 Kompostunu Analiz Et</div>
    </div>
    <div class="upload-zone">
      <div class="upload-title">Fotoğraf yükle</div>
      <div class="upload-hint">Fotoğraf seç veya sürükle bırak • JPG, PNG</div>
    </div>
""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Fotoğraf Yükle",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    col_analyze, col_close = st.columns([3, 1])
    with col_analyze:
        analyze_clicked = st.button("🔍 Kompostu Analiz Et", type="primary", use_container_width=True)
    with col_close:
        close_analysis_clicked = st.button("✕ Kapat", use_container_width=True, key="close_analysis")

    st.markdown("</div></div>", unsafe_allow_html=True)

    if close_analysis_clicked:
        st.session_state.analysis_open = False
        st.rerun()

    if analyze_clicked:
        if uploaded_file is None:
            st.warning("Lütfen önce bir kompost fotoğrafı yükleyin.")
        else:
            image = Image.open(uploaded_file)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = f"""
Analyze the compost image and the user's compost tracking data.
Return ONLY valid JSON with this exact structure:
{{
  "health_score": 0,
  "moisture": "",
  "balance": "",
  "ready_in": "",
  "problems": [],
  "recommendations": []
}}

User tracking data:
- Compost type: {compost_type}
- Start date: {start_date}
- Compost age: {age_days} days
- Current journey stage: {rule_stage}
- Last turning date: {last_turn_date}
- Days since last turning: {days_since_turn}
- Next turning due in: {days_until_turn} days
- Approximate material amount: {material_amount} kg

Rules:
* health_score: integer 0-100
* moisture: one of — Kuru, Optimal, Islak
* balance: one of — Karbon Fazla, Dengeli, Azot Fazla
* ready_in: short Turkish time estimate e.g. "3-6 ay"
* problems: max 2 items, each max 3 words, in Turkish
* recommendations: max 3 items, each max 3 words, in Turkish
* no explanation outside JSON
"""

            with st.spinner("Kompostun analiz ediliyor..."):
                try:
                    response = model.generate_content([prompt, image])
                    clean = response.text.strip().replace("```json", "").replace("```", "")
                    data = json.loads(clean)
                    st.session_state.ai_data = data
                    st.session_state.ai_image = image.copy()
                    st.session_state.analysis_open = False
                    st.session_state.sheet = None
                    st.rerun()

                except Exception as e:
                    st.error(f"Analiz sırasında hata oluştu: {e}")



# ─────────────────────────────────────────────
# MY COMPOST DASHBOARD
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="card">
  <div class="card-head">
    <div>
      <div class="card-title">My Compost</div>
      <div class="card-sub">Kompost bilgilerini kaydet; takip ve AI analizi buna göre güncellensin.</div>
    </div>
    <div class="icon-chip">{SPROUT_SVG}</div>
  </div>

  <div class="compost-summary">
    <div class="summary-main">
      <div class="summary-label">Kompost Yaşı</div>
      <div class="summary-value">{age_days} gün</div>
      <div class="summary-note">{rule_stage} dönemi</div>
    </div>
    <div class="summary-side">
      <div class="summary-label">Sonraki Çevirme</div>
      <div class="summary-value" style="font-size:22px;letter-spacing:-.04em;">{turn_label}</div>
      <div class="summary-note">Son çevirme: {last_turn_text}</div>
    </div>
  </div>

  <div class="card-title" style="font-size:15px;margin-top:16px;">Compost Journey</div>
  <div class="journey-row">
    <span class="journey-step {'active' if rule_stage == 'Başlangıç' else ''}">Başlangıç</span>
    <span class="journey-step {'active' if rule_stage == 'Aktif' else ''}">Aktif</span>
    <span class="journey-step {'active' if rule_stage == 'Olgunlaşma' else ''}">Olgunlaşma</span>
    <span class="journey-step {'active' if rule_stage == 'Hazır' else ''}">Hazır</span>
  </div>
  <div class="journey-track">
    <div class="journey-fill" style="width:{rule_journey_pct}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)

# Clickable compost info pills
p1, p2, p3 = st.columns([1.4, 1.0, 1.2])
with p1:
    if st.button(compost_type, use_container_width=True, key="edit_type_pill"):
        st.session_state.edit_open = True
        st.session_state.analysis_open = False
        st.session_state.sheet = None
        st.rerun()

with p2:
    if st.button(f"Yaklaşık {material_amount:.1f} kg", use_container_width=True, key="edit_amount_pill"):
        st.session_state.edit_open = True
        st.session_state.analysis_open = False
        st.session_state.sheet = None
        st.rerun()

with p3:
    if st.button(f"Başlangıç: {start_date.strftime('%d.%m.%Y')}", use_container_width=True, key="edit_start_pill"):
        st.session_state.edit_open = True
        st.session_state.analysis_open = False
        st.session_state.sheet = None
        st.rerun()

if st.button("📷 Kompostunu Analiz Et", use_container_width=True, key="open_analysis_main"):
    st.session_state.analysis_open = True
    st.session_state.edit_open = False
    st.session_state.sheet = None
    st.rerun()

# ─────────────────────────────────────────────
# EDIT PANEL
# ─────────────────────────────────────────────
if st.session_state.edit_open:
    edit_close_cols = st.columns([8, 1])
    with edit_close_cols[1]:
        if st.button("✕", key="close_edit_panel"):
            st.session_state.edit_open = False
            st.rerun()

    st.markdown("""
<div class="sheet-card">
  <div class="sheet-head">
    <div class="sheet-title">Kompost Bilgileri</div>
  </div>
""", unsafe_allow_html=True)

    with st.form("compost_info_form"):
        new_type = st.selectbox(
            "Kompost tipi",
            ["Ev tipi / soğuk kompost", "Bahçe tipi / soğuk kompost", "Sıcak kompost"],
            index=["Ev tipi / soğuk kompost", "Bahçe tipi / soğuk kompost", "Sıcak kompost"].index(st.session_state.compost_type)
        )
        f1, f2 = st.columns(2)
        with f1:
            new_start = st.date_input("Başlangıç tarihi", value=st.session_state.start_date)
        with f2:
            new_turn = st.date_input("Son çevirme tarihi", value=st.session_state.last_turn_date)
        new_amount = st.number_input(
            "Yaklaşık materyal miktarı (kg)",
            min_value=0.0,
            value=float(st.session_state.material_amount),
            step=0.5
        )
        saved = st.form_submit_button("Kaydet")

        if saved:
            st.session_state.compost_type = new_type
            st.session_state.start_date = new_start
            st.session_state.last_turn_date = new_turn
            st.session_state.material_amount = new_amount
            st.session_state.edit_open = False
            st.success("Bilgiler güncellendi.")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DAILY CHECK-IN
# ─────────────────────────────────────────────
st.markdown("""
<div class="check-card">
  <div class="check-title">Günlük Kontrol</div>
  <div class="check-sub">Bugün kompostu havalandırdın mı?</div>
</div>
""", unsafe_allow_html=True)

b1, b2 = st.columns(2)
with b1:
    later_clicked = st.button("Daha Sonra", use_container_width=True)
with b2:
    done_clicked = st.button("✓ Çevirdim", use_container_width=True)

if done_clicked:
    st.session_state.care_done = True
    st.session_state.last_turn_date = date.today()
    st.balloons()
    st.rerun()

if later_clicked:
    st.session_state.care_done = False

if st.session_state.care_done:
    st.markdown("""
<div class="success-note">
  Güzel iş! Bugünkü bakım tamamlandı. Kompostun bugün biraz daha nefes aldı.
</div>
""", unsafe_allow_html=True)
else:
    st.markdown("""
<div class="info-note">
  Havalandırma, ayrışmayı hızlandırır ve kötü koku riskini azaltır.
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# AI RESULTS
# ─────────────────────────────────────────────
if st.session_state.ai_data is not None:
    data = st.session_state.ai_data
    image = st.session_state.ai_image
    score = data["health_score"]
    progress, avg_months = parse_months(data.get("ready_in", "4 ay"))
    bar_pct = int(progress * 100)
    probs = data.get("problems", [])
    recs = data.get("recommendations", [])

    st.markdown(f"""
<div class="health-card">
  <div class="health-icon-small">{SPROUT_SVG}</div>
  <div class="health-text-block">
    <h4>Health Score</h4>
    <div class="health-score-num">{score}<span>/100</span></div>
    <div class="health-status-label">{score_label(score)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

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

    prob_items = "".join([
        f'<div class="panel-item">{tri("#E8A020")}<span>{make_short_label(p)}</span></div>'
        for p in probs[:2]
    ])
    rec_items = "".join([
        f'<div class="panel-item">{tri("#7C80ED")}<span>{make_short_label(r)}</span></div>'
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

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        if st.button("Sorunlar", use_container_width=True):
            st.session_state.sheet = "problems"
    with s2:
        if st.button("Öneriler", use_container_width=True):
            st.session_state.sheet = "recommendations"
    with s3:
        if st.button("Durum", use_container_width=True):
            st.session_state.sheet = "status"
    with s4:
        if st.button("Fotoğraf", use_container_width=True):
            st.session_state.sheet = "photo"

    # ── Sheet modals ──────────────────────────────
    if st.session_state.sheet:
        sheet_close_col1, sheet_close_col2 = st.columns([8, 1])
        with sheet_close_col2:
            if st.button("✕", key="close_sheet_btn"):
                st.session_state.sheet = None
                st.rerun()

    if st.session_state.sheet == "problems":
        items = "".join([
            f'<div class="sheet-item">{circle("#E8A020")}<span>{p}</span></div>'
            for p in probs
        ]) or '<div class="sheet-item"><span>Belirgin sorun yok.</span></div>'
        st.markdown(f"""
<div class="modal-overlay">
  <div class="modal-box">
    <div class="modal-header">
      <div class="modal-title">⚠️ Sorunlar</div>
    </div>
    {items}
  </div>
</div>
""", unsafe_allow_html=True)

    elif st.session_state.sheet == "recommendations":
        items = "".join([
            f'<div class="sheet-item">{circle(PALETTE[i % 3])}<span>{r}</span></div>'
            for i, r in enumerate(recs)
        ]) or '<div class="sheet-item"><span>Öneri bulunamadı.</span></div>'
        st.markdown(f"""
<div class="modal-overlay">
  <div class="modal-box">
    <div class="modal-header">
      <div class="modal-title">✅ Öneriler</div>
    </div>
    {items}
  </div>
</div>
""", unsafe_allow_html=True)

    elif st.session_state.sheet == "status":
        st.markdown(f"""
<div class="modal-overlay">
  <div class="modal-box">
    <div class="modal-header">
      <div class="modal-title">📊 Kompost Durumu</div>
    </div>
    <div class="sheet-mini-grid">
      <div class="sheet-mini">
        <div class="sheet-mini-label">Nem</div>
        <div class="sheet-mini-value">{data["moisture"]}</div>
      </div>
      <div class="sheet-mini">
        <div class="sheet-mini-label">C/N Dengesi</div>
        <div class="sheet-mini-value">{data["balance"]}</div>
      </div>
      <div class="sheet-mini">
        <div class="sheet-mini-label">Kompost Yaşı</div>
        <div class="sheet-mini-value">{age_days} gün</div>
      </div>
      <div class="sheet-mini">
        <div class="sheet-mini-label">Sonraki Çevirme</div>
        <div class="sheet-mini-value">{turn_label}</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    elif st.session_state.sheet == "photo":
        st.markdown("""
<div class="modal-overlay">
  <div class="modal-box">
    <div class="modal-header">
      <div class="modal-title">🖼️ Yüklenen Fotoğraf</div>
    </div>
""", unsafe_allow_html=True)
        if image is not None:
            st.image(image, use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

