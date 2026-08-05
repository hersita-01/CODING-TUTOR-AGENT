# AI Coding Tutor Agent

An intelligent, interactive, Socratic AI Coding Tutor built as an 8-week internship capstone project.

## Project Description
This repository contains an advanced AI Coding Tutor Agent that guides students through Python programming errors using the Socratic method rather than giving direct answers. 

## Architecture Overview
The project is built on a Service-Oriented Architecture orchestrated by a **LangGraph State Machine**.
- **LLM Layer:** OpenAI / Groq (Prompt Engineering, JSON mode)
- **Execution Layer:** Local Subprocess Sandbox
- **State Layer:** ChromaDB (RAG/Memory) and SQLite Checkpoints
- **UI Layer:** Streamlit
- **Evaluation Layer:** Automated LLM-as-a-judge MLOps pipeline

## Weekly Roadmap
- **[Week 1](./week1_foundations/README.md)**: Python Foundations
- **[Week 2](./week2_prompt_engineering/README.md)**: Prompt Engineering (Socratic Constraints)
- **[Week 3](./week3_tool_use/README.md)**: Code Sandbox & Tool Use
- **[Week 4](./week4_mini_tutor/README.md)**: Streamlit UI
- **[Week 5](./week5_memory/README.md)**: ChromaDB Memory & Learner Profiles
- **[Week 6](./week6_agent_framework/README.md)**: LangGraph Orchestration & Human-in-the-Loop
- **[Week 7](./week7_evaluation/README.md)**: MLOps Evaluation Framework
- **[Week 8](./week8_capstone/README.md)**: Capstone Architecture & Production Readiness

## Installation & Running
\\ash
pip install -r requirements.txt
streamlit run week4_mini_tutor/day4_streamlit_ui/app.py
\
## Author
Developed as an AI Engineering Capstone.
