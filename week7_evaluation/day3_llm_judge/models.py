import json
from dataclasses import dataclass, field
from typing import List

@dataclass
class LLMJudgeResult:
    """
    Structured output model for the LLM Judge.
    Matches the exact schema required by the Week 7 Day 3 handbook.
    """
    diagnosis_score: float
    socratic_score: float
    hint_score: float
    pedagogy_score: float
    safety_score: float
    tone_score: float
    overall_score: float
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    feedback: str = ""
    passed: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> "LLMJudgeResult":
        return cls(
            diagnosis_score=float(data.get("diagnosis_score", 0.0)),
            socratic_score=float(data.get("socratic_score", 0.0)),
            hint_score=float(data.get("hint_score", 0.0)),
            pedagogy_score=float(data.get("pedagogy_score", 0.0)),
            safety_score=float(data.get("safety_score", 0.0)),
            tone_score=float(data.get("tone_score", 0.0)),
            overall_score=float(data.get("overall_score", 0.0)),
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            feedback=data.get("feedback", ""),
            passed=bool(data.get("passed", False))
        )
