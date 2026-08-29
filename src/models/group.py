import numpy as np
import pandas as pd
import scipy.stats as ss
from src.schemas.predictions import AnomalyPredictions
from sklearn.base import BaseEstimator
from typing import Tuple

class GroupEstimator(BaseEstimator):
    def __init__(self, alpha, min_group_size = 10):
        self.alpha = alpha
        self.min_group_size = min_group_size

    def fit(self, X, y):
        X = np.asarray(X)
        y = pd.Series(y)

        indices = []
        upper_bounds = []
        centers = []
        for i, group in y.groupby(list(X.T)):
            if len(group) < self.min_group_size:
                continue
            indices.append(i)
            upper_bounds.append(self._get_upper_bound(group))
            centers.append(np.mean(group))

        self.preds_ = pd.DataFrame(
            {'upper_bound' : upper_bounds, 'center' : centers},
            index = indices
        )
        self.global_center_ = np.mean(y)
        self.global_upper_bound_ = self._get_upper_bound(group)

    def _get_upper_bound(self, a : np.ndarray) -> float:
        raise NotImplementedError()

    def predict(self, X):
        X = np.array(X)
        
        preds = self.preds_.reindex(list(map(tuple, X)))

        preds['center'] = preds['center'].fillna(self.global_center_)
        preds['upper_bound'] = preds['upper_bound'].fillna(self.global_upper_bound_)

        return AnomalyPredictions(
            center = preds.center.to_numpy(),
            upper_bound = preds.upper_bound.to_numpy()
        )

class ZScore(GroupEstimator):
    def _get_upper_bound(self, a):
        params = ss.norm.fit(a)
        return ss.norm.ppf(1 - self.alpha, *params)

class TScore(GroupEstimator):
    def _get_upper_bound(self, a):
        params = ss.t.fit(a)
        return ss.t.ppf(1 - self.alpha, *params)

class EmpiricalQuantile(GroupEstimator):
    def _get_upper_bound(self, a):
        h = 1 + (len(a) - 1) * 0.95
        g = h - int(h)
        sorted_a = np.sort(a)
        return sorted_a[int(h)] + (sorted_a[int(h) + 1] - sorted_a[int(h)]) * g