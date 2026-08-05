import os
from pathlib import Path
from typing import List

from week7_evaluation.day1_evaluation_framework.runner import EvaluationRunner
from week7_evaluation.day1_evaluation_framework.models import EvaluationResult, EvaluationTestCase
from week7_evaluation.day2_test_dataset.loader import load_test_cases
from week7_evaluation.day3_llm_judge.evaluator import EducationalQualityEvaluator
from week7_evaluation.day4_metrics.metrics_engine import MetricsEngine
from .results_manager import save_results, save_report

class EndToEndEvaluationPipeline:
    """
    Orchestrates the entire evaluation lifecycle by wiring together
    Day 1 (Runner), Day 2 (Dataset), Day 3 (Judge), and Day 4 (Metrics).
    """
    
    def __init__(self, dataset_path: str | Path):
        self.dataset_path = Path(dataset_path)
        
        # 1. Instantiate the LLM Judge (Day 3)
        self.judge = EducationalQualityEvaluator()
        
        # 2. Instantiate the Execution Runner (Day 1) with the Judge
        self.runner = EvaluationRunner(evaluators=[self.judge])
        
        # 3. Instantiate the Metrics Engine (Day 4)
        self.metrics_engine = MetricsEngine()
        
    def run_pipeline(self) -> str:
        """
        Executes the end-to-end evaluation flow.
        """
        print(f"Loading dataset from {self.dataset_path}...")
        test_cases: List[EvaluationTestCase] = load_test_cases(self.dataset_path)
        
        print(f"Executing {len(test_cases)} test cases through the Week 6 Graph and LLM Judge...")
        raw_results: List[EvaluationResult] = self.runner.run_suite(test_cases)
        
        print("Calculating metrics...")
        overall_metrics = self.metrics_engine.process_results(raw_results, test_cases)
        
        print("Generating report...")
        report_markdown = self.metrics_engine.generate_summary_report(overall_metrics)
        
        print("Saving artifacts...")
        # Save raw JSON results
        save_results(raw_results, "latest_results.json")
        # Save Markdown report
        save_report(report_markdown, "latest_report.md")
        
        return report_markdown
