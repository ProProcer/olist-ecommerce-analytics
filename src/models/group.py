import numpy as np
import pandas as pd
import scipy.stats as ss
from src.schemas.predictions import AnomalyPredictions
from sklearn.base import BaseEstimator

class ZScore(BaseEstimator):
    def __init__(self, alpha):
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

class TScore(BaseEstimator):
    def __init__(self, alpha):
        self.alpha = alpha

    def fit(self, X, y):
        X = np.asarray(X)
        y = pd.Series(y)

        keys = []
        upper_bounds = []
        centers = []
        for key, ser in y.groupby(list(X.T)):
            keys.append(key)
            t_params = ss.t.fit(ser)
            upper_bounds.append(ss.t.ppf(1 - self.alpha, *t_params))
            centers.append(np.mean(ser))

        self.preds = pd.DataFrame(
            {'upper_bound' : upper_bounds, 'center' : centers},
            index = keys
        )
        
    def predict(self, X):
        X = np.array(X)
        
        preds = self.preds.loc[list(map(tuple, X))]

        return AnomalyPredictions(
            center = preds.center.to_numpy(),
            upper_bound = preds.upper_bound.to_numpy()
        )