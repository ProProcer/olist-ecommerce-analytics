import mlflow
from omegaconf import OmegaConf, DictConfig
from src.schemas.evaluation import ValidationResult
import pandas as pd

class MLflowTracker:
    def __init__(self, experiment_name : str, tracking_uri : str = None):
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)

    def log_run(self, run_name : str, config : DictConfig, result : ValidationResult):
        
        with mlflow.start_run(run_name = run_name) as run:
            resolved_cfg = OmegaConf.to_container(config)
            mlflow.log_dict(resolved_cfg, artifact_file='configs/config.yaml')
            mlflow.log_params(
                pd.json_normalize(resolved_cfg, sep = '.').to_dict(orient='records')[0]
            )

            mlflow.log_metrics({f'oof/{metric}' : val for metric, val in result.oof_metrics.items()})
            mlflow.log_metrics({f'cv_mean/{metric}' : val for metric, val in result.mean_metrics.items()})
            mlflow.log_metrics({f'cv_std/{metric}' : val for metric, val in result.std_metrics.items()})

            for i in range(len(result.fold_metrics)):
                mlflow.log_metrics({f'fold/{metric}' : val for metric, val in result.fold_metrics[i].items()}, step = i)
                mlflow.log_metrics({f'train/{metric}' : val for metric, val in result.train_metrics[i].items()}, step = i)