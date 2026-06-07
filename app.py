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
  --mustard:#FFD580; --cream:#FFE9BD; --royal:#464CE6; --peri:#7C80ED;
  --lavender:#B2B4F4; --mist:#E8E8FC; --sage:#B8CCB6; --pale-sage:#DBE5DA;
  --orange:#E8650A; --orange-dk:#C8560A; --dark:#242428; --mid:#5A5A66;
  --light:#8A8A98; --page-bg:#F7F4EE; --line:#EDE8DC;
}
.stApp, .main, .block-container {
  background:var(--page-bg) !important;
  font-family:'Plus Jakarta Sans', sans-serif !important;
}
.block-container { padding-top:1.2rem !important; padding-bottom:3rem !important; max-width:540px !important; }
header[data-testid="stHeader"], footer { display:none !important; }
.stFileUploader label { display:none !important; }
.stAlert { border-radius:16px !important; }

/* Hero */
.hero-card {
  background:linear-gradient(140deg,var(--cream) 0%,var(--mustard) 100%);
  border-radius:28px; padding:22px; margin-bottom:14px; position:relative; overflow:hidden;
  box-shadow:0 10px 30px rgba(232,101,10,0.08);
}
.hero-pattern { position:absolute; top:0; right:0; width:150px; height:100%; opacity:.16; pointer-events:none; }
.hero-title { font-size:30px; font-weight:800; letter-spacing:-.04em; color:var(--dark); line-height:1.08; position:relative; z-index:1; }
.hero-sub { font-size:13px; color:#666; margin-top:8px; position:relative; z-index:1; }
.inline-icon { width:44px; height:44px; margin-bottom:8px; }

/* Generic cards */
.card {
  background:white; border-radius:24px; padding:18px; border:1px solid var(--line); margin-bottom:14px;
  box-shadow:0 8px 26px rgba(70,76,230,0.045);
}
.card-title { font-size:17px; font-weight:800; color:var(--dark); margin-bottom:6px; letter-spacing:-.02em; }
.card-sub { font-size:12px; color:var(--mid); line-height:1.45; margin-bottom:12px; }
.section-label { font-size:11px; color:var(--light); text-transform:uppercase; letter-spacing:.08em; font-weight:800; margin:14px 0 7px; }

/* Compost profile */
.profile-card {
  background:linear-gradient(135deg,#FFF8E8 0%, #FFFFFF 72%); border:1px solid #F1E1B5;
  border-radius:24px; padding:18px; margin-bottom:14px; box-shadow:0 10px 28px rgba(232,101,10,.06);
}
.profile-top { display:flex; justify-content:space-between; align-items:flex-start; gap:10px; margin-bottom:14px; }
.profile-title { display:flex; align-items:center; gap:10px; font-size:18px; font-weight:800; letter-spacing:-.03em; color:var(--dark); }
.worm-mini { width:38px; height:38px; flex-shrink:0; }
.edit-pill { background:#F0F1FF; color:var(--royal); border:1px solid #DADCFB; border-radius:99px; padding:6px 10px; font-size:11px; font-weight:800; }
.tracker-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:14px; }
.tracker-mini { background:#FFF7E6; border-radius:18px; padding:13px; border:1px solid #F2E2B8; }
.tracker-mini.alt { background:#F0F1FF; border-color:#DADCFB; }
.tracker-label { font-size:10px; color:var(--light); text-transform:uppercase; letter-spacing:.06em; font-weight:800; }
.tracker-value { font-size:24px; font-weight:800; color:var(--dark); line-height:1.05; margin-top:3px; letter-spacing:-.04em; }
.tracker-note { font-size:11px; color:var(--mid); margin-top:4px; }
.journey-row { display:flex; justify-content:space-between; font-size:11px; color:var(--light); margin:12px 0 10px; }
.journey-step.active { color:var(--royal); font-weight:800; }
.journey-track { height:10px; background:var(--mist); border-radius:999px; overflow:hidden; }
.journey-fill { height:100%; background:linear-gradient(90deg,var(--peri),var(--royal)); border-radius:999px; transition:width 1s ease; }

/* Form panel */
.form-panel {
  background:white; border-radius:26px; border:2px solid var(--mist); padding:18px; margin:10px 0 14px;
  box-shadow:0 -6px 0 rgba(178,180,244,.35),0 18px 38px rgba(70,76,230,.10);
  animation:sheetUp .25s ease-out;
}
.panel-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; }
.panel-title { font-size:18px; font-weight:800; color:var(--royal); letter-spacing:-.03em; }

/* Check-in */
.check-card { background:#FFFDF7; border:1px solid var(--line); border-radius:22px; padding:18px; margin-bottom:14px; box-shadow:0 8px 24px rgba(0,0,0,.035); }
.check-title { font-size:17px; font-weight:800; color:var(--dark); margin-bottom:4px; letter-spacing:-.02em; }
.check-sub { font-size:12px; color:var(--mid); margin-bottom:12px; }
.success-note { background:var(--mist); border:1px solid #DADCFB; color:var(--royal); border-radius:18px; padding:14px 16px; font-size:13px; font-weight:700; margin-top:10px; box-shadow:4px 4px 0 rgba(178,180,244,.45); }
.info-note { background:#FFF7E6; border:1px solid #F2E2B8; color:#7A5E20; border-radius:18px; padding:14px 16px; font-size:13px; margin-top:10px; }

/* Buttons */
div[data-testid="stButton"] > button {
  width:100% !important; padding:13px 18px !important; border-radius:999px !important;
  font-family:'Plus Jakarta Sans', sans-serif !important; font-size:14px !important; font-weight:800 !important;
  border:1.5px solid var(--royal) !important; color:var(--royal) !important; background:white !important;
  transition:transform .12s ease, box-shadow .12s ease !important; box-shadow:none !important;
}
div[data-testid="stButton"] > button:hover { transform:translateY(-1px) !important; box-shadow:0 8px 18px rgba(70,76,230,.12) !important; }
div[data-testid="stButton"] > button[kind="primary"] { background:var(--orange) !important; color:white !important; border-color:var(--orange) !important; }

/* Upload */
.upload-zone { border:1.5px dashed #C8B88A; border-radius:18px; padding:12px 14px; background:#FFFDF7; margin-bottom:10px; }
.upload-title { font-size:14px; color:var(--mid); font-weight:800; }
.upload-hint { font-size:11px; color:#AAA; margin-top:3px; }
.stFileUploader [data-testid="stFileUploaderDropzone"] {
  background:#FFFDF7 !important; border:1.5px dashed #C8B88A !important; border-radius:18px !important;
  min-height:58px !important; padding:10px !important;
}

/* Analysis result */
.health-card { background:var(--mustard); border-radius:24px; padding:20px; margin-bottom:14px; display:flex; align-items:center; gap:18px; box-shadow:0 10px 24px rgba(232,101,10,.08); }
.health-score-num { font-size:52px; font-weight:800; color:var(--dark); line-height:1; margin:2px 0; letter-spacing:-.06em; }
.health-score-num span { font-size:20px; color:#7A5E20; letter-spacing:-.02em; }
.health-text-block h4 { font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:#7A5E20; font-weight:800; margin:0; }
.health-status-label { font-size:12px; color:#7A5E20; font-weight:700; }
.metrics-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:14px; }
.metric-card { background:white; border-radius:18px; padding:14px; border:1px solid var(--line); box-shadow:0 8px 22px rgba(70,76,230,.04); }
.metric-label { font-size:10px; color:var(--light); text-transform:uppercase; letter-spacing:.06em; font-weight:800; margin-bottom:4px; }
.metric-value { font-size:20px; font-weight:800; color:var(--dark); letter-spacing:-.04em; }
.maturity-card { background:white; border-radius:20px; padding:16px 18px; margin-bottom:14px; border:1px solid var(--line); box-shadow:0 8px 22px rgba(70,76,230,.04); }
.maturity-header { display:flex; justify-content:space-between; align-items:baseline; margin-bottom:10px; }
.maturity-label { font-size:10px; color:var(--light); text-transform:uppercase; letter-spacing:.06em; font-weight:800; }
.maturity-value { font-size:14px; color:var(--royal); font-weight:800; }
.maturity-track { height:8px; background:var(--mist); border-radius:99px; overflow:hidden; margin-bottom:10px; }
.maturity-fill { height:100%; background:linear-gradient(90deg,var(--peri),var(--royal)); border-radius:99px; transition:width 1.2s cubic-bezier(.4,0,.2,1); }
.maturity-dots { display:flex; gap:5px; flex-wrap:wrap; }
.mdot { width:8px; height:8px; border-radius:50%; background:var(--mist); display:inline-block; }
.mdot.filled { background:var(--peri); }
.mdot.active { background:var(--royal); transform:scale(1.3); }

/* Summary cards */
.panels-row { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px; }
.panel-card { background:white; border-radius:18px; border:1px solid var(--line); overflow:hidden; box-shadow:0 10px 26px rgba(70,76,230,.045); }
.panel-header { padding:12px 14px 10px; display:flex; align-items:center; gap:8px; }
.panel-header.problems { border-bottom:2px solid var(--cream); }
.panel-header.recs { border-bottom:2px solid var(--mist); }
.panel-title { font-size:13px; font-weight:800; color:var(--dark); }
.panel-badge { margin-left:auto; font-size:10px; font-weight:800; padding:2px 8px; border-radius:99px; }
.badge-amber { background:#FFF0C8; color:#9A6700; }
.badge-blue { background:var(--mist); color:var(--royal); }
.panel-preview { padding:8px 14px 12px; font-size:12px; color:var(--mid); line-height:1.55; }
.panel-item { display:flex; gap:7px; margin-bottom:6px; align-items:flex-start; }
.bullet-tri { flex-shrink:0; margin-top:5px; width:0; height:0; border-top:5px solid transparent; border-bottom:5px solid transparent; border-left:8px solid; }
.bullet-circle { flex-shrink:0; width:8px; height:8px; border-radius:50%; margin-top:5px; }

/* Bottom sheet simulation */
.sheet-card { background:white; border-radius:26px 26px 18px 18px; border:2px solid var(--mist); padding:18px 18px 16px; margin:14px 0; box-shadow:0 -6px 0 rgba(178,180,244,.35),0 18px 38px rgba(70,76,230,.10); animation:sheetUp .28s ease-out; }
@keyframes sheetUp { from { transform:translateY(28px); opacity:0; } to { transform:translateY(0); opacity:1; } }
.sheet-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.sheet-title { font-size:18px; font-weight:800; color:var(--royal); letter-spacing:-.03em; }
.sheet-x { width:34px; height:34px; border-radius:50%; background:#F6F6FF; display:flex; align-items:center; justify-content:center; color:var(--royal); font-weight:800; }
.sheet-item { display:flex; gap:10px; margin-bottom:10px; align-items:flex-start; font-size:13px; color:var(--mid); line-height:1.5; }
.sheet-mini-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.sheet-mini { background:#F8F8FF; border:1px solid var(--mist); border-radius:16px; padding:14px; }
.sheet-mini-label { font-size:10px; color:var(--light); text-transform:uppercase; letter-spacing:.06em; font-weight:800; }
.sheet-mini-value { font-size:18px; color:var(--dark); font-weight:800; margin-top:4px; }
.photo-card { background:white; border-radius:18px; border:1px solid var(--line); overflow:hidden; margin-bottom:12px; }
.photo-card-header { padding:12px 16px; border-bottom:1px solid var(--line); font-size:11px; text-transform:uppercase; letter-spacing:.06em; color:var(--light); font-weight:800; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SVG ILLUSTRATIONS
# ─────────────────────────────────────────────
HERO_SVG = """
<svg viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg" class="inline-icon">
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
</svg>"""

WORM_SVG = """
<svg viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:72px;height:72px;flex-shrink:0">
  <circle cx="36" cy="36" r="32" fill="#FFE9BD"/>
  <rect x="12" y="48" width="48" height="14" rx="4" fill="#C8A060" opacity="0.4"/>
  <path d="M20 50 Q22 44 26 45 Q30 46 28 50 Q26 54 30 53 Q34 52 34 48 Q34 44 38 44" stroke="#E86040" stroke-width="3" fill="none" stroke-linecap="round"/>
  <circle cx="38" cy="43" r="3" fill="#E86040"/>
  <circle cx="39" cy="42" r="1" fill="white"/>
  <path d="M48 47 L48 38" stroke="#5A8A40" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M48 41 Q44 38 43 34 Q47 33 49 37Z" fill="#7ABD5A"/>
</svg>"""

WORM_MINI = """
<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" class="worm-mini">
  <circle cx="20" cy="20" r="18" fill="#FFE9BD"/>
  <path d="M10 25 Q13 20 16 22 Q19 24 17 27 Q15 30 20 29 Q24 28 23 24 Q22 20 27 20" stroke="#E86040" stroke-width="2.4" fill="none" stroke-linecap="round"/>
  <circle cx="28" cy="19" r="2.5" fill="#E86040"/>
  <path d="M28 18 L28 12" stroke="#5A8A40" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M28 15 Q24 13 23 10 Q27 9 29 13Z" fill="#7ABD5A"/>
</svg>"""

MOISTURE_SVG = """
<svg viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:26px;height:26px;margin-bottom:6px">
  <path d="M13 4 Q10 8 8 12 Q6 16 8 20 Q10 24 13 24 Q16 24 18 20 Q20 16 18 12 Q16 8 13 4Z" fill="#B2D4F4" stroke="#464CE6" stroke-width="1.2"/>
</svg>"""

BALANCE_SVG = """
<svg viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:26px;height:26px;margin-bottom:6px">
  <rect x="4" y="14" width="7" height="8" rx="2" fill="#B8CCB6" stroke="#5A8A40" stroke-width="1.2"/>
  <rect x="15" y="10" width="7" height="12" rx="2" fill="#FFD580" stroke="#C8A020" stroke-width="1.2"/>
  <path d="M2 22 L24 22" stroke="#ccc" stroke-width="1"/>
</svg>"""

WARNING_SVG = """<svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px;flex-shrink:0"><circle cx="8" cy="8" r="6.5" stroke="#E8A020" stroke-width="1.3"/><path d="M8 5 L8 9" stroke="#E8A020" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="11.5" r="1" fill="#E8A020"/></svg>"""
CHECK_SVG = """<svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px;flex-shrink:0"><circle cx="8" cy="8" r="6.5" stroke="#7C80ED" stroke-width="1.3"/><path d="M5 8 L7 10 L11 6" stroke="#7C80ED" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

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
if "analysis_open" not in st.session_state:
    st.session_state.analysis_open = False
if "edit_open" not in st.session_state:
    st.session_state.edit_open = False
if "care_done" not in st.session_state:
    st.session_state.care_done = False
if "compost_type" not in st.session_state:
    st.session_state.compost_type = "Ev tipi / soğuk kompost"
if "start_date" not in st.session_state:
    st.session_state.start_date = today - timedelta(days=22)
if "last_turn_date" not in st.session_state:
    st.session_state.last_turn_date = today - timedelta(days=3)
if "material_amount" not in st.session_state:
    st.session_state.material_amount = 2.0

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

age_days = max(0, (today - start_date).days)
interval = turning_interval_days(compost_type)
days_since_turn = max(0, (today - last_turn_date).days)
next_turn_date = last_turn_date + timedelta(days=interval)
days_until_turn = (next_turn_date - today).days
turn_label = turning_message(days_until_turn)
rule_stage, rule_journey_pct = journey_from_age(age_days, compost_type)

# ─────────────────────────────────────────────
# MY COMPOST DASHBOARD
# ─────────────────────────────────────────────
st.markdown(f"""
<div class="profile-card">
  <div class="profile-top">
    <div class="profile-title">{WORM_MINI}<span>My Compost</span></div>
    <div class="edit-pill">Düzenle</div>
  </div>
  <div class="tracker-grid">
    <div class="tracker-mini">
      <div class="tracker-label">Kompost Yaşı</div>
      <div class="tracker-value">{age_days} gün</div>
      <div class="tracker-note">{rule_stage} dönemi</div>
    </div>
    <div class="tracker-mini alt">
      <div class="tracker-label">Sonraki Çevirme</div>
      <div class="tracker-value">{turn_label}</div>
      <div class="tracker-note">Son çevirme: {days_since_turn} gün önce</div>
    </div>
  </div>
  <div class="card-sub"><b>{compost_type}</b> • Yaklaşık {material_amount:.1f} kg materyal</div>
  <div class="card-title" style="font-size:15px;margin-top:4px;">Compost Journey</div>
  <div class="journey-row">
    <span class="journey-step {'active' if rule_stage == 'Başlangıç' else ''}">Başlangıç</span>
    <span class="journey-step {'active' if rule_stage == 'Aktif' else ''}">Aktif</span>
    <span class="journey-step {'active' if rule_stage == 'Olgunlaşma' else ''}">Olgunlaşma</span>
    <span class="journey-step {'active' if rule_stage == 'Hazır' else ''}">Hazır</span>
  </div>
  <div class="journey-track"><div class="journey-fill" style="width:{rule_journey_pct}%"></div></div>
</div>
""", unsafe_allow_html=True)

edit_col, analysis_col = st.columns(2)
with edit_col:
    if st.button("Bilgileri Düzenle", use_container_width=True):
        st.session_state.edit_open = not st.session_state.edit_open
with analysis_col:
    if st.button("+ Yeni Analiz", use_container_width=True):
        st.session_state.analysis_open = not st.session_state.analysis_open

# ─────────────────────────────────────────────
# EDIT PANEL
# ─────────────────────────────────────────────
if st.session_state.edit_open:
    st.markdown("""
<div class="form-panel">
  <div class="panel-head">
    <div class="panel-title">Kompost Bilgileri</div>
    <div class="sheet-x">×</div>
  </div>
</div>
""", unsafe_allow_html=True)

    draft_type = st.selectbox(
        "Kompost tipi",
        ["Ev tipi / soğuk kompost", "Bahçe tipi / soğuk kompost", "Sıcak kompost"],
        index=["Ev tipi / soğuk kompost", "Bahçe tipi / soğuk kompost", "Sıcak kompost"].index(st.session_state.compost_type)
    )
    d1, d2 = st.columns(2)
    with d1:
        draft_start = st.date_input("Başlangıç tarihi", value=st.session_state.start_date)
    with d2:
        draft_turn = st.date_input("Son çevirme tarihi", value=st.session_state.last_turn_date)
    draft_amount = st.number_input(
        "Yaklaşık materyal miktarı (kg)",
        min_value=0.0,
        value=float(st.session_state.material_amount),
        step=0.5
    )
    save_col, cancel_col = st.columns(2)
    with save_col:
        if st.button("Kaydet", type="primary", use_container_width=True):
            st.session_state.compost_type = draft_type
            st.session_state.start_date = draft_start
            st.session_state.last_turn_date = draft_turn
            st.session_state.material_amount = draft_amount
            st.session_state.edit_open = False
            st.success("Kompost bilgileri güncellendi.")
            st.rerun()
    with cancel_col:
        if st.button("Kapat", use_container_width=True):
            st.session_state.edit_open = False
            st.rerun()

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
    st.balloons()
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
# ANALYSIS PANEL
# ─────────────────────────────────────────────
if st.session_state.analysis_open:
    st.markdown("""
<div class="form-panel">
  <div class="panel-head">
    <div class="panel-title">Yeni Analiz</div>
    <div class="sheet-x">×</div>
  </div>
  <div class="upload-zone">
    <div class="upload-title">Fotoğraf yükle</div>
    <div class="upload-hint">JPG, PNG • Kompost yığınının güncel fotoğrafı</div>
  </div>
</div>
""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Fotoğraf Yükle",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    if st.button("🔍 Kompostu Analiz Et", type="primary"):
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

                    score = data["health_score"]
                    progress, avg_months = parse_months(data.get("ready_in", "4 ay"))
                    bar_pct = int(progress * 100)
                    probs = data.get("problems", [])
                    recs = data.get("recommendations", [])

                    # HEALTH
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

                    # METRICS
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

                    # MATURITY
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

                    # SUMMARY CARDS
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

                    # DETAIL SELECTORS
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

                    if st.session_state.sheet:
                        if st.button("× Kapat", use_container_width=True):
                            st.session_state.sheet = None
                            st.rerun()

                    # BOTTOM SHEET SIMULATION
                    if st.session_state.sheet == "problems":
                        items = "".join([
                            f'<div class="sheet-item">{circle("#E8A020")}<span>{p}</span></div>'
                            for p in probs
                        ]) or '<div class="sheet-item"><span>Belirgin sorun yok.</span></div>'
                        st.markdown(f"""
<div class="sheet-card">
  <div class="sheet-head">
    <div class="sheet-title">Sorunlar</div>
    <div class="sheet-x">×</div>
  </div>
  {items}
</div>
""", unsafe_allow_html=True)

                    elif st.session_state.sheet == "recommendations":
                        items = "".join([
                            f'<div class="sheet-item">{circle(PALETTE[i % 3])}<span>{r}</span></div>'
                            for i, r in enumerate(recs)
                        ]) or '<div class="sheet-item"><span>Öneri bulunamadı.</span></div>'
                        st.markdown(f"""
<div class="sheet-card">
  <div class="sheet-head">
    <div class="sheet-title">Öneriler</div>
    <div class="sheet-x">×</div>
  </div>
  {items}
</div>
""", unsafe_allow_html=True)

                    elif st.session_state.sheet == "status":
                        st.markdown(f"""
<div class="sheet-card">
  <div class="sheet-head">
    <div class="sheet-title">Kompost Durumu</div>
    <div class="sheet-x">×</div>
  </div>
  <div class="sheet-mini-grid">
    <div class="sheet-mini"><div class="sheet-mini-label">Nem</div><div class="sheet-mini-value">{data["moisture"]}</div></div>
    <div class="sheet-mini"><div class="sheet-mini-label">C/N Dengesi</div><div class="sheet-mini-value">{data["balance"]}</div></div>
    <div class="sheet-mini"><div class="sheet-mini-label">Kompost Yaşı</div><div class="sheet-mini-value">{age_days} gün</div></div>
    <div class="sheet-mini"><div class="sheet-mini-label">Sonraki Çevirme</div><div class="sheet-mini-value">{turn_label}</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

                    elif st.session_state.sheet == "photo":
                        st.markdown("""
<div class="sheet-card">
  <div class="sheet-head">
    <div class="sheet-title">Yüklenen Fotoğraf</div>
    <div class="sheet-x">×</div>
  </div>
</div>
""", unsafe_allow_html=True)
                        st.image(image, use_container_width=True)

                except Exception as e:
                    st.error(f"Analiz sırasında hata oluştu: {e}")
