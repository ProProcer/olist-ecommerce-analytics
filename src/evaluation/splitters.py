import pandas as pd
import numpy as np
from sklearn.model_selection import BaseCrossValidator

class SlidingWindowSplitter(BaseCrossValidator):
    def __init__(self, period_train, period_test, timestamp, freq = 'M'):
        self.period_train = period_train
        self.period_test = period_test
        self.timestamp = timestamp
        self.freq = freq

    def _is_contiguous(self, a):
        return a.isin(min(a) + np.arange(0, len(a))).all()

    def split(self, X : pd.DataFrame, y = None, groups = None):
        periods = X[self.timestamp].dt.to_period(self.freq).unique()
        self._is_contiguous(periods)

        idx_list = [np.where(X[self.timestamp].dt.to_period(self.freq) == p)[0] for p in periods]

        for i in range(self.get_n_splits(X, y, groups)):
            train_idx = np.concatenate(idx_list[i : i + self.period_train])
            test_idx = np.concatenate(idx_list[i + self.period_train : i + self.period_train + self.period_test])
            yield train_idx, test_idx

    def get_n_splits(self, X=None, y=None, groups=None):
        periods = pd.to_datetime(X[self.timestamp]).dt.to_period(self.freq).nunique()
        return max(0, periods - self.period_train - self.period_test + 1)
