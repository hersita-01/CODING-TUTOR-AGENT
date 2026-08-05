from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class CategoryMetrics:
    total_cases: int = 0
    passed_cases: int = 0
    average_score: float = 0.0

@dataclass
class OverallMetrics:
    total_cases: int = 0
    passed_cases: int = 0
    pass_rate: float = 0.0
    average_overall_score: float = 0.0
    average_diagnosis_score: float = 0.0
    average_socratic_score: float = 0.0
    average_hint_score: float = 0.0
    average_pedagogy_score: float = 0.0
    average_safety_score: float = 0.0
    average_tone_score: float = 0.0
    
    # Breakdowns
    by_error_category: Dict[str, CategoryMetrics] = field(default_factory=dict)
    by_difficulty: Dict[str, CategoryMetrics] = field(default_factory=dict)
    by_learning_concept: Dict[str, CategoryMetrics] = field(default_factory=dict)
    
    metadata: Dict[str, Any] = field(default_factory=dict)
