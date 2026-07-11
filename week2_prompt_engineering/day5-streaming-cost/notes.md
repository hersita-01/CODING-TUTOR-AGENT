# Day 5 Notes: Streaming, Cost, and Model Size

Goal: make tutor responses feel faster while keeping token usage controlled.

Choices:
- Model: `llama-3.1-8b-instant` for low latency during practice.
- `max_tokens`: capped at 180 so beginner hints stay short.
- `temperature`: 0.3 to keep explanations stable and avoid rambling.
- Streaming: enabled so the learner sees text as it is generated.

Cost-control habits:
- Keep system prompts clear and reusable.
- Cap `max_tokens` for every request.
- Log model name, latency, and token limits.
- Use a small model for drafts and only upgrade when quality requires it.
