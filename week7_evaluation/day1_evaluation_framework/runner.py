import sys
from pathlib import Path
from typing import List, Dict, Any

from .models import EvaluationTestCase, EvaluationResult
from .base_evaluator import BaseEvaluator

# To ensure the runner can orchestrate the Week 6 graph
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(_PROJECT_ROOT / "week6_agent_framework" / "day5_human_in_loop"))

try:
    from human_in_loop_graph import build_human_in_loop_graph
    _GRAPH_AVAILABLE = True
except ImportError:
    _GRAPH_AVAILABLE = False


class EvaluationRunner:
    """
    Orchestrates the evaluation pipeline.
    Day 5 will fully implement this runner to execute test suites in parallel.
    """
    
    def __init__(self, evaluators: List[BaseEvaluator]):
        self.evaluators = evaluators
        if _GRAPH_AVAILABLE:
            self.graph = build_human_in_loop_graph()
        else:
            self.graph = None
            
    def run_suite(self, test_cases: List[EvaluationTestCase]) -> List[EvaluationResult]:
        """
        Runs the tutor graph on a suite of test cases and executes all evaluators.
        """
        results = []
        
        if not self.graph:
            print("Warning: Week 6 Graph not available. Returning empty results.")
            return results
            
        for case in test_cases:
            # 1. Setup mock state based on test case
            initial_state = {
                "student_id": f"eval_user_{case.id}",
                "student_code": case.student_code,
                "learner_level": case.learner_level,
                # Clear previous state
                "metadata": {}
            }
            
            # 2. Invoke the Week 6 Human-in-the-Loop graph
            # This serves as a stub for Day 1. Later days will actually invoke the graph 
            # and potentially override the 'interrupt' checkpoints for automated testing.
            final_state: Dict[str, Any] = {} # e.g. self.graph.invoke(initial_state)
            
            # 3. Run all evaluators on the resulting state
            for evaluator in self.evaluators:
                # result = evaluator.evaluate(case, final_state)
                # results.append(result)
                pass
                
        return results
