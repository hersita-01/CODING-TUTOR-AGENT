# AI Coding Tutor Agent

An AI-powered coding tutor that helps beginner programmers learn Python through guided explanations, debugging support, and Socratic questioning instead of directly giving answers.

---

# Week 1 Progress

## Day 1 — Environment Setup

Completed:
- Ubuntu development setup
- Git & GitHub configuration
- Python virtual environment setup
- VS Code setup
- Installed AI development libraries

Technologies:
- Python
- Git
- LangChain
- LangGraph
- Streamlit
- FastAPI
- ChromaDB

---

## Day 2 — Python Basics

Learned:
- Variables & data types
- Lists & dictionaries
- Conditions (`if-else`)
- Loops (`for` loop)

Programs created:
- Calculator
- Even/Odd checker
- Student marks program
- List iteration exercises

Skills gained:
- Writing basic Python programs
- Using loops and conditions
- Working with collections

---

## Day 3 — Functions & Debugging

Learned:
- Functions
- Parameters & return values
- Error handling (`try-except`)
- File handling
- Debugging common Python errors

Practiced:
- NameError
- IndexError
- TypeError

Skills gained:
- Reading Python errors
- Writing reusable functions
- File read/write operations
- Debugging workflow

---

## Day 4 — LLM API Integration

Learned:
- Working with LLM APIs
- Using Groq API with OpenAI-compatible SDK
- Secure API key handling using `.env`
- Temperature & Max Tokens
- API error handling

Programs created:
- `groq_test.py`
- `first_llm.py`
- `temperature_test.py`
- `tokens_test.py`

Skills gained:
- AI API integration
- Prompt execution
- Model parameter tuning
- Secure credential management

---

## Day 5 — Prompt Engineering & AI Tutor Behavior

Learned:
- Prompt Engineering
- AI Tutor Design
- Role-based prompting
- Socratic questioning
- AI behavior control

Built:
- AI Coding Tutor using Groq API
- Tutor-style prompts
- Guided debugging interactions

Files created:
- `tutor_prompt.py`
- `notes.txt`

Example Tutor Prompt:

```python
prompt = """
You are a beginner-friendly Python tutor.

Rules:
- Never directly give the answer
- Ask guiding questions
- Encourage the student
- Explain concepts simply

Student Question:
"My Python loop is not working."
"""
```

Skills gained:
- Designing tutor-style AI behavior
- Controlling AI responses using prompts
- Building interactive learning experiences

---

# Week 2 Progress

## Day 1 — Bug Explainer

Built:
- `bug_explainer.py`
- A system/user prompt flow that explains beginner programming errors without immediately giving corrected code

Skills gained:
- Separating system prompts from user prompts
- Writing beginner-friendly debugging instructions
- Asking one guiding question at the end of an explanation

## Day 2 — Few-Shot Socratic Hints

Built:
- `few_shot_bug_explainer.py`
- Few-shot examples showing good Socratic hints and one bad answer-revealing hint

Skills gained:
- Using examples to shape model behavior
- Running student code in a subprocess with a timeout
- Capturing runtime errors for tutor feedback

## Day 3 — Socratic Tutor Variants

Built:
- `friendly_tutor.py`
- `socratic_hint_generator.py`
- `chain_of_thought_tutor.py`
- `strict_socratic_mode.py`
- `safe_python_runner.py`

Skills gained:
- Comparing friendly, guided, and strict Socratic tutor behavior
- Avoiding direct fixes
- Asking targeted debugging questions

## Day 4 — Structured Outputs

Built:
- `structured_tutor_response.py`
- JSON tutor response format with `diagnosis`, `hint`, `follow_up_question`, and `confidence`

Skills gained:
- Producing structured model output for future UI integration
- Parsing and validating JSON responses

## Day 5 — Streaming, Cost, and Model Choice

Built:
- `streaming_tutor.py`
- Notes on model size, latency, token limits, and cost-control habits

Skills gained:
- Streaming model responses
- Capping `max_tokens`
- Logging model and latency basics

---

# Current Project Structure

```text
coding-tutor-agent/
│
├── week1-foundations/
│   ├── day2-python-basics/
│   │   ├── basics.py
│   │   └── student.py
│   ├── day3-functions-debugging/
│   │   ├── functions.py
│   │   └── notes.txt
│   ├── day4-llm-api/
│   │   ├── first_llm.py
│   │   ├── groq_test.py
│   │   ├── temperature_test.py
│   │   └── tokens_test.py
│   └── day5-prompt-engineering/
│       ├── tutor_prompt.py
│       └── notes.txt
│
├── week2-prompt-engineering/
│   ├── prompt_library.md
│   ├── day1-bug-explainer/
│   ├── day2-few-shot/
│   ├── day3-socratic/
│   ├── day4-structured-output/
│   └── day5-streaming-cost/
│
├── tutor-env/
├── README.md
└── .gitignore
```

---

# Goals

- Build an AI-powered coding tutor
- Help beginners debug Python code
- Teach through guided questioning
- Explore AI agents and prompt engineering
- Learn modern AI application development
