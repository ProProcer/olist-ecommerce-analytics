from src.schemas.predictions import AnomalyPredictions
import numpy as np
from sklearn import metrics

def outlier_fraction(y_true : np.ndarray, preds : AnomalyPredictions) -> float:
    return preds.is_outlier.mean().item()

def rmse(y_true : np.ndarray, preds : AnomalyPredictions) -> float:
    return metrics.root_mean_squared_error(y_true, preds.center)