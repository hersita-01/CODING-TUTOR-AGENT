from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class EvaluationTestCase:
    """
    Represents a single test scenario for the AI Tutor.
    Expanded in Day 2 to include robust evaluation criteria.
    """
    id: str
    title: str
    student_code: str
    learning_concept: str
    expected_error_category: str
    difficulty_level: str
    expected_tutor_behaviour: str
    expected_socratic_objective: str
    expected_hint_level: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationMetric:
    """
    Represents a single metric score returned by an evaluator.
    """
    name: str
    score: float  # Normalized between 0.0 and 1.0
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationResult:
    """
    Represents the aggregate result of running an evaluator on a test case.
    """
    test_case_id: str
    evaluator_name: str
    metrics: List[EvaluationMetric] = field(default_factory=list)
    tutor_response: Optional[str] = None
    passed: bool = False
