from pathlib import Path
from .evaluation_pipeline import EndToEndEvaluationPipeline

def main():
    """
    Entry point for running the Week 7 evaluation pipeline.
    """
    # Resolve path to the Day 2 dataset
    project_root = Path(__file__).resolve().parents[3]
    dataset_path = project_root / "week7_evaluation" / "day2_test_dataset" / "test_cases.json"
    
    pipeline = EndToEndEvaluationPipeline(dataset_path=dataset_path)
    final_report = pipeline.run_pipeline()
    
    print("\n--- PIPELINE COMPLETE ---\n")
    print(final_report)

if __name__ == "__main__":
    main()
