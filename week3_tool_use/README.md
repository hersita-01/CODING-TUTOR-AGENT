# Week 3 Overview
**Topic:** Tool Use & Sandbox.
Provides a safe subprocess execution environment for untrusted student code.
- **Workflow:** Validates code via AST parsing, executes it with strict timeout limits, and captures stderr tracebacks.
- **Connection:** Safely confirms user-reported errors before passing them to the LangGraph in Week 6.
