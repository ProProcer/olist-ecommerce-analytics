from typing import Dict, Any, Callable
from omegaconf import DictConfig
from hydra.utils import instantiate
from src.schemas.predictions import AnomalyPredictions
import numpy as np

class MetricEvaluator():
    def __init__(
            self, 
            primary_metric : str, 
            greater_is_better : bool, 
            metrics : Dict[str, Any]
        ):
        self.primary_metric = primary_metric
        self.greater_is_better = greater_is_better
        self.metrics : Dict[str, Callable] = {}

        for name, target in metrics.items():
            if isinstance(target, (dict, DictConfig)): 
                self.metrics[name]  = instantiate(target)
            else: 
                self.metrics[name] = target

        assert primary_metric in self.metrics

    def compute(
            self,
            y_true : np.ndarray, 
            preds : AnomalyPredictions
        ):
        results : Dict[str, float] = {}

        for name, metric_fn in self.metrics.items():
            results[name] = metric_fn(y_true, preds)

        return results