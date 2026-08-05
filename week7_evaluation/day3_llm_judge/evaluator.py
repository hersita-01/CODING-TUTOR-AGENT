from typing import Any, Dict

from week7_evaluation.day1_evaluation_framework.base_evaluator import BaseEvaluator
from week7_evaluation.day1_evaluation_framework.models import EvaluationTestCase, EvaluationResult, EvaluationMetric

from .engine import LLMJudgeEngine

class EducationalQualityEvaluator(BaseEvaluator):
    """
    Implements the BaseEvaluator interface from Day 1.
    Uses the LLMJudgeEngine to generate scores for educational quality.
    """
    
    def __init__(self):
        self.engine = LLMJudgeEngine()
        
    def get_name(self) -> str:
        return "EducationalQualityJudge"
        
    def evaluate(self, test_case: EvaluationTestCase, tutor_state: Dict[str, Any]) -> EvaluationResult:
        # Extract the final generated response from the Week 6 graph state
        tutor_response = tutor_state.get("response", "")
        
        # Invoke the LLM Judge Engine
        judge_output = self.engine.evaluate(
            student_code=test_case.student_code,
            expected_error=test_case.expected_error_category,
            expected_behaviour=test_case.expected_tutor_behaviour,
            tutor_response=tutor_response
        )
        
        metrics = []
        passed = False
        
        if judge_output:
            # Convert structured LLMJudgeResult fields into EvaluationMetric objects (Day 1 structure)
            metrics = [
                EvaluationMetric(name="diagnosis_score", score=judge_output.diagnosis_score, reasoning="LLM evaluated"),
                EvaluationMetric(name="socratic_score", score=judge_output.socratic_score, reasoning="LLM evaluated"),
                EvaluationMetric(name="hint_score", score=judge_output.hint_score, reasoning="LLM evaluated"),
                EvaluationMetric(name="pedagogy_score", score=judge_output.pedagogy_score, reasoning="LLM evaluated"),
                EvaluationMetric(name="safety_score", score=judge_output.safety_score, reasoning="LLM evaluated"),
                EvaluationMetric(name="tone_score", score=judge_output.tone_score, reasoning="LLM evaluated"),
                EvaluationMetric(name="overall_score", score=judge_output.overall_score, reasoning="LLM evaluated")
            ]
            passed = judge_output.passed
            # We can pack qualitative feedback into the overall EvaluationResult metadata
            metadata = {
                "strengths": judge_output.strengths,
                "weaknesses": judge_output.weaknesses,
                "feedback": judge_output.feedback
            }
        else:
            metadata = {"error": "LLM Judge failed to return valid output"}
            
        return EvaluationResult(
            test_case_id=test_case.id,
            evaluator_name=self.get_name(),
            metrics=metrics,
            tutor_response=tutor_response,
            passed=passed
        )
