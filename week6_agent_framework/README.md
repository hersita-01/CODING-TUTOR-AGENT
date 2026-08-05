# Week 6 Overview
**Topic:** LangGraph Orchestration.
The core state machine of the Tutor.
- **Workflow:** Routes the student's input through a Diagnose Node -> Pedagogize Node -> Respond Node. Includes Human-in-the-Loop (HITL) checkpoints via SQLite persistent state.
- **Connection:** Orchestrates Weeks 2, 3, and 5 into a single loop.
