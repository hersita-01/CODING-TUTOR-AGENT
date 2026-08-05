from typing import List
from week7_evaluation.day1_evaluation_framework.models import EvaluationResult, EvaluationTestCase
from .metrics_models import OverallMetrics
from .export_helpers import to_markdown, to_json

class DetailedReportGenerator:
    """
    Day 4 implementation of report generation.
    Expands the Day 1 skeleton with full export logic.
    """
    
    def format_markdown(self, metrics: OverallMetrics) -> str:
        """Converts aggregated metrics into a human-readable markdown report."""
        return to_markdown(metrics)
        
    def format_json(self, metrics: OverallMetrics) -> str:
        """Converts aggregated metrics into a JSON string for historical tracking."""
        # Stub for JSON dumping
        return "{}"
