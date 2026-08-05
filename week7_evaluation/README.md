# Week 7 Overview
**Topic:** MLOps Evaluation Framework.
A complete CI/CD testing pipeline for evaluating the AI Tutor's pedagogical quality.
- **Architecture:** BaseEvaluator ABC -> LLMJudgeEngine (Groq JSON mode) -> MetricsEngine.
- **Workflow:** Automates testing the Tutor against a static JSON dataset of student programs, exporting statistical markdown reports.
