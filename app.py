import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone
import time
import hashlib

st.set_page_config(page_title="Grade 7 Separation Lab FA", page_icon="🧪", layout="wide")

# ---------- CONFIG ----------
TIME_LIMIT = 30 * 60  # 30 minutes
MAX_SCORE = 10.0

QUESTIONS = [
    {
        "id": 1, "type": "mcq", "points": 1.0,
        "title": "Lab Station 1 — Muddy Water",
        "scenario": "A beaker contains water, sand, and small insoluble soil particles. Your goal is to obtain clearer water.",
        "question": "Which sequence is the BEST choice?",
        "options": [
            "Evaporation → crystallization",
            "Sedimentation → decantation → filtration",
            "Distillation → magnetism",
            "Chromatography → sieving"
        ],
        "answer": "Sedimentation → decantation → filtration",
        "feedback": "For an insoluble solid in a liquid, allow settling, decant carefully, then filter."
    },
    {
        "id": 2, "type": "mcq", "points": 1.0,
        "title": "Lab Station 2 — Iron + Sand",
        "scenario": "A tray contains iron filings mixed with sand.",
        "question": "Which tool should you drag/use first?",
        "options": ["Magnet", "Filter paper", "Evaporating dish", "Condenser"],
        "answer": "Magnet",
        "feedback": "Iron is magnetic; sand is not."
    },
    {
        "id": 3, "type": "mcq", "points": 1.0,
        "title": "Lab Station 3 — Salt Water",
        "scenario": "Salt is completely dissolved in water. You need to recover the SOLID salt.",
        "question": "Which technique is most suitable?",
        "options": ["Filtration", "Magnetic separation", "Evaporation / crystallization", "Sieving"],
        "answer": "Evaporation / crystallization",
        "feedback": "Dissolved salt passes through a filter; removing water allows salt crystals to remain."
    },
    {
        "id": 4, "type": "mcq", "points": 1.0,
        "title": "Lab Station 4 — Pure Water from Salt Water",
        "scenario": "This time you must collect the WATER from a salt solution, not the salt.",
        "question": "Which setup should you choose?",
        "options": ["Simple distillation", "Filtration", "Magnetism", "Decantation only"],
        "answer": "Simple distillation",
        "feedback": "Water vaporizes, then condenses and is collected as distillate."
    },
    {
        "id": 5, "type": "mcq", "points": 1.0,
        "title": "Lab Station 5 — Oil + Water",
        "scenario": "Oil and water form two visible liquid layers.",
        "question": "Why can they be separated using a separating funnel or careful decantation?",
        "options": [
            "They have different particle sizes only",
            "They are immiscible and form separate layers",
            "Oil is magnetic",
            "Water evaporates at room temperature instantly"
        ],
        "answer": "They are immiscible and form separate layers",
        "feedback": "Immiscible liquids do not mix and form layers."
    },
    {
        "id": 6, "type": "mcq", "points": 1.0,
        "title": "Lab Station 6 — Ink Investigation",
        "scenario": "A black ink spot may contain several colored dyes.",
        "question": "Which method can show the different dyes?",
        "options": ["Paper chromatography", "Sieving", "Filtration", "Magnetic separation"],
        "answer": "Paper chromatography",
        "feedback": "Different dyes travel different distances with the solvent."
    },
    {
        "id": 7, "type": "mcq", "points": 1.0,
        "title": "Challenge — Homogeneous or Heterogeneous?",
        "scenario": "A learner prepares four mixtures.",
        "question": "Which mixture is HOMOGENEOUS?",
        "options": ["Sand + water", "Oil + water", "Salt completely dissolved in water", "Iron filings + sulfur powder"],
        "answer": "Salt completely dissolved in water",
        "feedback": "A salt solution has a uniform composition throughout."
    },
    {
        "id": 8, "type": "mcq", "points": 1.0,
        "title": "Challenge — Filtration",
        "scenario": "You filter a mixture of sand and water.",
        "question": "What are the sand on the filter paper and the water collected below called?",
        "options": [
            "Filtrate and residue",
            "Residue and filtrate",
            "Solute and solvent",
            "Distillate and condensate"
        ],
        "answer": "Residue and filtrate",
        "feedback": "Residue stays on the filter paper; filtrate passes through."
    },
    {
        "id": 9, "type": "mcq", "points": 1.0,
        "title": "Problem Solving — Mixed Sample",
        "scenario": "A sample contains iron filings, sand, and salt. The salt is soluble in water; the other two are not.",
        "question": "Which plan correctly separates ALL THREE substances?",
        "options": [
            "Add water → filter → magnet",
            "Magnet → add water → filter → evaporate the filtrate",
            "Evaporate → magnet → filter",
            "Filter → distill → sieve"
        ],
        "answer": "Magnet → add water → filter → evaporate the filtrate",
        "feedback": "Remove iron magnetically, dissolve salt, filter out sand, then recover salt by evaporation."
    },
    {
        "id": 10, "type": "mcq", "points": 1.0,
        "title": "Final Lab Decision",
        "scenario": "A student says: “Filtration can separate sugar from sugar solution because the filter paper traps sugar particles.”",
        "question": "Evaluate the statement.",
        "options": [
            "Correct: dissolved sugar is trapped by filter paper",
            "Incorrect: dissolved sugar passes through; evaporation/crystallization can recover it",
            "Correct: all solids are always trapped by filters",
            "Incorrect: a magnet should be used"
        ],
        "answer": "Incorrect: dissolved sugar passes through; evaporation/crystallization can recover it",
        "feedback": "Filtration separates insoluble solids, not dissolved solutes."
    },
]

# ---------- STORAGE ----------
@st.cache_resource
def get_sheet():
    info = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sh = client.open_by_key(st.secrets["sheet_id"])
    try:
        ws = sh.worksheet("Results")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title="Results", rows=1000, cols=20)
        ws.append_row(["Timestamp","Student ID","Student Name","Class","Score /10",
                       "Percentage","Time Used (min)","Status","Attempt Hash"])
    return ws

def normalize_id(s):
    return "".join(ch for ch in s.strip().lower() if ch.isalnum() or ch in "-_")

def attempt_hash(student_id):
    return hashlib.sha256(("G7SEPFA|" + normalize_id(student_id)).encode()).hexdigest()[:16]

def has_submitted(ws, student_id):
    sid = normalize_id(student_id)
    if not sid:
        return False
    records = ws.get_all_records()
    return any(normalize_id(str(r.get("Student ID",""))) == sid for r in records)

def save_result(ws, name, student_id, klass, score, elapsed, status):
    ws.append_row([
        datetime.now(timezone.utc).isoformat(),
        normalize_id(student_id),
        name.strip(),
        klass.strip(),
        round(score, 2),
        round(score/MAX_SCORE*100, 1),
        round(elapsed/60, 1),
        status,
        attempt_hash(student_id)
    ])

# ---------- SESSION ----------
defaults = {
    "started": False, "start_time": None, "student_name": "", "student_id": "",
    "klass": "", "submitted": False, "score": None
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.title("🧪 Separation Mission: Virtual Lab FA")
st.caption("Grade 7 • Separation techniques • 30 minutes • One attempt • Grade /10")

try:
    ws = get_sheet()
except Exception as e:
    st.error("Google Sheets connection failed.")
    st.exception(e)
    st.stop()

# ---------- SIDEBAR / TEACHER ----------
with st.sidebar:
    st.header("Mode")
    mode = st.radio("Choose view", ["Student Lab", "Teacher Dashboard"])
    st.divider()
    st.caption("The teacher dashboard is password protected.")

if mode == "Teacher Dashboard":
    st.subheader("👩‍🏫 Teacher Results Dashboard")
    pw = st.text_input("Teacher password", type="password")
    if pw != st.secrets.get("teacher_password", ""):
        st.info("Enter the teacher password.")
        st.stop()

    records = ws.get_all_records()
    if not records:
        st.info("No learner has submitted yet.")
        st.stop()

    import pandas as pd
    df = pd.DataFrame(records)
    c1,c2,c3 = st.columns(3)
    c1.metric("Submissions", len(df))
    numeric_scores = pd.to_numeric(df["Score /10"], errors="coerce")
    c2.metric("Class Average", f"{numeric_scores.mean():.2f}/10")
    c3.metric("Highest", f"{numeric_scores.max():.2f}/10")
    st.dataframe(df.sort_values("Timestamp", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Download results as CSV", df.to_csv(index=False).encode("utf-8"),
                       "grade7_separation_FA_results.csv", "text/csv")
    st.stop()

# ---------- STUDENT LOGIN ----------
if not st.session_state.started and not st.session_state.submitted:
    st.subheader("Student Entry")
    st.warning("⚠️ Your 30-minute timer starts when you press **Start my one attempt**. Use your real school ID. You cannot submit a second attempt with the same ID.")
    name = st.text_input("Full name")
    sid = st.text_input("School ID / learner code")
    klass = st.text_input("Class / section (example: 7A)")
    agree = st.checkbox("I understand that this is one graded attempt.")
    if st.button("Start my one attempt", type="primary", use_container_width=True):
        if not name.strip() or not sid.strip() or not klass.strip():
            st.error("Complete your name, school ID, and class.")
        elif not agree:
            st.error("Tick the confirmation box.")
        elif has_submitted(ws, sid):
            st.error("This learner ID has already submitted this assessment.")
        else:
            st.session_state.student_name = name.strip()
            st.session_state.student_id = normalize_id(sid)
            st.session_state.klass = klass.strip()
            st.session_state.started = True
            st.session_state.start_time = time.time()
            st.rerun()
    st.stop()

# ---------- ASSESSMENT ----------
if st.session_state.submitted:
    st.success(f"Submitted successfully. Final grade: **{st.session_state.score:.1f} / 10**")
    st.balloons()
    st.info("Your result has been sent to the teacher dashboard. This attempt is now closed.")
    st.stop()

elapsed = time.time() - st.session_state.start_time
remaining = max(0, TIME_LIMIT - elapsed)

m, s = divmod(int(remaining), 60)
st.markdown(f"### ⏱️ Time remaining: **{m:02d}:{s:02d}**")
st.progress(remaining / TIME_LIMIT)
st.caption(f"Learner: {st.session_state.student_name} • {st.session_state.klass}")

# Auto-submit if time is already over on a rerun/interation.
if remaining <= 0:
    score = 0.0
    for q in QUESTIONS:
        selected = st.session_state.get(f"q_{q['id']}")
        if selected == q["answer"]:
            score += q["points"]
    if not has_submitted(ws, st.session_state.student_id):
        save_result(ws, st.session_state.student_name, st.session_state.student_id,
                    st.session_state.klass, score, TIME_LIMIT, "Time expired")
    st.session_state.score = score
    st.session_state.submitted = True
    st.session_state.started = False
    st.rerun()

st.info("🔬 Work through each virtual lab station. Read the sample, choose the correct separation decision, and submit before the timer ends.")

for q in QUESTIONS:
    with st.container(border=True):
        st.markdown(f"#### {q['title']} — {q['points']:.0f} mark")
        st.write(q["scenario"])
        st.markdown(f"**{q['question']}**")
        st.radio(
            "Select one answer:",
            q["options"],
            index=None,
            key=f"q_{q['id']}",
            label_visibility="collapsed"
        )

answered = sum(st.session_state.get(f"q_{q['id']}") is not None for q in QUESTIONS)
st.write(f"Answered: **{answered}/{len(QUESTIONS)}**")

if st.button("Submit final assessment", type="primary", use_container_width=True):
    elapsed = min(time.time() - st.session_state.start_time, TIME_LIMIT)
    score = sum(q["points"] for q in QUESTIONS if st.session_state.get(f"q_{q['id']}") == q["answer"])
    if has_submitted(ws, st.session_state.student_id):
        st.error("A submission already exists for this learner ID.")
    else:
        save_result(ws, st.session_state.student_name, st.session_state.student_id,
                    st.session_state.klass, score, elapsed, "Submitted")
        st.session_state.score = score
        st.session_state.submitted = True
        st.session_state.started = False
        st.rerun()

# Periodic rerun makes the visible timer update. It does not replace server-side identity controls.
time.sleep(1)
st.rerun()

