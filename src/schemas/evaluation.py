from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np
from sklearn.base import BaseEstimator

@dataclass
class ValidationResult:
    oof_metrics : Dict[str, float]
    fold_metrics : List[Dict[str, float]]
    mean_metrics : Dict[str, float]
    std_metrics : Dict[str, float]
    train_metrics : List[Dict[str, float]]
    oof_predictions : Dict[str, np.ndarray]
    fitted_models : List[BaseEstimator]