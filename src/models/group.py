import numpy as np
import pandas as pd
import scipy.stats as ss
from src.schemas.predictions import AnomalyPredictions
from sklearn.base import BaseEstimator
from typing import Tuple

class GroupEstimator(BaseEstimator):
    def __init__(self, alpha):
        self.alpha = alpha

    def fit(self, X, y):
        X = np.asarray(X)
        y = pd.Series(y)

        indices = []
        upper_bounds = []
        centers = []
        for i, group in y.groupby(list(X.T)):
            indices.append(i)
            upper_bounds.append(self._get_bounds(group))
            centers.append(np.mean(group))

        self.preds = pd.DataFrame(
            {'upper_bound' : upper_bounds, 'center' : centers},
            index = indices
        )

    def _get_upper_bound(self, a : np.ndarray) -> Tuple[float]:
        raise NotImplementedError()

    def predict(self, X):
        X = np.array(X)
        
        preds = self.preds.loc[list(map(tuple, X))]

        return AnomalyPredictions(
            center = preds.center.to_numpy(),
            upper_bound = preds.upper_bound.to_numpy()
        )

class ZScore(GroupEstimator):
    def _get_bounds(self, a):
        params = ss.norm.fit(a)
        return ss.norm.ppf(1 - self.alpha, *params)

class TScore(GroupEstimator):
    def _get_bounds(self, a):
        params = ss.t.fit(a)
        return ss.t.ppf(1 - self.alpha, *params)

class EmpiricalQuantile(GroupEstimator):
    def _get_bounds(self, a):
        h = 1 + (len(a) - 1) * 0.95
        g = h - int(h)
        sorted_a = np.sort(a)
        return sorted_a[int(h)] + (sorted_a[int(h) + 1] - sorted_a[int(h)]) * g