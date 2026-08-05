import json
from typing import List, Any
from .metrics_models import OverallMetrics

def to_markdown(metrics: OverallMetrics) -> str:
    lines = [
        "# Evaluation Metrics Report",
        f"**Total Cases:** {metrics.total_cases}",
        f"**Passed Cases:** {metrics.passed_cases} ({metrics.pass_rate*100:.1f}%)",
        "",
        "## Average Scores",
        f"- **Diagnosis:** {metrics.average_diagnosis_score:.2f}",
        f"- **Socratic:** {metrics.average_socratic_score:.2f}",
        f"- **Hint:** {metrics.average_hint_score:.2f}",
        f"- **Pedagogy:** {metrics.average_pedagogy_score:.2f}",
        f"- **Safety:** {metrics.average_safety_score:.2f}",
        f"- **Tone:** {metrics.average_tone_score:.2f}",
        f"- **Overall:** {metrics.average_overall_score:.2f}",
        "",
        "## Breakdown by Difficulty"
    ]
    
    for diff, cat in metrics.by_difficulty.items():
        rate = (cat.passed_cases / cat.total_cases * 100) if cat.total_cases > 0 else 0
        lines.append(f"- **{diff.title()}**: {cat.passed_cases}/{cat.total_cases} passed ({rate:.1f}%)")
        
    return "\n".join(lines)

def to_json(metrics: OverallMetrics, filepath: str) -> None:
    # A complete system would recursively dump the dataclass
    pass

def to_csv(metrics: OverallMetrics, filepath: str) -> None:
    # Stub for future exporting
    pass
