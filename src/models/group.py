import numpy as np
import pandas as pd
import scipy.stats as ss
from src.schemas.predictions import AnomalyPredictions
from sklearn.base import BaseEstimator

class ZScore(BaseEstimator):
    def __init__(self, alpha = 0.05):
        self.alpha = alpha
    

    def fit(self, X, y):
        X = np.array(X)
        y = pd.Series(y)
        
        self.mean = y.groupby(list(X.T)).mean()
        self.std = y.groupby(list(X.T)).std()
        
    def predict(self, X) -> AnomalyPredictions:
        X = np.array(X)
        if X.shape[1] > 1:
            center = self.mean[list(map(tuple, X))]
        else: 
            center = self.mean[X[:, 0]]
        upper_bound = center + ss.norm.ppf(1 - self.alpha) * self.std

        preds = AnomalyPredictions(
            center = center.to_numpy(),
            upper_bound = upper_bound.to_numpy()
        )

        return preds