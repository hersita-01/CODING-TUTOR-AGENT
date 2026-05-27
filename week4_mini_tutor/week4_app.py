# -----------------------------------
# WEEK 4 - MINI-TUTOR v1
# STREAMLIT UI  —  iOS design language
# -----------------------------------
#
# Run with:   streamlit run week4_app.py
# Requires:   pip install openai streamlit python-dotenv ruff
#             GROQ_API_KEY in .env
# -----------------------------------

import streamlit as st
from dotenv import load_dotenv
from week4_mini_tutor import run_tutor_agent, MAX_CODE_LINES

load_dotenv()

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="Mini-Tutor",
    page_icon="🐍",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------
# iOS-STYLE CSS
# Principles:
#   • Pure white background — no gradients, no gloss
#   • -apple-system font stack (SF Pro on Apple, Segoe on Windows, etc.)
#   • 8pt grid spacing
#   • Hairline 1px borders in #E5E5EA (iOS separator colour)
#   • Rounded corners: 12px for cards, 10px for inputs
#   • Blue accent: #007AFF (iOS system blue)
#   • Secondary text: #8E8E93 (iOS secondary label)
#   • Destructive / error red: #FF3B30
#   • Success green: #34C759
#   • No box-shadows beyond a single subtle 0 1px 3px
# -----------------------------------

st.markdown("""
<style>
/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                 "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 15px;
    background: #FFFFFF;
    color: #1C1C1E;
    -webkit-font-smoothing: antialiased;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 680px !important;
    margin: 0 auto !important;
}

/* ── Top nav bar (iOS-style) ── */
.nav-bar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid #E5E5EA;
    padding: 14px 20px 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-bar .nav-icon {
    font-size: 22px;
    line-height: 1;
}
.nav-bar .nav-title {
    font-size: 17px;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: #1C1C1E;
}
.nav-bar .nav-subtitle {
    font-size: 12px;
    color: #8E8E93;
    margin-left: auto;
    font-weight: 400;
}

/* ── Page body padding ── */
.page-body { padding: 0 20px 100px; }

/* ── Section label (like iOS grouped table headers) ── */
.section-label {
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.4px;
    color: #8E8E93;
    text-transform: uppercase;
    padding: 20px 4px 6px;
}

/* ── Message bubbles ── */
.bubble-wrap { margin-bottom: 2px; }

.bubble-student {
    background: #F2F2F7;
    border-radius: 12px 12px 4px 12px;
    padding: 12px 14px;
    margin: 8px 0 8px 48px;
    font-family: "SF Mono", "Fira Code", "Menlo", "Monaco", monospace;
    font-size: 12.5px;
    line-height: 1.6;
    color: #1C1C1E;
    white-space: pre-wrap;
    word-break: break-word;
    border: 1px solid #E5E5EA;
}

.bubble-label-student {
    font-size: 11px;
    color: #8E8E93;
    text-align: right;
    margin: 4px 4px 0;
    font-weight: 500;
}

.bubble-tutor {
    background: #FFFFFF;
    border-radius: 12px 12px 12px 4px;
    padding: 14px 16px;
    margin: 8px 48px 8px 0;
    color: #1C1C1E;
    font-size: 14.5px;
    line-height: 1.65;
    border: 1px solid #E5E5EA;
}

.bubble-label-tutor {
    font-size: 11px;
    color: #007AFF;
    margin: 4px 4px 0;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Bold Diagnosis / Question / Next Step labels */
.bubble-tutor strong {
    color: #007AFF;
    font-weight: 600;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 56px 24px 32px;
    color: #8E8E93;
}
.empty-state .empty-icon { font-size: 48px; margin-bottom: 12px; }
.empty-state .empty-title {
    font-size: 17px;
    font-weight: 600;
    color: #1C1C1E;
    margin-bottom: 6px;
}
.empty-state .empty-body {
    font-size: 14px;
    line-height: 1.5;
    color: #8E8E93;
}

/* ── Input area ── */
.input-container {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 680px;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-top: 1px solid #E5E5EA;
    padding: 12px 16px 20px;
}

/* Override Streamlit textarea */
.stTextArea textarea {
    font-family: "SF Mono", "Fira Code", "Menlo", monospace !important;
    font-size: 13px !important;
    line-height: 1.55 !important;
    background: #F2F2F7 !important;
    color: #1C1C1E !important;
    border: 1px solid #E5E5EA !important;
    border-radius: 10px !important;
    padding: 10px 12px !important;
    box-shadow: none !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: #007AFF !important;
    box-shadow: 0 0 0 3px rgba(0,122,255,0.12) !important;
    outline: none !important;
}

/* Primary button → iOS blue pill */
.stButton > button[kind="primary"] {
    background: #007AFF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    letter-spacing: -0.2px !important;
    box-shadow: none !important;
    transition: background 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: #0066CC !important;
}
.stButton > button[kind="primary"]:active {
    background: #004EA6 !important;
}

/* Secondary / ghost button */
.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    color: #007AFF !important;
    border: 1px solid #007AFF !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    box-shadow: none !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: #F0F7FF !important;
}

/* Limit hint */
.limit-hint {
    font-size: 11px;
    color: #8E8E93;
    text-align: right;
    margin-top: 4px;
}

/* Warning pill */
.warning-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #FFF3E0;
    border: 1px solid #FFCC80;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    color: #E65100;
    margin: 8px 0;
}

/* Thinking spinner override */
.stSpinner > div {
    border-top-color: #007AFF !important;
}

/* Sidebar iOS-style */
[data-testid="stSidebar"] {
    background: #F2F2F7 !important;
    border-right: 1px solid #E5E5EA !important;
}
[data-testid="stSidebar"] .stMarkdown {
    font-size: 14px;
    color: #1C1C1E;
}

/* Hide label on text area */
.stTextArea label { display: none !important; }
</style>
""", unsafe_allow_html=True)


# -----------------------------------
# SESSION STATE
# -----------------------------------

if "history"       not in st.session_state: st.session_state.history       = []
if "display_turns" not in st.session_state: st.session_state.display_turns = []


# -----------------------------------
# NAV BAR
# -----------------------------------

st.markdown("""
<div class="nav-bar">
  <span class="nav-icon">🐍</span>
  <span class="nav-title">Mini-Tutor</span>
  <span class="nav-subtitle">AI Coding Tutor</span>
</div>
""", unsafe_allow_html=True)


# -----------------------------------
# CONVERSATION
# -----------------------------------

st.markdown('<div class="page-body">', unsafe_allow_html=True)

if not st.session_state.display_turns:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon">💬</div>
      <div class="empty-title">Paste your Python code</div>
      <div class="empty-body">
        The tutor will run it, find the bug, and guide you<br>
        to the fix with a question — not just the answer.
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)
    for turn in st.session_state.display_turns:
        if turn["role"] == "student":
            st.markdown(f"""
            <div class="bubble-wrap">
              <div class="bubble-label-student">You</div>
              <div class="bubble-student">{turn["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bubble-wrap">
              <div class="bubble-label-tutor">🎓 Tutor</div>
              <div class="bubble-tutor">{turn["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------------
# INPUT FORM  (fixed bottom bar)
# -----------------------------------

with st.form("input_form", clear_on_submit=True):
    user_input = st.text_area(
        label="code_input",
        placeholder=(
            "# Paste your Python code here, or ask a question.\n"
            "# Example:\n"
            "numbers = [1, 2, 3]\n"
            "print(numbers[5])"
        ),
        height=130,
        label_visibility="collapsed"
    )

    col_hint, col_btn = st.columns([4, 1])

    with col_hint:
        st.markdown(
            f'<div class="limit-hint">Max {MAX_CODE_LINES} lines · 8 tool calls/turn · packages auto-installed</div>',
            unsafe_allow_html=True
        )

    with col_btn:
        submitted = st.form_submit_button("Send", type="primary", use_container_width=True)


# -----------------------------------
# HANDLE SUBMISSION
# -----------------------------------

if submitted and user_input.strip():

    st.session_state.display_turns.append({
        "role": "student",
        "content": user_input.strip()
    })

    with st.spinner("Thinking…"):
        try:
            reply, updated_history = run_tutor_agent(
                student_message=user_input.strip(),
                conversation_history=st.session_state.history
            )
            st.session_state.history = updated_history

        except Exception as e:
            reply = (
                f"⚠️ Error: {str(e)}\n\n"
                "Make sure `GROQ_API_KEY` is set in your `.env` file and required packages are installed."
            )

    st.session_state.display_turns.append({
        "role": "tutor",
        "content": reply
    })
    st.rerun()

elif submitted and not user_input.strip():
    st.markdown(
        '<div class="warning-pill">⚠️ Please enter some code or a question first.</div>',
        unsafe_allow_html=True
    )


# -----------------------------------
# SIDEBAR
# -----------------------------------

with st.sidebar:
    st.markdown("### Mini-Tutor v1")
    st.markdown(
        "An AI coding tutor that runs your code, diagnoses bugs, "
        "and asks Socratic questions to help you think through the fix."
    )
    st.markdown("---")

    st.markdown("**Tools**")
    st.markdown("🔧 `run_python` — executes code, auto-installs packages")
    st.markdown("🔍 `lint_code` — checks for style issues")
    st.markdown("📖 `doc_search` — 80+ Python concepts")
    st.markdown("---")

    st.markdown("**Tips**")
    st.markdown(
        "- Paste buggy code and describe what you expected\n"
        "- Ask *'What is a for loop?'* to explore concepts\n"
        "- Answer the tutor's questions — that's how you learn\n"
        "- The tutor will never just hand you the fixed code"
    )
    st.markdown("---")

    if st.session_state.display_turns:
        turns = len([t for t in st.session_state.display_turns if t["role"] == "student"])
        st.markdown(f"**{turns}** question{'s' if turns != 1 else ''} this session")
        st.markdown("---")

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.history       = []
        st.session_state.display_turns = []
        st.rerun()