# -----------------------------------
# WEEK 4 — CONFIGURATION
# week4_mini_tutor/ config.py
#
# Single source of truth for all tunable constants.
# Week 4 imports from here; Week 2 and Week 3 are NOT modified.
# -----------------------------------

# Agent behaviour
MAX_TOOL_CALLS  = 8
MAX_CODE_LINES  = 30          # ≤30 lines per snippet (Week 4 brief requirement)
TIMEOUT_SECONDS = 5           # Week 2 default is 3 s; 5 s gives interactive code more room
MAX_RETRIES     = 2           # Retry budget for rate-limit / network errors
RETRY_BACKOFF_S = 2           # Base back-off multiplier (seconds × attempt)

# Model
GROQ_MODEL = "llama-3.3-70b-versatile"