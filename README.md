# AI Coding Tutor Agent

An AI-powered Python Coding Tutor that helps beginner programmers learn through guided debugging, Socratic questioning, safe code execution, memory-aware reasoning, and AI-assisted feedback.

Instead of directly providing answers, the tutor encourages students to analyze errors, understand programming concepts, and discover solutions independently.

---

# Project Overview

The AI Coding Tutor Agent was developed as a six-week learning project that progressively explores:

* Python fundamentals
* Prompt engineering
* AI tool integration
* Safe code execution
* Memory systems
* Retrieval-Augmented Generation (RAG)
* Agent frameworks
* Educational software development

Each week builds upon the previous one, culminating in a fully functional AI-powered tutoring application.

---

# Project Objectives

The primary goals of this project are to:

* Help beginners understand Python errors and debugging techniques.
* Provide guided, Socratic-style tutoring instead of direct answers.
* Execute and analyze student code safely.
* Use AI tools to generate context-aware educational feedback.
* Build memory-aware tutoring systems.
* Explore Retrieval-Augmented Generation (RAG).
* Understand modern AI agent frameworks.
* Explore production-oriented AI application development practices.

---

# Technologies Used

| Category               | Technology                 |
| ---------------------- | -------------------------- |
| Programming Language   | Python                     |
| AI Provider            | Groq API                   |
| AI SDK                 | OpenAI Python SDK          |
| Agent Framework        | LangGraph                  |
| LLM Framework          | LangChain                  |
| Frontend               | Streamlit                  |
| Embedding Model        | SentenceTransformers       |
| Vector Database        | ChromaDB                   |
| Code Validation        | AST (Abstract Syntax Tree) |
| Safe Execution         | subprocess                 |
| Environment Management | python-dotenv              |
| Linting                | Ruff                       |
| Version Control        | Git & GitHub               |

---

# Project Structure

```text
CODING-TUTOR-AGENT/
│
├── week1-foundations/
│   ├── day2-python-basics/
│   ├── day3-functions-debugging/
│   ├── day4-llm-api/
│   ├── day5-prompt-engineering/
│   └── week1_README.md
│
├── week2-prompt-engineering/
│   ├── day1-bug-explainer/
│   ├── day2-few-shot/
│   ├── day3-socratic/
│   ├── day4-structured-output/
│   ├── day5-streaming-cost/
│   ├── prompt_library.md
│   └── README.md
│
├── week3-tool-use/
│   ├── day1_tool_concepts.py
│   ├── day2-tool-schemas/
│   ├── day3-tool-loop/
│   ├── day4-more-tools/
│   ├── day5-error-handling/
│   └── README.md
│
├── week4_mini_tutor/
│   ├── config.py
│   ├── prompts.py
│   ├── week4_app.py
│   ├── week4_mini_tutor.py
│   └── week4_README.md
│
├── week5-memory/
│   ├── day1-memory-manager/
│   ├── day2-embeddings/
│   ├── day3-vector-store/
│   ├── day4-chunking-strategies/
│   ├── day5-rag-pipeline/
│   └── README.md
│
├── week6-agent-frameworks/
│   ├── day1-framework-tour/
│   ├── day2-langgraph-basics/
│   ├── day3-tutoring-graph/
│   ├── day4-state-persistence/
│   ├── day5-human-loop/
│   └── README.md
│
├── .env
├── .gitignore
└── README.md
```

---

# Week 1 – Foundations

Focus: Learning Python fundamentals and understanding how large language models can be integrated into applications.

Implemented:

* Python programming exercises.
* Functions and debugging practice.
* API integration using Groq.
* Temperature and token experiments.
* Initial prompt engineering concepts.
* Basic AI tutor prototypes.

Key Learning:

Understanding how language models generate responses and how prompts influence output quality.

---

# Week 2 – Prompt Engineering

Focus: Improving tutoring quality through prompt design.

Implemented:

* Bug explanation assistants.
* Few-shot prompting examples.
* Socratic tutoring workflows.
* Chain-of-thought reasoning experiments.
* Structured tutor responses.
* Streaming AI responses.
* Safe Python execution using AST-based validation.
* Enhanced traceback parsing and execution result handling.

Key Learning:

Prompt design significantly affects the quality, consistency, and educational value of AI-generated feedback.

---

# Week 3 – Tool Use

Focus: Building AI systems that use tools instead of relying only on model reasoning.

Implemented:

* Tool schemas and tool-calling workflows.
* Code execution tools.
* Validation and analysis pipelines.
* Runtime error analysis.
* Multi-step tool execution loops.
* Safe execution workflows.
* Tool-based tutoring agents.

Key Learning:

AI systems become more reliable when they can execute code, inspect results, and use external tools to make decisions.

---

# Week 4 – Mini Tutor

Focus: Integrating all previous concepts into a complete AI-powered tutoring application.

Implemented:

* Command Line Interface (CLI).
* Streamlit-based web application.
* Safe code execution pipeline.
* AST-based security validation.
* Timeout protection.
* Memory protection.
* Structured traceback analysis.
* AI-generated Socratic debugging guidance.
* Modular configuration and prompt management.
* Improved project organization and maintainability.

Key Learning:

Combining prompt engineering, tool use, and secure execution creates a practical educational AI application.

---

# Week 5 – Memory and Retrieval

Focus: Equipping the tutor with memory and retrieval capabilities so that it can remember past interactions, retrieve relevant knowledge, and provide context-aware assistance.

Implemented:

* Conversation memory management.
* Learner profile storage.
* Embedding generation using SentenceTransformers.
* Document chunking strategies.
* ChromaDB vector storage.
* Semantic document retrieval.
* Metadata enrichment and filtering.
* Chunking strategy evaluation framework.
* Retrieval-Augmented Generation (RAG) pipeline.
* Citation-aware document search.

Key Learning:

Large language models become significantly more useful when they can retrieve relevant information from external knowledge sources and remember previous interactions. Retrieval systems and memory management enable personalized and context-aware tutoring experiences.

---

# Week 6 – Agent Frameworks

Focus: Moving beyond hand-written execution loops and rebuilding the AI tutor using production-grade agent frameworks.

Implemented:

* Study of modern AI frameworks.
* Comparison of LangChain, LangGraph, LlamaIndex, and Haystack.
* Graph-based workflow design.
* Stateful multi-step tutoring pipelines.
* Node and edge orchestration.
* Shared state management.
* Conditional routing logic.
* Persistent learner profiles.
* Human-in-the-loop checkpoints.
* Production-oriented agent architecture.

Key Learning:

As AI systems become more complex, manually managing workflows becomes increasingly difficult. Agent frameworks such as LangGraph provide structured state management, tool orchestration, persistence, and human oversight, making them suitable for building production-grade AI applications.

---

# Core Features

* Socratic tutoring approach.
* Safe Python code execution.
* Runtime error detection.
* Structured traceback analysis.
* AST-based security validation.
* Timeout and memory protection.
* AI-assisted debugging guidance.
* Conversation memory.
* Learner profile management.
* Semantic document retrieval.
* Retrieval-Augmented Generation (RAG).
* Vector database integration.
* Tool-calling workflows.
* Stateful agent execution.
* Human-in-the-loop checkpoints.
* Command Line Interface (CLI).
* Streamlit Web Interface.
* Modular and maintainable architecture.

---

# Example Workflow

Student Code:

```python
numbers = [1, 2, 3]
print(numbers[10])
```

Runtime Error:

```text
IndexError: list index out of range
```

Tutor Response:

```text
Diagnosis:
The program is trying to access a list index that does not exist.

Question:
How many elements are currently stored in the list?

Next Step:
Check the valid index range before accessing an element.
```

---

# Running the Project

Clone the repository:

```bash
git clone https://github.com/hersita-01/CODING-TUTOR-AGENT.git
cd CODING-TUTOR-AGENT
```

Create a virtual environment:

```bash
python -m venv tutor-env
```

Activate the environment.

Windows:

```bash
tutor-env\Scripts\activate
```

Linux/macOS:

```bash
source tutor-env/bin/activate
```

Install dependencies:

```bash
pip install openai streamlit python-dotenv ruff sentence-transformers chromadb langchain langgraph
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Run the Mini Tutor:

CLI:

```bash
python week4_mini_tutor/week4_mini_tutor.py
```

Streamlit:

```bash
streamlit run week4_mini_tutor/week4_app.py
```

---

# Learning Outcomes

Through this project, the following concepts were explored:

* Python programming fundamentals.
* Prompt engineering.
* Socratic tutoring design.
* Safe code execution.
* Tool calling and tool orchestration.
* Retrieval-Augmented Generation (RAG).
* Memory systems.
* Vector databases.
* Agent frameworks.
* Stateful workflows.
* Human-in-the-loop systems.
* Educational AI design.
* Full-stack AI application development.

---

# Author

Developed as part of an AI engineering learning journey focused on:

* Prompt Engineering
* AI Agents
* Tool Calling
* Safe Code Execution
* Memory Systems
* Retrieval-Augmented Generation
* Agent Frameworks
* Educational AI Systems
* Full-Stack AI Application Development
