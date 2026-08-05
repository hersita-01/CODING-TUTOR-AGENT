import json
from pathlib import Path
from typing import List, Dict, Any

from week7_evaluation.day1_evaluation_framework.models import EvaluationTestCase

def load_test_cases(file_path: str | Path) -> List[EvaluationTestCase]:
    """
    Loads evaluation test cases from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing the dataset.
        
    Returns:
        A list of strongly typed EvaluationTestCase objects.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Test case file not found: {path}")
        
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    test_cases = []
    for item in data:
        # Validate required fields (basic validation happens during object instantiation,
        # but custom validation can be added via validators.py)
        test_case = EvaluationTestCase(
            id=item["id"],
            title=item["title"],
            student_code=item["student_code"],
            learning_concept=item["learning_concept"],
            expected_error_category=item["expected_error_category"],
            difficulty_level=item["difficulty_level"],
            expected_tutor_behaviour=item["expected_tutor_behaviour"],
            expected_socratic_objective=item["expected_socratic_objective"],
            expected_hint_level=item.get("expected_hint_level"),
            metadata=item.get("metadata", {})
        )
        test_cases.append(test_case)
        
    return test_cases
