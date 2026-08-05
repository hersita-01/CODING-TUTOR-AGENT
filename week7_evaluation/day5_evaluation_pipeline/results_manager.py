import json
import dataclasses
from pathlib import Path
from typing import List, Any
from week7_evaluation.day1_evaluation_framework.models import EvaluationResult

def save_results(results: List[EvaluationResult], filename: str) -> None:
    """
    Saves the raw structured evaluation results to disk.
    """
    out_dir = Path(__file__).resolve().parent / "output"
    out_dir.mkdir(exist_ok=True)
    
    out_path = out_dir / filename
    
    class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o: Any) -> Any:
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)
            
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, cls=EnhancedJSONEncoder, indent=4)

def save_report(markdown_content: str, filename: str) -> None:
    """
    Saves the formatted Markdown evaluation report to disk.
    """
    out_dir = Path(__file__).resolve().parent / "output"
    out_dir.mkdir(exist_ok=True)
    
    out_path = out_dir / filename
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
