import streamlit as st
import time
import hashlib
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Separation Mission – Virtual Lab FA",
    page_icon="🧪",
    layout="wide"
)

TIME_LIMIT = 30 * 60  # 30 minutes
MAX_SCORE = 10

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
    .main-title {
        text-align:center;
        font-size:42px;
        font-weight:800;
        margin-bottom:0px;
    }

    .subtitle {
        text-align:center;
        color:#666;
        margin-bottom:25px;
    }

    .lab-card {
        padding:22px;
        border:2px solid #dedede;
        border-radius:18px;
        background-color:#fafafa;
        margin-bottom:15px;
    }

    .observation {
        padding:18px;
        border-left:6px solid #ff9f1c;
        background:#fff7e8;
        border-radius:8px;
        margin-top:15px;
        margin-bottom:15px;
    }

    .success-box {
        padding:18px;
        background:#eaf8ef;
        border-radius:12px;
        border:1px solid #a7d8b4;
        margin:15px 0;
    }

    .mission-box {
        padding:18px;
        background:#eef6ff;
        border-radius:12px;
        border:1px solid #b7d8ff;
        margin-bottom:20px;
    }

    .equipment {
        font-size:30px;
        text-align:center;
    }

    .timer {
        font-size:22px;
        font-weight:700;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# QUESTIONS / MARKING
# ============================================================

def initialize_state():

    defaults = {
        "started": False,
        "submitted": False,
        "start_time": None,
        "student_name": "",
        "student_id": "",
        "student_class": "",
        "score": 0,
        "stage": 1,

        # Mission answers
        "m1_technique": None,
        "m1_result": None,

        "m2_technique": None,
        "m2_observation": None,

        "m3_tool": None,
        "m3_observation": None,

        "m4_step1": None,
        "m4_step2": None,
        "m4_step3": None,

        "q_residue": None,
        "q_filtrate": None,
        "q_evaporation": None,

        "finalized": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def remaining_time():

    if not st.session_state.started:
        return TIME_LIMIT

    elapsed = int(time.time() - st.session_state.start_time)
    return max(0, TIME_LIMIT - elapsed)


def format_time(seconds):
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def calculate_score():

    score = 0

    # Mission 1 = 2 marks
    if st.session_state.m1_technique == "Filtration":
        score += 1

    if st.session_state.q_residue == "Sand":
        score += 1

    # Mission 2 = 2 marks
    if st.session_state.m2_technique == "Evaporation":
        score += 1

    if st.session_state.q_evaporation == "Salt remains while water evaporates":
        score += 1

    # Mission 3 = 2 marks
    if st.session_state.m3_tool == "Magnet":
        score += 1

    if st.session_state.m3_observation == "Iron is attracted to the magnet":
        score += 1

    # Final challenge = 3 marks
    if st.session_state.m4_step1 == "Use a magnet":
        score += 1

    if st.session_state.m4_step2 == "Add water, then filter":
        score += 1

    if st.session_state.m4_step3 == "Evaporate the filtrate":
        score += 1

    # Scientific vocabulary = 1 mark
    if st.session_state.q_filtrate == "The liquid that passes through the filter":
        score += 1

    return score


def finish_assessment(status="Submitted"):

    st.session_state.score = calculate_score()
    st.session_state.submitted = True
    st.session_state.finalized = True
    st.session_state.status = status


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🧪 Separation Mission: Virtual Lab FA</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Grade 7 • Separation Techniques • 30 minutes • One attempt • Grade /10'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# STUDENT ENTRY
# ============================================================

if not st.session_state.started:

    st.subheader("🔐 Student Entry")

    st.info(
        "You are about to enter the Separation Laboratory. "
        "Read carefully, perform the experiments and use your observations "
        "to solve each challenge."
    )

    name = st.text_input("Full Name")

    student_id = st.text_input("Student ID")

    student_class = st.selectbox(
        "Class",
        ["Select class", "Grade 7A", "Grade 7B", "Grade 7C"]
    )

    confirm = st.checkbox(
        "I confirm that the information above is correct and I am ready "
        "to begin my assessment."
    )

    if st.button(
        "🚀 START MISSION",
        type="primary",
        use_container_width=True
    ):

        if not name.strip():
            st.error("Please enter your full name.")

        elif not student_id.strip():
            st.error("Please enter your Student ID.")

        elif student_class == "Select class":
            st.error("Please select your class.")

        elif not confirm:
            st.error("Please tick the confirmation box.")

        else:

            st.session_state.student_name = name.strip()
            st.session_state.student_id = student_id.strip()
            st.session_state.student_class = student_class

            st.session_state.started = True
            st.session_state.start_time = time.time()

            st.rerun()

    st.stop()


# ============================================================
# TIMER
# ============================================================

remaining = remaining_time()

if remaining <= 0 and not st.session_state.submitted:
    finish_assessment("Time expired")


# ============================================================
# RESULTS
# ============================================================

if st.session_state.submitted:

    score = st.session_state.score

    elapsed = min(
        TIME_LIMIT,
        int(time.time() - st.session_state.start_time)
    )

    minutes_used = round(elapsed / 60, 1)

    percentage = int((score / MAX_SCORE) * 100)

    code_raw = (
        st.session_state.student_id +
        st.session_state.student_name +
        str(score)
    )

    submission_code = hashlib.sha256(
        code_raw.encode()
    ).hexdigest()[:8].upper()

    st.balloons()

    st.success("🏁 MISSION COMPLETED!")

    st.markdown("---")

    st.header("🧾 Mission Report")

    col1, col2 = st.columns(2)

    with col1:
        st.write(
            f"**Student:** {st.session_state.student_name}"
        )
        st.write(
            f"**Student ID:** {st.session_state.student_id}"
        )
        st.write(
            f"**Class:** {st.session_state.student_class}"
        )

    with col2:
        st.metric("Final Grade", f"{score} / 10")
        st.metric("Percentage", f"{percentage}%")
        st.metric("Time Used", f"{minutes_used} min")

    st.markdown("---")

    if score >= 9:
        st.success(
            "🏆 Excellent laboratory work! "
            "You demonstrated excellent understanding of separation techniques."
        )

    elif score >= 7:
        st.success(
            "⭐ Very good work! Your separation skills are developing very well."
        )

    elif score >= 5:
        st.warning(
            "🔬 Mission completed. Review the purpose of each separation technique."
        )

    else:
        st.error(
            "🧪 Mission completed. More practice with separation techniques is recommended."
        )

    st.subheader("🔐 Submission Code")

    st.code(submission_code)

    st.info(
        "📸 Take a screenshot of this Mission Report and submit it to your teacher. "
        "Your screenshot must clearly show your name, ID, class, grade and submission code."
    )

    st.stop()


# ============================================================
# TOP STATUS
# ============================================================

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.write(
        f"👩‍🔬 **Scientist:** {st.session_state.student_name}"
    )

with col2:
    st.write(
        f"🏫 **{st.session_state.student_class}**"
    )

with col3:
    st.markdown(
        f'<div class="timer">⏱️ {format_time(remaining)}</div>',
        unsafe_allow_html=True
    )

st.progress((TIME_LIMIT - remaining) / TIME_LIMIT)

st.markdown("---")


# ============================================================
# LAB INTRODUCTION
# ============================================================

st.header("🔬 Welcome to the Separation Laboratory")

st.markdown("""
<div class="mission-box">

### 🎯 Your Mission

Several mixtures have arrived at the laboratory.

Your job is NOT simply to name separation techniques.

You must:

🧠 examine each mixture  
🧰 select suitable laboratory equipment  
🧪 perform a separation  
👀 observe what happens  
📋 interpret your results  
🏆 complete the final separation challenge

**Your laboratory decisions will determine your grade.**

</div>
""", unsafe_allow_html=True)


# ============================================================
# MISSION 1
# ============================================================

st.header("🧪 Experiment 1 — The Muddy Sample")

st.markdown("""
<div class="lab-card">

A beaker containing **sand + water** has been delivered to your laboratory.

The sand does not dissolve.

Your goal is to obtain **clear water**.

### 🧰 Laboratory bench

🧲 Magnet &nbsp;&nbsp;
🔻 Filter funnel &nbsp;&nbsp;
📄 Filter paper &nbsp;&nbsp;
🔥 Evaporating dish &nbsp;&nbsp;
🥄 Spatula

</div>
""", unsafe_allow_html=True)

st.write("### Step 1 — Choose the technique you want to try")

m1 = st.radio(
    "Select your experimental procedure:",
    [
        "Choose...",
        "Filtration",
        "Evaporation",
        "Magnetic separation",
        "Decantation"
    ],
    key="m1_radio"
)

if st.button("🧪 PERFORM EXPERIMENT 1"):

    st.session_state.m1_technique = m1

    if m1 == "Filtration":

        st.session_state.m1_result = "success"

    elif m1 == "Evaporation":

        st.session_state.m1_result = "evaporation"

    elif m1 == "Magnetic separation":

        st.session_state.m1_result = "magnet"

    elif m1 == "Decantation":

        st.session_state.m1_result = "decant"

    else:

        st.warning("Choose a technique first.")


if st.session_state.m1_result == "success":

    st.markdown("""
<div class="success-box">

### 🔬 Experimental observation

🥛 Sand + water  
⬇️  
🔻 **FILTER + FILTER PAPER**  
⬇️

💧 Clear water passes through the filter.

🏖️ Sand remains on the filter paper.

</div>
""", unsafe_allow_html=True)

elif st.session_state.m1_result == "evaporation":

    st.markdown("""
<div class="observation">

🔥 You heat the mixture.

The water begins to evaporate, but this was not the most suitable
procedure for your goal of **collecting clear liquid water**.

Think about which technique allows liquid to pass through while
an insoluble solid is retained.

</div>
""", unsafe_allow_html=True)

elif st.session_state.m1_result == "magnet":

    st.markdown("""
<div class="observation">

🧲 You place a magnet near the mixture.

Nothing happens.

The sand is **not attracted to the magnet**.

Choose a technique based on the fact that sand is an
**insoluble solid in water**.

</div>
""", unsafe_allow_html=True)

elif st.session_state.m1_result == "decant":

    st.markdown("""
<div class="observation">

🥛 You carefully pour the water into another beaker.

Some water separates, but small sand particles may still be carried
with it.

There is another technique that produces a clearer liquid.

</div>
""", unsafe_allow_html=True)


if st.session_state.m1_result:

    st.write("### 🔎 Analyse your experiment")

    st.session_state.q_residue = st.radio(
        "Which substance forms the RESIDUE?",
        [
            "Choose...",
            "Water",
            "Sand",
            "Both sand and water"
        ]
    )

    st.session_state.q_filtrate = st.radio(
        "What is a filtrate?",
        [
            "Choose...",
            "The solid remaining on the filter paper",
            "The liquid that passes through the filter",
            "The original mixture"
        ]
    )


st.markdown("---")


# ============================================================
# MISSION 2
# ============================================================

st.header("💧 Experiment 2 — Recover the Salt")

st.markdown("""
<div class="lab-card">

You now receive a beaker containing:

### 💧 SALT WATER

The salt has completely dissolved.

Your mission is to **recover the solid salt**.

What should you do?

</div>
""", unsafe_allow_html=True)

m2 = st.radio(
    "Choose your technique:",
    [
        "Choose...",
        "Filtration",
        "Evaporation",
        "Magnetic separation",
        "Sieving"
    ],
    key="m2_radio"
)

if st.button("🔥 PERFORM EXPERIMENT 2"):

    st.session_state.m2_technique = m2

    if m2 == "Evaporation":
        st.session_state.m2_observation = "correct"
    elif m2 != "Choose...":
        st.session_state.m2_observation = "incorrect"


if st.session_state.m2_observation == "correct":

    st.markdown("""
<div class="success-box">

### 🔥 Heating simulation

💧🧂 Salt solution  
⬇️

🔥 🔥 🔥

💨 Water particles escape as water vapour.

⬇️

🧂 **Salt remains in the evaporating dish.**

### Observation:
A dissolved solid can be recovered from its solution by
**evaporating the solvent**.

</div>
""", unsafe_allow_html=True)


elif st.session_state.m2_observation == "incorrect":

    st.markdown("""
<div class="observation">

### 👀 Observation

The salt is dissolved in the water.

You cannot remove dissolved salt using this technique.

Think about what would happen if the **water were removed as a vapour**.

</div>
""", unsafe_allow_html=True)


if st.session_state.m2_observation:

    st.session_state.q_evaporation = st.radio(
        "What happens during the correct separation?",
        [
            "Choose...",
            "Salt evaporates and water remains",
            "Salt remains while water evaporates",
            "Salt is trapped by filter paper",
            "The magnet attracts the salt"
        ]
    )


st.markdown("---")


# ============================================================
# MISSION 3
# ============================================================

st.header("🧲 Experiment 3 — The Mystery Metal")

st.markdown("""
<div class="lab-card">

A tray contains:

### 🏖️ Sand + ⚙️ Iron filings

Both substances are solids.

You must separate the iron **without adding water**.

Choose a laboratory tool and test it.

</div>
""", unsafe_allow_html=True)

tool = st.radio(
    "Choose your tool:",
    [
        "Choose...",
        "Magnet",
        "Filter funnel",
        "Evaporating dish",
        "Beaker"
    ],
    key="m3_radio"
)

if st.button("🧲 TEST THE TOOL"):

    st.session_state.m3_tool = tool

    if tool == "Magnet":
        st.session_state.m3_observation = (
            "Iron is attracted to the magnet"
        )

    elif tool != "Choose...":
        st.session_state.m3_observation = "No useful separation occurs"


if st.session_state.m3_observation == "Iron is attracted to the magnet":

    st.markdown("""
<div class="success-box">

### 🧲 Simulation

Before:

⚫ ⚙️ ⚫ ⚙️ ⚫ ⚙️ ⚫

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🧲  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;⬆️  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;⚙️⚙️⚙️

### 👀 Observation

The **iron filings move toward the magnet**.

The sand remains in the tray.

</div>
""", unsafe_allow_html=True)


elif st.session_state.m3_observation == "No useful separation occurs":

    st.markdown("""
<div class="observation">

### 👀 Observation

The substances remain mixed.

Consider a **physical property of iron** that sand does not have.

</div>
""", unsafe_allow_html=True)


st.markdown("---")


# ============================================================
# FINAL CHALLENGE
# ============================================================

st.header("🚨 FINAL LAB CHALLENGE")

st.markdown("""
<div class="mission-box">

## 🧪 Complex Mixture

A laboratory accident has produced a mixture containing:

### ⚙️ IRON FILINGS + 🏖️ SAND + 🧂 SALT

Your supervisor wants **all three solids separated**.

You must design the correct separation sequence.

Think carefully about the properties of each substance.

</div>
""", unsafe_allow_html=True)


st.write("### 🥇 STEP 1")

st.session_state.m4_step1 = st.selectbox(
    "What should you do FIRST?",
    [
        "Choose...",
        "Use a magnet",
        "Filter the dry mixture",
        "Evaporate the mixture",
        "Heat everything strongly"
    ]
)


if st.session_state.m4_step1 == "Use a magnet":

    st.success(
        "🧲 Observation: Iron filings are removed. "
        "Sand and salt remain."
    )


st.write("### 🥈 STEP 2")

st.session_state.m4_step2 = st.selectbox(
    "How will you separate the sand from the salt?",
    [
        "Choose...",
        "Add water, then filter",
        "Use another magnet",
        "Evaporate immediately",
        "Use only a sieve"
    ]
)


if st.session_state.m4_step2 == "Add water, then filter":

    st.success("""
💧 Salt dissolves in water.

🔻 Sand remains as the residue.

💧🧂 Salt solution passes through as the filtrate.
""")


st.write("### 🥉 STEP 3")

st.session_state.m4_step3 = st.selectbox(
    "You now have salt solution. How will you recover the salt?",
    [
        "Choose...",
        "Evaporate the filtrate",
        "Filter it again",
        "Use a magnet",
        "Add more water"
    ]
)


if st.session_state.m4_step3 == "Evaporate the filtrate":

    st.success("""
🔥 Water evaporates.

🧂 Solid salt remains.

You have successfully designed a complete separation procedure!
""")


st.markdown("---")


# ============================================================
# SUBMISSION
# ============================================================

st.header("📋 Laboratory Submission")

st.warning(
    "Before submitting, check your experimental decisions. "
    "After submission, your final grade will be calculated."
)

ready = st.checkbox(
    "I have completed all laboratory experiments and I am ready to submit."
)

if st.button(
    "🏁 SUBMIT FINAL LAB REPORT",
    type="primary",
    use_container_width=True
):

    if not ready:

        st.error(
            "Please confirm that you are ready to submit."
        )

    else:

        finish_assessment()

        st.rerun()


# ============================================================
# AUTO REFRESH TIMER
# ============================================================

time.sleep(1)
st.rerun()
