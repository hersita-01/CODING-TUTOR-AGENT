from typing import List
from week7_evaluation.day1_evaluation_framework.models import EvaluationResult, EvaluationTestCase
from .aggregation import aggregate_results
from .metrics_models import OverallMetrics
from .report_generator import DetailedReportGenerator

class MetricsEngine:
    """
    Central engine for Day 4 Metrics.
    Coordinates the aggregation of raw results, computes advanced statistics,
    and interfaces with the report generation layer.
    """
    
    def __init__(self):
        self.report_generator = DetailedReportGenerator()
        
    def process_results(self, results: List[EvaluationResult], test_cases: List[EvaluationTestCase]) -> OverallMetrics:
        """
        Takes raw evaluation results and produces a structured, aggregated metrics model.
        """
        return aggregate_results(results, test_cases)
        
    def generate_summary_report(self, metrics: OverallMetrics) -> str:
        """
        Uses the ReportGenerator to format the metrics into a Markdown report.
        """
        # We pass the pre-computed metrics into the generator (assuming a refactored generator interface)
        return self.report_generator.format_markdown(metrics)
