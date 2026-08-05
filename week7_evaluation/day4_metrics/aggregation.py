from typing import List, Dict
from week7_evaluation.day1_evaluation_framework.models import EvaluationResult, EvaluationTestCase
from .metrics_models import OverallMetrics, CategoryMetrics

def aggregate_results(results: List[EvaluationResult], test_cases: List[EvaluationTestCase]) -> OverallMetrics:
    """
    Processes raw evaluation results and computes structured aggregations.
    """
    metrics = OverallMetrics(total_cases=len(results))
    if not results:
        return metrics
        
    case_map = {tc.id: tc for tc in test_cases}
    
    total_diagnosis = 0.0
    total_socratic = 0.0
    total_hint = 0.0
    total_pedagogy = 0.0
    total_safety = 0.0
    total_tone = 0.0
    total_overall = 0.0
    
    for res in results:
        if res.passed:
            metrics.passed_cases += 1
            
        case = case_map.get(res.test_case_id)
        if not case:
            continue
            
        # Group by Error Category
        cat = case.expected_error_category
        if cat not in metrics.by_error_category:
            metrics.by_error_category[cat] = CategoryMetrics()
        metrics.by_error_category[cat].total_cases += 1
        if res.passed: metrics.by_error_category[cat].passed_cases += 1
        
        # Group by Difficulty
        diff = case.difficulty_level
        if diff not in metrics.by_difficulty:
            metrics.by_difficulty[diff] = CategoryMetrics()
        metrics.by_difficulty[diff].total_cases += 1
        if res.passed: metrics.by_difficulty[diff].passed_cases += 1
            
        # Accumulate scores from standard Day 1 metrics
        score_map = {m.name: m.score for m in res.metrics}
        total_diagnosis += score_map.get("diagnosis_score", 0.0)
        total_socratic += score_map.get("socratic_score", 0.0)
        total_hint += score_map.get("hint_score", 0.0)
        total_pedagogy += score_map.get("pedagogy_score", 0.0)
        total_safety += score_map.get("safety_score", 0.0)
        total_tone += score_map.get("tone_score", 0.0)
        total_overall += score_map.get("overall_score", 0.0)
        
    n = metrics.total_cases
    metrics.pass_rate = metrics.passed_cases / n
    metrics.average_diagnosis_score = total_diagnosis / n
    metrics.average_socratic_score = total_socratic / n
    metrics.average_hint_score = total_hint / n
    metrics.average_pedagogy_score = total_pedagogy / n
    metrics.average_safety_score = total_safety / n
    metrics.average_tone_score = total_tone / n
    metrics.average_overall_score = total_overall / n
    
    return metrics
