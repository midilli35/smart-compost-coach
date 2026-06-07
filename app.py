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
  --page-bg:   #FFFFFF;
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

.stFileUploader [data-testid="stFileUploaderDropzone"] {
  background: #FFFDF7 !important;
  border: 1.5px dashed #C8B88A !important;
  border-radius: 18px !important;
  min-height: 76px !important;
  padding: 12px !important;
}

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

.goal-card {
  background: linear-gradient(
      180deg,
      #DBE5DA 0%,
      #F5F8F5 100%
  );
  border: 1.5px solid #B8CCB6;
  border-radius: 24px;
  padding: 20px;
  margin-top: 12px;
  margin-bottom: 16px;
  box-shadow: 0 10px 24px rgba(255,213,128,0.22);
}

/* Haftanın hedefleri kartı */
.st-key-weekly_goals_card {
  background: linear-gradient(180deg, #FFE9BD 0%, #FFF9EA 100%) !important;
  border: 1.5px solid #FFD580 !important;
  border-radius: 24px !important;
  padding: 18px !important;
  margin-top: 14px !important;
  margin-bottom: 16px !important;
  box-shadow: 0 10px 24px rgba(255,213,128,0.22) !important;
}

.st-key-weekly_goals_card .stCheckbox label p {
  font-size: 14px !important;
  font-weight: 600 !important;
  color: var(--dark) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.goal-title-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 10px;
}

.goal-title {
  font-size: 16px;
  font-weight: 800;
  color: var(--dark);
}

.goal-progress {
  font-size: 11px;
  color: var(--royal);
  font-weight: 800;
}

.goal-sub {
  font-size: 12px;
  color: var(--mid);
  margin-bottom: 10px;
  line-height: 1.45;
}

.completed-note {
  background: var(--mist);
  border: 1px solid #DADCFB;
  color: var(--royal);
  border-radius: 18px;
  padding: 12px 14px;
  font-size: 13px;
  font-weight: 800;
  margin-top: 10px;
}

.analysis-ready {
  background: #F0F1FF;
  border: 1px solid #DADCFB;
  color: var(--royal);
  border-radius: 20px;
  padding: 15px 16px;
  margin-bottom: 14px;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 4px 4px 0 rgba(178,180,244,0.35);
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

.sheet-card {
  background: white;
  border-radius: 22px;
  border: 2px solid var(--mist);
  padding: 18px 18px 16px;
  margin: 10px 0 14px;
  box-shadow: 0 12px 30px rgba(70,76,230,0.09);
}

.sheet-title { font-size: 18px; font-weight: 800; color: var(--royal); letter-spacing: -0.03em; margin-bottom: 12px; }
.sheet-item { display:flex; gap:10px; margin-bottom:10px; align-items:flex-start; font-size:13px; color:var(--mid); line-height:1.5; }


.st-key-compost_info_card {
  background: #FFFFFF !important;
  border: 1.5px solid #E8E8FC !important;
  border-radius: 24px !important;
  padding: 16px !important;
  margin-bottom: 14px !important;
  box-shadow: 0 8px 22px rgba(70,76,230,0.05) !important;
}

.st-key-compost_info_card div[data-testid="stButton"] > button {
  background: #F7F7FF !important;
  border: 1.5px solid var(--royal) !important;
  color: var(--royal) !important;
  height: 44px !important;
  min-height: 44px !important;
}

.st-key-compost_info_header div[data-testid="stButton"] > button {
  background: linear-gradient(90deg, #464CE6 0%, #3E43D5 100%) !important;
  color: white !important;
  border-color: #464CE6 !important;
  height: 46px !important;
  min-height: 46px !important;
  font-size: 14px !important;
  font-weight: 800 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# SVG
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


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
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


def make_short_label(text: str, max_words: int = 4) -> str:
    words = re.sub(r"[.!?]", "", str(text)).split()
    return " ".join(words[:max_words])


def safe_json_loads(text: str) -> dict:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


def normalize_list(value, limit: int = 3) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    return [str(item).strip() for item in value if str(item).strip()][:limit]


def normalize_ai_data(data: dict) -> dict:
    issue = data.get("issue") or data.get("main_issue") or "Belirgin sorun yok"
    problems = normalize_list(data.get("detected_problems") or data.get("problems"), 3)
    recs = normalize_list(data.get("recommendations"), 3)

    score = data.get("health_score", 60)
    try:
        score = int(score)
    except Exception:
        score = 60
    score = max(0, min(100, score))

    current_status = str(data.get("current_status") or "Kompost genel olarak izlenebilir durumda; bakım adımlarına göre süreç iyileştirilebilir.").strip()
    coach_note = data.get("coach_note") or data.get("coach_message") or ""
    if not coach_note:
        coach_note = "Kompostunu izlemeye devam et; küçük bakım adımları süreci hızlandırır."

    return {
        "health_score": score,
        "moisture": data.get("moisture", "Belirsiz"),
        "balance": data.get("balance", "Belirsiz"),
        "ready_in": data.get("ready_in", "3-6 ay"),
        "current_status": current_status,
        "issue": str(issue).strip() or "Belirgin sorun yok",
        "detected_problems": problems or [str(issue).strip() or "Belirgin sorun yok"],
        "recommendations": recs or ["Kompostu nazikçe karıştır ve hava almasını sağla."],
        "coach_note": str(coach_note).strip(),
    }


def make_weekly_goals(
    ai_data: dict | None,
    days_until_turn: int,
    compost_type: str,
    odor_status: str = "Yok",
) -> list[str]:
    goals = []

    # 1. Çevirme zamanı
    if days_until_turn <= 3:
        goals.append("Kompostu çevir")

    # 2. Koku gözlemi
    if odor_status == "Belirgin":
        goals.append("Havalandırmayı artır")
    elif odor_status == "Hafif":
        goals.append("Kompostu karıştır")

    # 3. AI nemi
    if ai_data:
        moisture = ai_data.get("moisture", "")
        issue = ai_data.get("issue", "").lower()

        if moisture == "Kuru":
            goals.append("Bir miktar su ekle")
        elif moisture == "Islak":
            goals.append("Kuru yaprak veya karton ekle")
        elif moisture == "Optimal":
            goals.append("Avuç testi yap")

        # 4. AI görsel sorunu
        if any(word in issue for word in ["sıkış", "kompakt", "yoğun", "hava"]):
            goals.append("Kompostu karıştır")
        elif any(word in issue for word in ["büyük", "parça", "iri"]):
            goals.append("Büyük parçaları küçült")
        elif any(word in issue for word in ["kuru", "kuruluk"]):
            goals.append("Bir miktar su ekle")
        elif any(word in issue for word in ["ıslak", "çamur", "sulu"]):
            goals.append("Kuru yaprak veya karton ekle")
    else:
        goals.append("İlk fotoğraf analizini yap")
        goals.append("Koku durumunu kontrol et")

    # Tekrarları kaldır, max 3
    unique = []
    for goal in goals:
        if goal not in unique:
            unique.append(goal)
    return unique[:3]


def goals_signature(goals: list[str]) -> str:
    return "|".join(goals)


def ensure_goal_state(goals: list[str]) -> None:
    sig = goals_signature(goals)
    if st.session_state.get("goal_signature") != sig:
        st.session_state.goal_signature = sig
        st.session_state.goal_done = {goal: False for goal in goals}
        st.session_state.goal_balloons_shown = False
    else:
        for goal in goals:
            st.session_state.goal_done.setdefault(goal, False)


def goal_completion(goals: list[str]) -> tuple[int, int, float]:
    done = sum(1 for goal in goals if st.session_state.goal_done.get(goal, False))
    total = max(1, len(goals))
    return done, len(goals), done / total


def journey_progress(
    age_days: int,
    compost_type: str,
    health_score: int | None,
    goal_completion_ratio: float,
) -> tuple[str, int]:
    total_days = 90 if "Sıcak" in compost_type else 180
    age_pct = max(8, min(95, int((age_days / total_days) * 100)))
    if health_score is None:
        health_score = 70
    goal_score = int(goal_completion_ratio * 100)
    pct = int((age_pct * 0.50) + (health_score * 0.30) + (goal_score * 0.20))
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


def analyze_compost_image(
    image: Image.Image,
    compost_type: str,
    start_date: date,
    age_days: int,
    rule_stage: str,
    last_turn_date: date,
    days_since_turn: int,
    days_until_turn: int,
    material_amount: float,
    odor_status: str = "Yok",
) -> dict:
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
  "current_status": "",
  "issue": "",
  "detected_problems": [],
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
- User odor observation: {odor_status}

Rules:
- health_score: integer 0-100
- moisture: one of "Kuru", "Optimal", "Islak"
- balance: one of "Karbon Fazla", "Dengeli", "Azot Fazla"
- ready_in: short Turkish estimate, e.g. "2-3 ay"
- current_status: 1 short Turkish sentence, max 22 words. Explain what the compost currently looks like.
- issue: one main Turkish problem phrase, max 7 words
- detected_problems: 2-3 Turkish bullet-style sentences, each max 14 words. Mention visible clues when possible: dry leaves/cardboard, green material, brown material, wetness, clumping, large pieces, air/turning.
- recommendations: 2-3 practical Turkish actions, each max 13 words. Be specific, e.g. "Kuru yaprak veya karton ekle", "Yeşil atık oranını artır", "Büyük parçaları küçült".
- coach_note: one friendly Turkish sentence, max 20 words
- Do not be too long, but be more informative than one-word labels.
- If the image is unclear, say what can still be checked manually.
"""
    response = model.generate_content([prompt, image])
    return normalize_ai_data(safe_json_loads(response.text))


# ─────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ─────────────────────────────────────────────
today = date.today()
defaults = {
    "sheet": None,
    "compost_type": "Ev tipi / soğuk kompost",
    "start_date": today - timedelta(days=22),
    "last_turn_date": today - timedelta(days=3),
    "material_amount": 2.0,
    "odor_status": "Yok",
    "ai_data": None,
    "ai_image": None,
    "goal_done": {},
    "goal_signature": "",
    "goal_balloons_shown": False,
    "analysis_ready": False,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ─────────────────────────────────────────────
# COMPUTED VALUES
# ─────────────────────────────────────────────
compost_type = st.session_state.compost_type
start_date = st.session_state.start_date
last_turn_date = st.session_state.last_turn_date
material_amount = st.session_state.material_amount
odor_status = st.session_state.odor_status

age_days = max(0, (date.today() - start_date).days)
interval = turning_interval_days(compost_type)
days_since_turn = max(0, (date.today() - last_turn_date).days)
last_turn_text = last_turn_message(days_since_turn)
next_turn_date = last_turn_date + timedelta(days=interval)
days_until_turn = (next_turn_date - date.today()).days
turn_label = turning_message(days_until_turn)

goals = make_weekly_goals(st.session_state.ai_data, days_until_turn, compost_type, odor_status)
ensure_goal_state(goals)
goal_done_count, goal_total_count, goal_ratio = goal_completion(goals)

health_for_journey = None
if st.session_state.ai_data is not None:
    health_for_journey = st.session_state.ai_data.get("health_score")

rule_stage, rule_journey_pct = journey_progress(age_days, compost_type, health_for_journey, goal_ratio)


# ─────────────────────────────────────────────
# DIALOGS
# ─────────────────────────────────────────────
@st.dialog("📷 Kompostunu Analiz Et")
def analysis_dialog():
    st.caption("Fotoğraf yükle, Smart Compost Coach kısa bir bakım önerisi versin.")

    uploaded_file = st.file_uploader("Fotoğraf yükle", type=["jpg", "jpeg", "png"], key="analysis_uploader")

    if uploaded_file is not None:
        image_preview = Image.open(uploaded_file)
        st.image(image_preview, caption="Yüklenen fotoğraf", use_container_width=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_clicked = st.button("🔍 Analiz Et", type="primary", use_container_width=True)
    with col2:
        close_clicked = st.button("Kapat", use_container_width=True)

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
                    odor_status=odor_status,
                )

                st.session_state.ai_data = data
                st.session_state.ai_image = image.copy()
                st.session_state.analysis_ready = True

                new_goals = make_weekly_goals(data, days_until_turn, compost_type, odor_status)
                st.session_state.goal_signature = ""
                ensure_goal_state(new_goals)

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

        new_odor = st.radio(
            "Koku durumu",
            ["Yok", "Hafif", "Belirgin"],
            index=["Yok", "Hafif", "Belirgin"].index(st.session_state.odor_status),
            horizontal=True,
        )

        ef1, ef2 = st.columns([3, 1])
        with ef1:
            saved = st.form_submit_button("✓ Kaydet", type="primary", use_container_width=True)
        with ef2:
            cancel = st.form_submit_button("İptal", use_container_width=True)

        if saved:
            st.session_state.compost_type = new_type
            st.session_state.start_date = new_start
            st.session_state.last_turn_date = new_turn
            st.session_state.material_amount = new_amount
            st.session_state.odor_status = new_odor
            st.session_state.goal_signature = ""
            st.rerun()

        if cancel:
            st.rerun()


@st.dialog("📊 Analiz Sonuçları")
def results_dialog():
    data = st.session_state.ai_data
    image = st.session_state.ai_image

    if data is None:
        st.info("Henüz analiz sonucu yok.")
        if st.button("Kapat"):
            st.rerun()
        return

    score = data["health_score"]
    progress, _ = parse_months(data.get("ready_in", "4 ay"))
    bar_pct = int(progress * 100)
    issue = data.get("issue", "Belirgin sorun yok")
    current_status = data.get("current_status", "Kompost genel olarak izlenebilir durumda.")
    problems = data.get("detected_problems", [issue])[:3]
    recs = data.get("recommendations", [])[:3]

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

    tab1, tab2, tab3, tab4 = st.tabs(["Durum", "Problem", "Öneri", "Fotoğraf"])
    with tab1:
        st.markdown(
            f"""
<div class="sheet-card">
  <div class="sheet-title">Mevcut Durum</div>
  <div class="sheet-item">{tri("#464CE6")}<span>{current_status}</span></div>
  <div class="sheet-item">{tri("#E8A020")}<span><b>Ana nokta:</b> {issue}</span></div>
</div>
""",
            unsafe_allow_html=True,
        )

    with tab2:
        problem_detail = "".join(
            [f'<div class="sheet-item">{tri("#E8A020")}<span>{p}</span></div>' for p in problems]
        )
        st.markdown(
            f"""
<div class="sheet-card">
  <div class="sheet-title">Tespit Edilen Problemler</div>
  {problem_detail}
</div>
""",
            unsafe_allow_html=True,
        )

    with tab3:
        rec_detail = "".join(
            [f'<div class="sheet-item">{tri("#7C80ED")}<span>{r}</span></div>' for r in recs]
        )
        st.markdown(
            f"""
<div class="sheet-card">
  <div class="sheet-title">Bugünkü Tavsiyeler</div>
  {rec_detail}
</div>
""",
            unsafe_allow_html=True,
        )

    with tab4:
        if image is not None:
            st.image(image, use_container_width=True)

    if st.button("Kapat", use_container_width=True):
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
# MY COMPOST CARD
# ─────────────────────────────────────────────
st.markdown(
    f"""
<div class="card">
  <div class="card-head">
    <div>
      <div class="card-title">My Compost</div>
      <div class="card-sub">Kompostunun gelişimini takip et ve bakım önerilerini kişiselleştir.</div>
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
""",
    unsafe_allow_html=True,
)


# ─── Kompost Bilgileri Kartı ───
with st.container(key="compost_info_card"):
    with st.container(key="compost_info_header"):
        if st.button("Kompost Bilgileri", use_container_width=True, key="compost_info_header_btn"):
            edit_compost_dialog()

    # Info pills (2×2 grid)
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        if st.button(compost_type, use_container_width=True, key="edit_type_pill"):
            edit_compost_dialog()
    with row1_col2:
        if st.button(f"Yaklaşık {material_amount:.1f} kg", use_container_width=True, key="edit_amount_pill"):
            edit_compost_dialog()

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        if st.button(
            f"Başlangıç: {start_date.strftime('%d.%m.%Y')}",
            use_container_width=True,
            key="edit_start_pill",
        ):
            edit_compost_dialog()
    with row2_col2:
        if st.button(f"Koku: {odor_status}", use_container_width=True, key="edit_odor_pill"):
            edit_compost_dialog()

# ─── Analyze button ───
if st.button("📷 Kompostunu Analiz Et", type="primary", use_container_width=True, key="open_analysis_main"):
    analysis_dialog()

# ─── Analysis ready banner ───
if st.session_state.analysis_ready and st.session_state.ai_data is not None:
    st.markdown(
        """
<div class="analysis-ready">
  Analiz tamamlandı. Sonuçları ayrı panelde inceleyebilirsin.
</div>
""",
        unsafe_allow_html=True,
    )
    if st.button("📊 Analiz Sonuçlarını İncele", use_container_width=True, key="open_results"):
        results_dialog()


# ─────────────────────────────────────────────
# WEEKLY GOALS
# ─────────────────────────────────────────────
goal_done_count, goal_total_count, goal_ratio = goal_completion(goals)

with st.container(key="weekly_goals_card"):

    # Başlık satırı
    st.markdown(
        f"""
<div class="goal-title-row" style="margin-bottom:6px;">
  <div class="goal-title">Bu Haftanın Hedefleri</div>
  <div class="goal-progress">{goal_done_count}/{goal_total_count} tamamlandı</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Checkboxlar
    for idx, goal in enumerate(goals):
        key = f"goal_{idx}_{abs(hash(goal))}"
        current = bool(st.session_state.goal_done.get(goal, False))
        checked = st.checkbox(goal, value=current, key=key)

        if checked != current:
            st.session_state.goal_done[goal] = checked
            if checked and goal == "Kompostu çevir":
                st.session_state.last_turn_date = date.today()
            st.rerun()

    # Tamamlanma kontrolü
    goal_done_count, goal_total_count, goal_ratio = goal_completion(goals)
    if goal_total_count > 0 and goal_done_count == goal_total_count:
        st.success("Harika! Bu haftaki bakım hedeflerinin tamamı tamamlandı 🌱")
        if not st.session_state.goal_balloons_shown:
            st.balloons()
            st.session_state.goal_balloons_shown = True
