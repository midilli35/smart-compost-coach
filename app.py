import json
import re
from datetime import date, timedelta

import streamlit as st
from PIL import Image
import google.generativeai as genai


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Compost Coach",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    pass


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown(
    """
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
  --orange:    #E8650A;
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

/* Dialog styling */
div[data-testid="stDialog"] div[role="dialog"] {
  border-radius: 28px !important;
  border: 2px solid var(--mist) !important;
  box-shadow: 0 32px 80px rgba(18,18,60,0.28) !important;
}

div[data-testid="stDialog"] {
  backdrop-filter: blur(7px) !important;
  -webkit-backdrop-filter: blur(7px) !important;
}

div[data-testid="stDialog"] h2 {
  color: var(--royal) !important;
  font-weight: 800 !important;
  letter-spacing: -0.03em !important;
}

/* Buttons */
div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button {
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

div[data-testid="stButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 8px 18px rgba(70,76,230,0.12) !important;
}

div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
  background: var(--orange) !important;
  color: white !important;
  border-color: var(--orange) !important;
}

/* Equal pill buttons */
div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] > button {
  height: 44px !important;
  min-height: 44px !important;
  max-height: 44px !important;
  font-size: 11.5px !important;
  padding: 0 6px !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

/* Upload */
.stFileUploader [data-testid="stFileUploaderDropzone"] {
  background: #FFFDF7 !important;
  border: 1.5px dashed #C8B88A !important;
  border-radius: 18px !important;
  min-height: 76px !important;
  padding: 12px !important;
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
  width: 42px; height: 42px;
  border-radius: 50%;
  background: var(--cream);
  display: flex; align-items: center; justify-content: center;
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

/* Journey */
.journey-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--light);
  margin: 12px 0 10px;
}

.journey-step.active { color: var(--royal); font-weight: 800; }

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

.check-title { font-size: 17px; font-weight: 800; color: var(--dark); margin-bottom: 4px; letter-spacing: -0.02em; }
.check-sub { font-size: 12px; color: var(--mid); margin-bottom: 12px; }

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

/* AI result cards */
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
  width:56px; height:56px;
  border-radius:50%;
  background:#FFE9BD;
  display:flex; align-items:center; justify-content:center;
  flex-shrink:0;
}

.health-text-block h4 {
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em;
  color: #7A5E20; font-weight: 800; margin: 0;
}

.health-score-num {
  font-size: 52px; font-weight: 800; color: var(--dark);
  line-height: 1; margin: 2px 0; letter-spacing: -0.06em;
}

.health-score-num span { font-size: 20px; color: #7A5E20; letter-spacing: -0.02em; }
.health-status-label { font-size: 12px; color: #7A5E20; font-weight: 700; }

.metrics-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 12px; margin-bottom: 14px;
}

.metric-card {
  background: white; border-radius: 18px; padding: 14px;
  border: 1px solid var(--line);
  box-shadow: 0 8px 22px rgba(70,76,230,0.04);
}

.metric-label {
  font-size: 10px; color: var(--light); text-transform: uppercase;
  letter-spacing: 0.06em; font-weight: 800; margin-bottom: 4px;
}

.metric-value { font-size: 20px; font-weight: 800; color: var(--dark); letter-spacing: -0.04em; }

.maturity-card {
  background: white; border-radius: 20px; padding: 16px 18px;
  margin-bottom: 14px; border: 1px solid var(--line);
  box-shadow: 0 8px 22px rgba(70,76,230,0.04);
}

.maturity-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 10px; }
.maturity-label { font-size: 10px; color: var(--light); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 800; }
.maturity-value { font-size: 14px; color: var(--royal); font-weight: 800; }
.maturity-track { height: 8px; background: var(--mist); border-radius: 99px; overflow: hidden; margin-bottom: 10px; }

.maturity-fill {
  height: 100%; background: linear-gradient(90deg, var(--peri), var(--royal));
  border-radius: 99px; transition: width 1.2s cubic-bezier(0.4,0,0.2,1);
}

.panels-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }

.panel-card {
  background: white; border-radius: 18px; border: 1px solid var(--line);
  overflow: hidden; box-shadow: 0 10px 26px rgba(70,76,230,0.045);
}

.panel-header { padding: 12px 14px 10px; display: flex; align-items: center; gap: 8px; }
.panel-header.problems { border-bottom: 2px solid var(--cream); }
.panel-header.recs { border-bottom: 2px solid var(--mist); }
.panel-title { font-size: 13px; font-weight: 800; color: var(--dark); }

.panel-preview {
  padding: 10px 14px 14px;
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
  flex-shrink:0;
  margin-top:5px;
  width:0; height:0;
  border-top:5px solid transparent;
  border-bottom:5px solid transparent;
  border-left:8px solid;
}

.sheet-card {
  background: white;
  border-radius: 26px 26px 18px 18px;
  border: 2px solid var(--mist);
  padding: 18px 18px 16px;
  margin: 14px 0;
  box-shadow: 0 -6px 0 rgba(178,180,244,0.35), 0 18px 38px rgba(70,76,230,0.10);
}

.sheet-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.sheet-title { font-size: 18px; font-weight: 800; color: var(--royal); letter-spacing: -0.03em; }
.sheet-item { display:flex; gap:10px; margin-bottom:10px; align-items:flex-start; font-size:13px; color:var(--mid); line-height:1.5; }

/* V18 additions */
.history-card {
  background: #FFFDF7;
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 14px;
  margin-top: 14px;
}

.history-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}

.history-title {
  font-size: 13px;
  font-weight: 800;
  color: var(--dark);
}

.history-note {
  font-size: 10px;
  color: var(--light);
  font-weight: 700;
}

.sparkline {
  display: flex;
  align-items: end;
  gap: 5px;
  height: 38px;
  margin-top: 8px;
}

.sparkbar {
  flex: 1;
  min-width: 10px;
  border-radius: 999px 999px 4px 4px;
  background: linear-gradient(180deg, var(--peri), var(--royal));
  opacity: .9;
}

.coach-card {
  background: white;
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 18px;
  margin-bottom: 14px;
  box-shadow: 0 8px 26px rgba(70,76,230,0.045);
}

.coach-label {
  font-size: 10px;
  color: var(--light);
  text-transform: uppercase;
  letter-spacing: .07em;
  font-weight: 800;
  margin-bottom: 7px;
}

.coach-text {
  font-size: 14px;
  color: var(--dark);
  line-height: 1.45;
  font-weight: 700;
}

.goal-card {
  background: #FFFDF7;
  border: 1px solid #F2E2B8;
  border-radius: 22px;
  padding: 18px;
  margin-bottom: 14px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.035);
}

.goal-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--dark);
  margin-bottom: 10px;
}

.goal-item {
  font-size: 13px;
  color: var(--mid);
  line-height: 1.55;
  margin-bottom: 6px;
  font-weight: 650;
}

.impact-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}

.impact-card {
  background: white;
  border-radius: 18px;
  padding: 14px;
  border: 1px solid var(--line);
  box-shadow: 0 8px 22px rgba(70,76,230,0.04);
}

.impact-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #F0F1FF;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.impact-label {
  font-size: 10px;
  color: var(--light);
  text-transform: uppercase;
  letter-spacing: .06em;
  font-weight: 800;
}

.impact-value {
  font-size: 20px;
  font-weight: 800;
  color: var(--dark);
  letter-spacing: -.04em;
  margin-top: 3px;
}

</style>
""",
    unsafe_allow_html=True,
)


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
def score_label(score: int) -> str:
    if score >= 80:
        return "İyi durumda"
    if score >= 60:
        return "Geliştirilebilir"
    if score >= 40:
        return "Dikkat gerekli"
    return "Hemen müdahale"


def parse_months(ready_in_str: str) -> tuple[float, float]:
    text = str(ready_in_str).lower().replace("-", " ")
    nums = [int(s) for s in text.split() if s.isdigit()]
    if nums:
        low = nums[0]
        high = nums[-1] if len(nums) > 1 else low
        avg = (low + high) / 2
        return max(0.05, min(0.95, 1 - (avg / 12))), avg
    return 0.3, 4


def tri(color: str) -> str:
    return f'<span class="bullet-tri" style="border-left-color:{color}"></span>'


def turning_interval_days(compost_type: str) -> int:
    if "Sıcak" in compost_type:
        return 3
    if "Bahçe" in compost_type:
        return 7
    return 10


def turning_message(days_until: int) -> str:
    if days_until < 0:
        return f"{abs(days_until)} gün gecikti"
    if days_until == 0:
        return "Bugün"
    if days_until == 1:
        return "Yarın"
    return f"{days_until} gün sonra"


def last_turn_message(days_since_turn: int) -> str:
    if days_since_turn == 0:
        return "Bugün"
    if days_since_turn == 1:
        return "Dün"
    return f"{days_since_turn} gün önce"


def journey_from_age(
    age_days: int,
    compost_type: str,
    health_score: int | None = None,
    days_since_turn: int | None = None,
) -> tuple[str, int]:
    """Compost Journey = age progress + AI health + care rhythm.

    This avoids showing a poorly maintained compost as mature only because time passed.
    """
    total_days = 90 if "Sıcak" in compost_type else 180
    age_pct = max(8, min(95, int((age_days / total_days) * 100)))

    if days_since_turn is None:
        care_score = 70
    else:
        interval = turning_interval_days(compost_type)
        if days_since_turn <= interval:
            care_score = 90
        elif days_since_turn <= interval + 4:
            care_score = 65
        else:
            care_score = 40

    if health_score is None:
        health_score = 70

    # 60% age + 25% AI health + 15% care rhythm
    pct = int((age_pct * 0.60) + (health_score * 0.25) + (care_score * 0.15))
    pct = max(8, min(95, pct))

    if pct < 25:
        stage = "Başlangıç"
    elif pct < 65:
        stage = "Aktif"
    elif pct < 90:
        stage = "Olgunlaşma"
    else:
        stage = "Hazır"
    return stage, pct


def make_short_label(text: str, max_words: int = 4) -> str:
    words = re.sub(r"[.!?]", "", str(text)).split()
    return " ".join(words[:max_words])


def safe_json_loads(text: str) -> dict:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def normalize_ai_data(data: dict) -> dict:
    issue = data.get("issue") or data.get("main_issue") or ""
    recs = data.get("recommendations", [])
    if isinstance(recs, str):
        recs = [recs]
    recs = [make_short_label(r, 5) for r in recs if str(r).strip()][:2]

    score = data.get("health_score", 60)
    try:
        score = int(score)
    except Exception:
        score = 60
    score = max(0, min(100, score))

    coach_note = data.get("coach_note") or data.get("coach_message") or ""
    if not coach_note:
        coach_note = "Kompostunu izlemeye devam et; küçük bakım adımları süreci hızlandırır."

    return {
        "health_score": score,
        "moisture": data.get("moisture", "Belirsiz"),
        "balance": data.get("balance", "Belirsiz"),
        "ready_in": data.get("ready_in", "3-6 ay"),
        "issue": make_short_label(issue, 5) or "Belirgin sorun yok",
        "recommendations": recs or ["Havalandırmayı sürdür"],
        "coach_note": str(coach_note).strip(),
    }


def make_weekly_goals(ai_data: dict | None, days_since_turn: int, compost_type: str) -> list[str]:
    """Rule-based weekly goals using Gemini's diagnosis, not Gemini-generated goals."""
    goals = []
    interval = turning_interval_days(compost_type)

    if days_since_turn >= interval:
        goals.append("Kompostu bir kez çevir")

    if ai_data:
        moisture = ai_data.get("moisture", "")
        balance = ai_data.get("balance", "")
        score = int(ai_data.get("health_score", 70))

        if moisture == "Kuru":
            goals.append("Nem seviyesini artır")
        elif moisture == "Islak":
            goals.append("Kuru kahverengi materyal ekle")
        else:
            goals.append("Nem seviyesini koru")

        if balance == "Karbon Fazla":
            goals.append("Yeşil materyal ekle")
        elif balance == "Azot Fazla":
            goals.append("Kahverengi materyal ekle")
        else:
            goals.append("Dengeyi koru")

        if score < 60:
            goals.append("Koku ve sıkışmayı kontrol et")
    else:
        goals.append("İlk fotoğraf analizini yap")
        goals.append("Bakım ritmini kaydet")

    # Deduplicate and keep compact.
    unique = []
    for goal in goals:
        if goal not in unique:
            unique.append(goal)
    return unique[:3]


def compost_impact(material_amount: float, age_days: int) -> dict:
    """Approximate, presentation-friendly impact values."""
    weeks = max(1, age_days / 7)
    processed_kg = round(material_amount * weeks, 1)
    compost_kg = round(processed_kg * 0.35, 1)
    co2_kg = round(processed_kg * 0.45, 1)
    return {
        "processed_kg": processed_kg,
        "compost_kg": compost_kg,
        "co2_kg": co2_kg,
    }


def sparkline_html(history: list[dict]) -> str:
    if not history:
        return '<div class="history-note">Henüz analiz yok</div>'

    recent = history[-6:]
    bars = []
    for item in recent:
        score = int(item.get("score", 0))
        height = max(10, min(38, int(score * 0.38)))
        bars.append(f'<div class="sparkbar" title="{score}/100" style="height:{height}px"></div>')
    return '<div class="sparkline">' + "".join(bars) + "</div>"


def analyze_compost_image(image: Image.Image, compost_type: str, start_date: date, age_days: int,
                          rule_stage: str, last_turn_date: date, days_since_turn: int,
                          days_until_turn: int, material_amount: float) -> dict:
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
You are Smart Compost Coach, a simple daily compost assistant.

Analyze the compost image and user tracking data.
Return ONLY valid JSON. No markdown. No explanation.

Required JSON:
{{
  "health_score": 0,
  "moisture": "",
  "balance": "",
  "ready_in": "",
  "issue": "",
  "recommendations": [],
  "coach_note": ""
}}

User data:
- Compost type: {compost_type}
- Start date: {start_date}
- Compost age: {age_days} days
- Journey stage: {rule_stage}
- Last turning date: {last_turn_date}
- Days since last turning: {days_since_turn}
- Next turning due in: {days_until_turn} days
- Approximate material amount: {material_amount} kg

Rules:
- health_score: integer 0-100
- moisture: one of "Kuru", "Optimal", "Islak"
- balance: one of "Karbon Fazla", "Dengeli", "Azot Fazla"
- ready_in: short Turkish estimate, e.g. "2-3 ay"
- issue: one short Turkish phrase, max 5 words
- recommendations: max 2 Turkish phrases, each max 5 words
- coach_note: one friendly Turkish sentence, max 18 words
- Keep it simple like a compost coach.
"""
    response = model.generate_content([prompt, image])
    return normalize_ai_data(safe_json_loads(response.text))


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
today = date.today()

defaults = {
    "sheet": None,
    "care_done": False,
    "show_balloons": False,
    "compost_type": "Ev tipi / soğuk kompost",
    "start_date": today - timedelta(days=22),
    "last_turn_date": today - timedelta(days=3),
    "material_amount": 2.0,
    "ai_data": None,
    "ai_image": None,
    "history": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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

health_for_journey = None
if st.session_state.ai_data is not None:
    health_for_journey = st.session_state.ai_data.get("health_score")

rule_stage, rule_journey_pct = journey_from_age(age_days, compost_type, health_for_journey, days_since_turn)


# ─────────────────────────────────────────────
# DIALOGS
# ─────────────────────────────────────────────
@st.dialog("📷 Kompostunu Analiz Et")
def analysis_dialog():
    st.caption("Fotoğraf yükle, Smart Compost Coach kısa bir bakım önerisi versin.")

    uploaded_file = st.file_uploader(
        "Fotoğraf yükle",
        type=["jpg", "jpeg", "png"],
        label_visibility="visible",
        key="analysis_uploader",
    )

    if uploaded_file is not None:
        image_preview = Image.open(uploaded_file)
        st.image(image_preview, caption="Yüklenen fotoğraf", use_container_width=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        analyze_clicked = st.button("🔍 Analiz Et", type="primary", use_container_width=True)

    with col2:
        close_clicked = st.button("✕ Kapat", use_container_width=True)

    if close_clicked:
        st.rerun()

    if analyze_clicked:
        if uploaded_file is None:
            st.warning("Lütfen önce bir kompost fotoğrafı yükleyin.")
            return

        image = Image.open(uploaded_file)

        with st.spinner("Kompostun analiz ediliyor..."):
            try:
                data = analyze_compost_image(
                    image=image,
                    compost_type=compost_type,
                    start_date=start_date,
                    age_days=age_days,
                    rule_stage=rule_stage,
                    last_turn_date=last_turn_date,
                    days_since_turn=days_since_turn,
                    days_until_turn=days_until_turn,
                    material_amount=material_amount,
                )
                st.session_state.ai_data = data
                st.session_state.ai_image = image.copy()

                st.session_state.history.append({
                    "date": date.today().strftime("%d.%m"),
                    "score": data["health_score"],
                    "moisture": data["moisture"],
                    "balance": data["balance"],
                })
                st.session_state.history = st.session_state.history[-8:]

                st.session_state.sheet = None
                st.rerun()
            except Exception as e:
                st.error(f"Analiz sırasında hata oluştu: {e}")


@st.dialog("🌱 Kompost Bilgileri")
def edit_compost_dialog():
    with st.form("compost_info_form"):
        new_type = st.selectbox(
            "Kompost tipi",
            ["Ev tipi / soğuk kompost", "Bahçe tipi / soğuk kompost", "Sıcak kompost"],
            index=["Ev tipi / soğuk kompost", "Bahçe tipi / soğuk kompost", "Sıcak kompost"].index(
                st.session_state.compost_type
            ),
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
            step=0.5,
        )

        ef1, ef2 = st.columns([3, 1])
        with ef1:
            saved = st.form_submit_button("✓ Kaydet", type="primary", use_container_width=True)
        with ef2:
            cancel = st.form_submit_button("✕ İptal", use_container_width=True)

        if saved:
            st.session_state.compost_type = new_type
            st.session_state.start_date = new_start
            st.session_state.last_turn_date = new_turn
            st.session_state.material_amount = new_amount
            st.rerun()

        if cancel:
            st.rerun()


# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown(
    f"""
<div class="hero-card">
  {HERO_PATTERN}
  <div style="position:relative;z-index:1">
    {HERO_SVG}
    <div class="hero-title">Smart Compost<br>Coach</div>
    <div class="hero-sub">Kompostunu takip et, fotoğrafla analiz et.</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# MY COMPOST DASHBOARD
# ─────────────────────────────────────────────
st.markdown(
    f"""
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

  <div class="history-card">
    <div class="history-head">
      <div class="history-title">Health History</div>
      <div class="history-note">Son analizler</div>
    </div>
    {sparkline_html(st.session_state.history)}
  </div>
</div>
""",
    unsafe_allow_html=True,
)

p1, p2, p3 = st.columns([1, 1, 1])
with p1:
    if st.button(compost_type, use_container_width=True, key="edit_type_pill"):
        edit_compost_dialog()
with p2:
    if st.button(f"Yaklaşık {material_amount:.1f} kg", use_container_width=True, key="edit_amount_pill"):
        edit_compost_dialog()
with p3:
    if st.button(f"Başlangıç: {start_date.strftime('%d.%m.%Y')}", use_container_width=True, key="edit_start_pill"):
        edit_compost_dialog()

if st.button("📷 Kompostunu Analiz Et", type="primary", use_container_width=True, key="open_analysis_main"):
    analysis_dialog()


impact = compost_impact(material_amount, age_days)
st.markdown(
    f"""
<div class="impact-grid">
  <div class="impact-card">
    <div class="impact-icon">♻️</div>
    <div class="impact-label">Dönüştürülen Atık</div>
    <div class="impact-value">{impact["processed_kg"]} kg</div>
  </div>
  <div class="impact-card">
    <div class="impact-icon">🌍</div>
    <div class="impact-label">Önlenen CO₂</div>
    <div class="impact-value">{impact["co2_kg"]} kg</div>
  </div>
  <div class="impact-card">
    <div class="impact-icon">🌱</div>
    <div class="impact-label">Tahmini Kompost</div>
    <div class="impact-value">{impact["compost_kg"]} kg</div>
  </div>
  <div class="impact-card">
    <div class="impact-icon">📈</div>
    <div class="impact-label">Analiz Sayısı</div>
    <div class="impact-value">{len(st.session_state.history)}</div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# DAILY CHECK-IN
# ─────────────────────────────────────────────
st.markdown(
    """
<div class="check-card">
  <div class="check-title">Günlük Kontrol</div>
  <div class="check-sub">Bugün kompostu havalandırdın mı?</div>
</div>
""",
    unsafe_allow_html=True,
)

b1, b2 = st.columns(2)
with b1:
    later_clicked = st.button("Daha Sonra", use_container_width=True)
with b2:
    done_clicked = st.button("✓ Çevirdim", use_container_width=True)

if done_clicked:
    st.session_state.care_done = True
    st.session_state.last_turn_date = date.today()
    st.session_state.show_balloons = True
    st.rerun()

if later_clicked:
    st.session_state.care_done = False

if st.session_state.get("show_balloons"):
    st.balloons()
    st.session_state.show_balloons = False

if st.session_state.care_done:
    st.markdown(
        """
<div class="success-note">
  Güzel iş! Bugünkü bakım tamamlandı. Kompostun bugün biraz daha nefes aldı.
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
<div class="info-note">
  Havalandırma, ayrışmayı hızlandırır ve kötü koku riskini azaltır.
</div>
""",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# WEEKLY GOAL — rule-based from AI output
# ─────────────────────────────────────────────
goals = make_weekly_goals(st.session_state.ai_data, days_since_turn, compost_type)
goal_items = "".join([f'<div class="goal-item">☐ {goal}</div>' for goal in goals])
st.markdown(
    f"""
<div class="goal-card">
  <div class="goal-title">Bu Haftanın Hedefi</div>
  {goal_items}
</div>
""",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# AI RESULTS
# ─────────────────────────────────────────────
if st.session_state.ai_data is not None:
    data = st.session_state.ai_data
    image = st.session_state.ai_image
    score = data["health_score"]
    progress, _ = parse_months(data.get("ready_in", "4 ay"))
    bar_pct = int(progress * 100)
    issue = data.get("issue", "Belirgin sorun yok")
    recs = data.get("recommendations", [])[:2]

    st.markdown(
        f"""
<div class="health-card">
  <div class="health-icon-small">{SPROUT_SVG}</div>
  <div class="health-text-block">
    <h4>Health Score</h4>
    <div class="health-score-num">{score}<span>/100</span></div>
    <div class="health-status-label">{score_label(score)}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="coach-card">
  <div class="coach-label">AI Coach Message</div>
  <div class="coach-text">{data.get("coach_note", "Kompostunu izlemeye devam et.")}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
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
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="maturity-card">
  <div class="maturity-header">
    <span class="maturity-label">Tahmini Olgunlaşma</span>
    <span class="maturity-value">{data["ready_in"]}</span>
  </div>
  <div class="maturity-track">
    <div class="maturity-fill" style="width:{bar_pct}%"></div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    rec_items = "".join(
        [f'<div class="panel-item">{tri("#7C80ED")}<span>{make_short_label(r, 5)}</span></div>' for r in recs]
    )

    st.markdown(
        f"""
<div class="panels-row">
  <div class="panel-card">
    <div class="panel-header problems">
      {WARNING_SVG}
      <span class="panel-title">Dikkat</span>
    </div>
    <div class="panel-preview">
      <div class="panel-item">{tri("#E8A020")}<span>{issue}</span></div>
    </div>
  </div>

  <div class="panel-card">
    <div class="panel-header recs">
      {CHECK_SVG}
      <span class="panel-title">Bugünkü Tavsiye</span>
    </div>
    <div class="panel-preview">{rec_items}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    s1, s2, s3 = st.columns(3)
    with s1:
        if st.button("Detay", use_container_width=True):
            st.session_state.sheet = "status"
    with s2:
        if st.button("Fotoğraf", use_container_width=True):
            st.session_state.sheet = "photo"
    with s3:
        if st.button("Kapat", use_container_width=True):
            st.session_state.sheet = None
            st.rerun()

    if st.session_state.sheet == "status":
        rec_detail = "".join([f"<div class='sheet-item'>• {r}</div>" for r in recs])
        st.markdown(
            f"""
<div class="sheet-card">
  <div class="sheet-head"><div class="sheet-title">Kompost Durumu</div></div>
  <div class="sheet-item">Nem: <b>{data["moisture"]}</b></div>
  <div class="sheet-item">Denge: <b>{data["balance"]}</b></div>
  <div class="sheet-item">Dikkat: <b>{issue}</b></div>
  <div class="sheet-item">Öneriler:</div>
  {rec_detail}
</div>
""",
            unsafe_allow_html=True,
        )

    elif st.session_state.sheet == "photo":
        st.markdown(
            """
<div class="sheet-card">
  <div class="sheet-head"><div class="sheet-title">Yüklenen Fotoğraf</div></div>
</div>
""",
            unsafe_allow_html=True,
        )
        if image is not None:
            st.image(image, use_container_width=True)


# ─────────────────────────────────────────────
# VERSION NOTE
# ─────────────────────────────────────────────
st.caption("Smart Compost Coach prototype · v18 with history, impact, weekly goals")
