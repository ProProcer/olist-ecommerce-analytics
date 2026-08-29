from dataclasses import fields, is_dataclass, replace
from typing import Callable, Optional
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, clone

class TransformedTargetEstimator(BaseEstimator):
    def __init__(
        self,
        model: BaseEstimator,
        transformer: Optional[BaseEstimator] = None,
        func: Optional[Callable] = None,
        inverse_func: Optional[Callable] = None,
    ):
        self.model = model
        self.transformer = transformer
        self.func = func
        self.inverse_func = inverse_func

    def _transform_y(self, y):
        if self.transformer_ is not None:
            y_arr = np.asarray(y)
            # Reshape 1D -> 2D for scikit-learn transformers if needed
            if y_arr.ndim == 1:
                return self.transformer_.fit_transform(y_arr.reshape(-1, 1)).ravel()
            return self.transformer_.fit_transform(y_arr)
        elif self.func is not None:
            return self.func(y)
        return y

    def _inverse_transform_array(self, arr: np.ndarray) -> np.ndarray:
        if arr is None:
            return None
        arr_np = np.asarray(arr)
        if self.transformer_ is not None:
            if arr_np.ndim == 1:
                return self.transformer_.inverse_transform(arr_np.reshape(-1, 1)).ravel()
            return self.transformer_.inverse_transform(arr_np)
        elif self.inverse_func is not None:
            return self.inverse_func(arr_np)
        return arr_np

    def fit(self, X, y):
        # Clone internal estimators to avoid state mutation
        self.model_ = clone(self.model)
        self.transformer_ = clone(self.transformer) if self.transformer is not None else None

        # 1. Transform y
        y_trans = self._transform_y(y)
        
        # Keep as Series/DataFrame index if original was pandas
        if isinstance(y, (pd.Series, pd.DataFrame)):
            y_trans = pd.Series(y_trans, index=y.index)

        # 2. Fit underlying model
        self.model_.fit(X, y_trans)
        return self

    def predict(self, X):
        raw_preds = self.model_.predict(X)

        # Handle Dataclass predictions (e.g. AnomalyPredictions)
        if is_dataclass(raw_preds):
            inverted_fields = {}
            for f in fields(raw_preds):
                val = getattr(raw_preds, f.name)
                if isinstance(val, np.ndarray):
                    inverted_fields[f.name] = self._inverse_transform_array(val)
                else:
                    inverted_fields[f.name] = val
            return type(raw_preds)(**inverted_fields)

        # Handle standard array output
        return self._inverse_transform_array(raw_preds)