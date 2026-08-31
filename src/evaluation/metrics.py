from src.schemas.predictions import AnomalyPredictions
import numpy as np
from sklearn import metrics

def outlier_fraction(y_true : np.ndarray, preds : AnomalyPredictions) -> float:
    return (preds.upper_bound < y_true).mean().item()

def rmse(y_true : np.ndarray, preds : AnomalyPredictions) -> float:
    return metrics.root_mean_squared_error(y_true, preds.center)

def medae(y_true : np.ndarray, preds : AnomalyPredictions) -> float:
    return metrics.median_absolute_error(y_true, preds.center)