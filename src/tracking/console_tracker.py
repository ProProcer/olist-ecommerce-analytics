from omegaconf import DictConfig
from src.schemas.evaluation import ValidationResult
import pprint

class ConsoleTracker:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def log_run(self, run_name: str, config: DictConfig, result: ValidationResult):
        print(f"\n{'='*20} RUN: {run_name} {'='*20}")
        print("\n--- OOF Metrics ---")
        pprint.pprint(result.oof_metrics)
        
        print("\n--- CV Mean Metrics ---")
        pprint.pprint(result.mean_metrics)
        
        if self.verbose:
            print("\n--- Fold Metrics ---")
            for i, fold in enumerate(result.fold_metrics):
                print(f"Fold {i}: {fold}")
        print(f"{'='*50}\n")