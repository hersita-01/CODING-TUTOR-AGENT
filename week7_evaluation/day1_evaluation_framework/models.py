from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class EvaluationTestCase:
    """
    Represents a single test scenario for the AI Tutor.
    Day 2 will focus on populating a dataset of these test cases.
    """
    id: str
    student_code: str
    learner_level: str
    expected_error_type: Optional[str] = None
    expected_hint_style: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationMetric:
    """
    Represents a single metric score returned by an evaluator (e.g. LLM Judge).
    Day 4 will define the standard metrics (e.g. Socratic adherence, safety).
    """
    name: str
    score: float  # Normalized between 0.0 and 1.0
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvaluationResult:
    """
    Represents the aggregate result of running an evaluator on a test case.
    Day 5 will use these results to generate final reports.
    """
    test_case_id: str
    evaluator_name: str
    metrics: List[EvaluationMetric] = field(default_factory=list)
    tutor_response: Optional[str] = None
    passed: bool = False
