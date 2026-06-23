# -----------------------------------
# WEEK 4 - MINI-TUTOR v1
# STREAMLIT UI  —  Teal-to-Blue Gradient
# -----------------------------------
#
# Run with:   streamlit run week4_app.py
# Requires:   pip install openai streamlit python-dotenv ruff
#             GROQ_API_KEY in .env
# -----------------------------------

import streamlit as st
from dotenv import load_dotenv
from week4_mini_tutor import run_tutor_agent
from config import MAX_CODE_LINES

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
# DESIGN TOKENS
#
# Background gradient: dark teal #0D1F2D → deep blue #0A0F1E
# Surface cards:       semi-transparent white overlays (glassmorphism lite)
# Accent:              bright teal #00C9B1  + blue highlight #4A9EFF
# Text:                #FFFFFF primary, #A8C4D0 secondary (always readable)
# Student bubble:      teal-tinted dark  #0F2A38 with teal border
# Tutor bubble:        blue-tinted dark  #0D1A30 with blue border
# Labels:              Diagnosis=teal, Question=amber, Next Step=violet
# -----------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --grad-start:   #0D1F2D;
    --grad-end:     #0A0F1E;
    --surface:      rgba(255,255,255,0.06);
    --surface-hover:rgba(255,255,255,0.10);
    --border:       rgba(255,255,255,0.10);
    --border-teal:  rgba(0,201,177,0.40);
    --border-blue:  rgba(74,158,255,0.40);
    --text:         #FFFFFF;
    --text-sub:     #A8C4D0;
    --teal:         #00C9B1;
    --blue:         #4A9EFF;
    --amber:        #F5C26B;
    --violet:       #C792EA;
    --danger:       #FF6B6B;
}

/* ── Base & gradient canvas ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
.main {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: linear-gradient(160deg, var(--grad-start) 0%, var(--grad-end) 100%) !important;
    background-attachment: fixed !important;
    color: var(--text) !important;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 0 !important;
    max-width: 740px !important;
    margin: 0 auto !important;
}

/* ── Nav bar — frosted glass over gradient ── */
.nav-bar {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(13,31,45,0.80);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-bottom: 1px solid var(--border);
    padding: 15px 24px 13px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.nav-bar .nav-icon { font-size: 24px; line-height: 1; }
.nav-bar .nav-title {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.3px;
    color: var(--text);
    background: linear-gradient(90deg, var(--teal), var(--blue));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.nav-bar .nav-badge {
    margin-left: 8px;
    background: rgba(0,201,177,0.15);
    border: 1px solid var(--border-teal);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    color: var(--teal);
    letter-spacing: 0.3px;
}
.nav-bar .nav-subtitle {
    font-size: 12px;
    color: var(--text-sub);
    margin-left: auto;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Page body ── */
.page-body { padding: 0 20px 120px; }

.section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    color: var(--text-sub);
    text-transform: uppercase;
    padding: 24px 4px 10px;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 72px 28px 40px;
}
.empty-state .empty-icon {
    font-size: 52px;
    margin-bottom: 18px;
    display: block;
}
.empty-state .empty-title {
    font-size: 22px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 10px;
    letter-spacing: -0.3px;
}
.empty-state .empty-body {
    font-size: 15px;
    line-height: 1.65;
    color: var(--text-sub);
    max-width: 380px;
    margin: 0 auto 28px;
}
.empty-state .feature-pills {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 8px;
}
.feature-pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12.5px;
    color: var(--text-sub);
    font-weight: 500;
}

/* ── Message bubbles ── */
.bubble-wrap { margin-bottom: 6px; }

/* Student bubble — teal tint */
.bubble-student {
    background: rgba(0,201,177,0.08);
    border: 1px solid var(--border-teal);
    border-radius: 14px 14px 4px 14px;
    padding: 14px 16px;
    margin: 6px 0 6px 52px;
    font-family: 'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
    font-size: 13px;
    line-height: 1.7;
    color: #D4F5F0;
    white-space: pre-wrap;
    word-break: break-word;
}
.bubble-label-student {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: var(--teal);
    text-align: right;
    margin: 4px 6px 2px;
    text-transform: uppercase;
}

/* Tutor bubble — blue tint */
.bubble-tutor {
    background: rgba(74,158,255,0.07);
    border: 1px solid var(--border-blue);
    border-radius: 14px 14px 14px 4px;
    padding: 16px 20px;
    margin: 6px 52px 6px 0;
    color: #E8F2FF;
    font-size: 15px;
    line-height: 1.75;
}
.bubble-label-tutor {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: var(--blue);
    margin: 4px 4px 2px 0;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* Colour the three structured reply labels inline */
.bubble-tutor .label-diagnosis { color: var(--teal);   font-weight: 700; }
.bubble-tutor .label-question  { color: var(--amber);  font-weight: 700; }
.bubble-tutor .label-nextstep  { color: var(--violet); font-weight: 700; }

/* ── Divider between turns ── */
.turn-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 16px 0;
    opacity: 0.5;
}

/* ── Fixed input bar ── */
.input-bar {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100%;
    max-width: 740px;
    background: rgba(13,31,45,0.90);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border-top: 1px solid var(--border);
    padding: 14px 18px 22px;
}

/* Streamlit textarea — fully recoloured */
[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.stTextArea textarea {
    font-family: 'JetBrains Mono', 'SF Mono', monospace !important;
    font-size: 13.5px !important;
    line-height: 1.65 !important;
    background: rgba(255,255,255,0.06) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 13px 15px !important;
    box-shadow: none !important;
    resize: none !important;
    caret-color: var(--teal) !important;
    transition: border-color 0.2s ease !important;
}
.stTextArea textarea::placeholder {
    color: rgba(168,196,208,0.55) !important;
}
.stTextArea textarea:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px rgba(0,201,177,0.15) !important;
    outline: none !important;
    background: rgba(255,255,255,0.09) !important;
}
.stTextArea label { display: none !important; }

/* Send button — teal-to-blue gradient */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--teal) 0%, var(--blue) 100%) !important;
    color: #05131E !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    padding: 11px 22px !important;
    letter-spacing: -0.1px !important;
    box-shadow: 0 4px 18px rgba(0,201,177,0.30) !important;
    transition: opacity 0.15s ease, transform 0.1s ease !important;
}
.stButton > button[kind="primary"]:hover {
    opacity: 0.88 !important;
    box-shadow: 0 6px 24px rgba(0,201,177,0.40) !important;
}
.stButton > button[kind="primary"]:active {
    transform: scale(0.97) !important;
}

/* Ghost / secondary button */
.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    color: var(--teal) !important;
    border: 1px solid var(--border-teal) !important;
    border-radius: 10px !important;
    font-size: 13.5px !important;
    font-weight: 600 !important;
    padding: 9px 16px !important;
    box-shadow: none !important;
    transition: background 0.15s ease !important;
}
.stButton > button:not([kind="primary"]):hover {
    background: rgba(0,201,177,0.10) !important;
}

.limit-hint {
    font-size: 11px;
    color: var(--text-sub);
    text-align: right;
    margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
    opacity: 0.7;
}

/* Warning pill */
.warning-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245,194,107,0.12);
    border: 1px solid rgba(245,194,107,0.40);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 13px;
    color: var(--amber);
    margin: 8px 0;
}

/* Spinner */
.stSpinner > div { border-top-color: var(--teal) !important; }
.stSpinner p { color: var(--text-sub) !important; }

/* ── Sidebar — teal-tinted dark ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1E2C 0%, #08111E 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {
    font-size: 13.5px;
    color: var(--text-sub) !important;
    line-height: 1.65;
}
[data-testid="stSidebar"] .stMarkdown h3 {
    color: var(--text) !important;
    font-size: 16px;
    font-weight: 700;
}
[data-testid="stSidebar"] .stMarkdown strong { color: var(--teal) !important; }
[data-testid="stSidebar"] code {
    background: rgba(0,201,177,0.10) !important;
    color: var(--teal) !important;
    padding: 2px 6px;
    border-radius: 5px;
    font-size: 12.5px;
}
[data-testid="stSidebar"] hr { border-color: var(--border) !important; }

/* Markdown inside chat */
.stMarkdown, .stMarkdown p, .stMarkdown li { color: var(--text) !important; }
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
  <span class="nav-badge">v1</span>
  <span class="nav-subtitle">AI Coding Tutor</span>
</div>
""", unsafe_allow_html=True)


# -----------------------------------
# HELPER — colour the three structured labels in tutor replies
# Wraps "Diagnosis:" / "Question:" / "Next Step:" in colour spans
# so they stand out from body text visually.
# -----------------------------------

def _strip_tool_traces(text: str) -> str:
    """Remove any <function/tool_name(...)> lines the model leaks into its reply.

    The agent sometimes includes its own tool-call trace in the assistant
    content string. These are internal scaffolding and must never be shown
    to the student.
    """
    import re
    # Matches the full line: <function/run_python({...})> or </function>
    text = re.sub(r'</?function[^>]*>', '', text)
    # Also strip bare tool-result JSON blocks if they sneak through
    text = re.sub(r'\{"success".*?\}', '', text, flags=re.DOTALL)
    # Collapse runs of blank lines left behind
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _colour_labels(text: str) -> str:
    import re, html as html_lib
    text = _strip_tool_traces(text)
    safe = html_lib.escape(text)
    safe = re.sub(r'(Diagnosis:)',
                  r'<span class="label-diagnosis">\1</span>', safe)
    safe = re.sub(r'(Question:)',
                  r'<span class="label-question">\1</span>', safe)
    safe = re.sub(r'(Next Step:)',
                  r'<span class="label-nextstep">\1</span>', safe)
    # Restore line breaks
    safe = safe.replace('\n', '<br>')
    return safe


# -----------------------------------
# CONVERSATION AREA
# -----------------------------------

st.markdown('<div class="page-body">', unsafe_allow_html=True)

if not st.session_state.display_turns:
    st.markdown("""
    <div class="empty-state">
      <span class="empty-icon">💬</span>
      <div class="empty-title">Paste your Python code</div>
      <div class="empty-body">
        The tutor runs it, finds the bug, and guides you<br>
        to the fix with a question — not just the answer.
      </div>
      <div class="feature-pills">
        <span class="feature-pill">🔧 Runs your code</span>
        <span class="feature-pill">🔍 Lints for issues</span>
        <span class="feature-pill">📖 Explains concepts</span>
        <span class="feature-pill">🎓 Socratic questions</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown('<div class="section-label">Conversation</div>', unsafe_allow_html=True)

    for i, turn in enumerate(st.session_state.display_turns):
        if i > 0:
            st.markdown('<hr class="turn-divider">', unsafe_allow_html=True)

        if turn["role"] == "student":
            import html as html_lib
            safe_content = html_lib.escape(turn["content"])
            st.markdown(f"""
            <div class="bubble-wrap">
              <div class="bubble-label-student">You</div>
              <div class="bubble-student">{safe_content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            coloured = _colour_labels(_strip_tool_traces(turn["content"]))
            st.markdown(f"""
            <div class="bubble-wrap">
              <div class="bubble-label-tutor">🎓 Tutor</div>
              <div class="bubble-tutor">{coloured}</div>
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
        height=120,
        label_visibility="collapsed"
    )

    col_hint, col_btn = st.columns([4, 1])

    with col_hint:
        st.markdown(
            f'<div class="limit-hint">Max {MAX_CODE_LINES} lines · 8 tool calls/turn · packages auto-installed</div>',
            unsafe_allow_html=True
        )
    with col_btn:
        submitted = st.form_submit_button("Send →", type="primary", use_container_width=True)


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
                f"Error: {str(e)}\n\n"
                "Make sure GROQ_API_KEY is set in your .env file "
                "and required packages are installed."
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
    st.markdown("### Mini-Tutor v2")
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

    # Show which weeks loaded successfully
    try:
        from week4_mini_tutor import _WEEK2_AVAILABLE, _WEEK3_AVAILABLE
        w2 = "✓ Week 2 sandbox active" if _WEEK2_AVAILABLE else "✗ Week 2 NOT FOUND"
        w3 = "✓ Week 3 tools active"   if _WEEK3_AVAILABLE else "✗ Week 3 NOT FOUND"
        w2_color = "teal" if _WEEK2_AVAILABLE else "#FF6B6B"
        w3_color = "teal" if _WEEK3_AVAILABLE else "#FF6B6B"
        st.markdown(f'<span style="color:{w2_color};font-size:12px">{w2}</span>', unsafe_allow_html=True)
        st.markdown(f'<span style="color:{w3_color};font-size:12px">{w3}</span>', unsafe_allow_html=True)
    except Exception:
        pass
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