from typing import List
from .models import EvaluationResult

class ReportGenerator:
    """
    Generates human-readable evaluation reports.
    Day 5 will extend this to output full markdown summaries and JSON datasets.
    """
    
    def generate_markdown_report(self, results: List[EvaluationResult]) -> str:
        """
        Generates a comprehensive markdown report.
        """
        report = "# AI Tutor Evaluation Report\n\n"
        report += "*(Report generation logic will be implemented in Day 5)*\n"
        return report
        
    def export_json(self, results: List[EvaluationResult], filepath: str) -> None:
        """
        Exports raw evaluation results to disk.
        """
        pass
