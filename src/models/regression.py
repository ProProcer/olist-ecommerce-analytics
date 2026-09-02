from sklearn.linear_model import LinearRegression as LinearRegression_
from sklearn.base import BaseEstimator
import numpy as np
from scipy import stats
from src.schemas.predictions import AnomalyPredictions

class LinearRegression(BaseEstimator):
    def __init__(self, alpha):
        self.alpha = alpha

    def fit(self, X, y):
        model = LinearRegression_()
        model.fit(X, y)

        n, p = X.shape
        dof = n - p - 1
        residuals = y - model.predict(X)
        s = np.sqrt(np.sum(residuals**2) / dof)
        self.X_mean_ = np.mean(X, axis=0)
        X_centered = np.asarray(X - self.X_mean_)

        self.XTX_inv = np.linalg.pinv(X_centered.T @ X_centered)
        self.model = model
        self.s = s
        self.n = n
        self.dof = dof

    def predict(self, X):
        model = self.model
        XTX_inv = self.XTX_inv
        s = self.s
        n = self.n
        dof = self.dof

        center = np.asarray(model.predict(X))

        X_centered = np.asarray(X - self.X_mean_)
        leverage = np.sum((X_centered @ self.XTX_inv) * X_centered, axis=1)
        prediction_se = s * np.sqrt(1 + (1 / n) + leverage)
        t_val = stats.t.ppf(1 - self.alpha, dof)

        upper_bound = center + t_val * prediction_se

        return AnomalyPredictions(
            center = center,
            upper_bound = upper_bound
        )



