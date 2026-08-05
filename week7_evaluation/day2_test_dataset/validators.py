from typing import List
from week7_evaluation.day1_evaluation_framework.models import EvaluationTestCase

class DatasetValidator:
    """
    Validates the structure and content of loaded test cases to ensure
    quality and consistency across the evaluation pipeline.
    """
    
    REQUIRED_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
    
    @classmethod
    def validate_suite(cls, test_cases: List[EvaluationTestCase]) -> bool:
        """
        Validates an entire suite of test cases.
        Raises ValueError if any test case violates the schema.
        """
        seen_ids = set()
        
        for case in test_cases:
            # 1. Check for unique IDs
            if case.id in seen_ids:
                raise ValueError(f"Duplicate test case ID found: {case.id}")
            seen_ids.add(case.id)
            
            # 2. Check difficulty enums
            if case.difficulty_level not in cls.REQUIRED_DIFFICULTIES:
                raise ValueError(f"Invalid difficulty '{case.difficulty_level}' in test case {case.id}")
                
            # 3. Check for empty critical fields
            if not case.student_code.strip():
                raise ValueError(f"Test case {case.id} is missing student code.")
            if not case.expected_tutor_behaviour.strip():
                raise ValueError(f"Test case {case.id} is missing expected behaviour.")
                
        return True
