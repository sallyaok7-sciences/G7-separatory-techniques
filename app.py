import streamlit as st
import time
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Grade 7 Separation Lab FA",
    page_icon="🧪",
    layout="centered"
)

TIME_LIMIT = 30 * 60  # 30 minutes
MAX_SCORE = 10

# ---------------------------------------------------------
# QUESTIONS
# ---------------------------------------------------------

QUESTIONS = [
    {
        "question": "1. A mixture contains iron filings and sand. Which technique should be used first?",
        "options": [
            "Filtration",
            "Magnetic separation",
            "Evaporation",
            "Decantation"
        ],
        "answer": "Magnetic separation"
    },
    {
        "question": "2. Which technique is best for separating an insoluble solid from a liquid?",
        "options": [
            "Filtration",
            "Evaporation",
            "Magnetic separation",
            "Crystallization"
        ],
        "answer": "Filtration"
    },
    {
        "question": "3. Salt is completely dissolved in water. What type of mixture is formed?",
        "options": [
            "Heterogeneous mixture",
            "Homogeneous mixture",
            "Suspension",
            "Two-layer mixture"
        ],
        "answer": "Homogeneous mixture"
    },
    {
        "question": "4. You need to obtain salt from salt water. Which technique is most suitable?",
        "options": [
            "Filtration",
            "Magnetic separation",
            "Evaporation",
            "Sieving"
        ],
        "answer": "Evaporation"
    },
    {
        "question": "5. Sand settles at the bottom of a beaker containing water. What should you do before decantation?",
        "options": [
            "Shake the mixture",
            "Allow the solid to settle",
            "Heat the mixture strongly",
            "Pass a magnet through it"
        ],
        "answer": "Allow the solid to settle"
    },
    {
        "question": "6. Which property makes sieving useful for separating a mixture?",
        "options": [
            "Difference in particle size",
            "Difference in magnetism",
            "Difference in solubility",
            "Difference in boiling point"
        ],
        "answer": "Difference in particle size"
    },
    {
        "question": "7. A learner has muddy water. Which sequence would best produce clearer water?",
        "options": [
            "Evaporation → magnetism",
            "Sedimentation → decantation → filtration",
            "Sieving → evaporation",
            "Magnetism → filtration"
        ],
        "answer": "Sedimentation → decantation → filtration"
    },
    {
        "question": "8. Oil and water form two visible layers. This mixture is:",
        "options": [
            "Homogeneous",
            "Heterogeneous",
            "A pure substance",
            "A solution"
        ],
        "answer": "Heterogeneous"
    },
    {
        "question": "9. A mixture contains gravel, sand and water. Which is the BEST sequence for separating the components?",
        "options": [
            "Sieving → filtration",
            "Evaporation → magnetic separation",
            "Filtration → magnetism",
            "Decantation → magnetism"
        ],
        "answer": "Sieving → filtration"
    },
    {
        "question": "10. A student filters salt water expecting the salt to remain on the filter paper. Why will this NOT work?",
        "options": [
            "Salt particles are magnetic",
            "Dissolved salt passes through the filter with the water",
            "Water cannot pass through filter paper",
            "Salt is an insoluble substance"
        ],
        "answer": "Dissolved salt passes through the filter with the water"
    }
]

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

defaults = {
    "started": False,
    "submitted": False,
    "start_time": None,
    "student_name": "",
    "student_id": "",
    "student_class": "",
    "score": None,
    "finish_time": None,
    "answers": {}
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("🧪 Separation Mission: Virtual Lab FA")

st.caption(
    "Grade 7 • Separation Techniques • 30 minutes • "
    "One attempt • Grade /10"
)

# ---------------------------------------------------------
# FINAL RESULT
# ---------------------------------------------------------

if st.session_state.submitted:

    percentage = int(
        (st.session_state.score / MAX_SCORE) * 100
    )

    elapsed = (
        st.session_state.finish_time -
        st.session_state.start_time
    )

    minutes_used = round(elapsed / 60, 1)

    st.success("✅ Assessment submitted successfully!")

    st.header("🎓 FINAL RESULT")

    st.markdown(
        f"""
### Student Submission Receipt

**Student:** {st.session_state.student_name}  
**Student ID:** {st.session_state.student_id}  
**Class:** {st.session_state.student_class}

---

# Score: {st.session_state.score} / 10

**Percentage:** {percentage}%  
**Time used:** {minutes_used} minutes  
**Submitted:** {datetime.now().strftime("%d/%m/%Y %H:%M")}

---
        """
    )

    if percentage >= 80:
        st.success("🌟 Excellent work!")
    elif percentage >= 60:
        st.info("👍 Good work!")
    elif percentage >= 50:
        st.warning("Keep practicing the separation techniques.")
    else:
        st.warning("Review the separation techniques carefully.")

    st.error(
        "📸 TAKE A SCREENSHOT OF THIS RESULT PAGE "
        "AND SUBMIT IT TO YOUR TEACHER."
    )

    st.info(
        "Your screenshot must clearly show your name, "
        "Student ID, class and score."
    )

    st.stop()

# ---------------------------------------------------------
# STUDENT LOGIN
# ---------------------------------------------------------

if not st.session_state.started:

    st.subheader("🔐 Student Entry")

    st.write(
        "Enter your information carefully. "
        "The 30-minute timer begins when you press **Start Mission**."
    )

    name = st.text_input("Full name")

    student_id = st.text_input("Student ID")

    student_class = st.selectbox(
        "Class",
        ["Select class", "7A", "7B", "7C"]
    )

    confirmation = st.checkbox(
        "I confirm that the information above is correct "
        "and I am ready to begin my assessment."
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

        elif not confirmation:
            st.error(
                "Please confirm that you are ready to begin."
            )

        else:
            st.session_state.student_name = name.strip()
            st.session_state.student_id = student_id.strip()
            st.session_state.student_class = student_class

            st.session_state.start_time = time.time()
            st.session_state.started = True

            st.rerun()

    st.stop()

# ---------------------------------------------------------
# TIMER
# ---------------------------------------------------------

elapsed = time.time() - st.session_state.start_time
remaining = max(0, TIME_LIMIT - elapsed)

minutes = int(remaining // 60)
seconds = int(remaining % 60)

st.subheader(
    f"⏱️ Time Remaining: {minutes:02d}:{seconds:02d}"
)

progress = remaining / TIME_LIMIT
st.progress(progress)

st.write(
    f"👤 **{st.session_state.student_name}** "
    f"| ID: **{st.session_state.student_id}** "
    f"| Class: **{st.session_state.student_class}**"
)

st.divider()

# ---------------------------------------------------------
# QUESTIONS
# ---------------------------------------------------------

for i, q in enumerate(QUESTIONS):

    st.markdown(f"### {q['question']}")

    choice = st.radio(
        "Choose one answer:",
        q["options"],
        index=None,
        key=f"question_{i}"
    )

    st.session_state.answers[i] = choice

    st.divider()

# ---------------------------------------------------------
# SUBMISSION FUNCTION
# ---------------------------------------------------------

def calculate_score():

    score = 0

    for i, q in enumerate(QUESTIONS):

        answer = st.session_state.answers.get(i)

        if answer == q["answer"]:
            score += 1

    return score

# ---------------------------------------------------------
# TIME EXPIRED
# ---------------------------------------------------------

if remaining <= 0:

    st.session_state.score = calculate_score()
    st.session_state.finish_time = time.time()
    st.session_state.submitted = True

    st.rerun()

# ---------------------------------------------------------
# MANUAL SUBMISSION
# ---------------------------------------------------------

answered = sum(
    1
    for answer in st.session_state.answers.values()
    if answer is not None
)

st.write(
    f"**Questions answered: {answered}/{len(QUESTIONS)}**"
)

confirm_submit = st.checkbox(
    "I have checked my answers and I am ready to submit."
)

if st.button(
    "📤 SUBMIT FINAL ANSWERS",
    type="primary",
    use_container_width=True
):

    if answered < len(QUESTIONS):

        st.warning(
            f"You answered {answered}/10 questions. "
            "Please answer all questions before submitting."
        )

    elif not confirm_submit:

        st.warning(
            "Please confirm that you are ready to submit."
        )

    else:

        st.session_state.score = calculate_score()
        st.session_state.finish_time = time.time()
        st.session_state.submitted = True

        st.rerun()

# ---------------------------------------------------------
# TIMER REFRESH
# ---------------------------------------------------------

time.sleep(1)
st.rerun()
