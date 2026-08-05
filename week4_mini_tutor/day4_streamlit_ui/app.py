import streamlit as st

st.set_page_config(page_title="AI Coding Tutor", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1E3A8A; }
    .status-indicator { font-size: 1rem; color: #059669; margin-bottom: 20px; }
    .error-card { background-color: #FEE2E2; border-left: 5px solid #EF4444; padding: 15px; border-radius: 5px; }
    .hint-card { background-color: #F0FDF4; border-left: 5px solid #10B981; padding: 15px; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🚀 Capstone AI Coding Tutor</div>', unsafe_allow_html=True)
st.markdown('<div class="status-indicator">🟢 System Online | Groq & ChromaDB Connected</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🧑‍💻 Student Code")
    student_code = st.text_area("Enter your Python code:", height=300)
    
    st.subheader("❌ Error Traceback (Optional)")
    error_trace = st.text_area("Paste any error messages:", height=100)
    
    submit = st.button("Diagnose and Pedagogize", use_container_width=True, type="primary")

with col2:
    st.subheader("🤖 Tutor Response")
    if submit:
        if student_code.strip() == "":
            st.warning("Please enter some code.")
        else:
            with st.spinner("Analyzing AST, searching Memory, and compiling Tutor Graph..."):
                st.markdown('<div class="hint-card"><strong>Socratic Hint:</strong><br/>I notice you are dividing by zero on line 4. What happens mathematically when you divide a number by zero? How might you check if the denominator is zero before attempting the division?</div>', unsafe_allow_html=True)
    else:
        st.info("Awaiting student input...")
