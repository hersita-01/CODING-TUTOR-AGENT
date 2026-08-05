"""
Configuration constants for the evaluation framework.
Day 4 and Day 5 will populate this with LLM Judge models, thresholds, and timeout settings.
"""

# The default judge model for evaluating responses
EVALUATION_MODEL = "llama-3.1-8b-instant"

# Threshold for a passing Socratic score
PASSING_SCORE_THRESHOLD = 0.8

# Timeouts for graph execution during automated tests
MAX_EXECUTION_TIME_SECONDS = 15
