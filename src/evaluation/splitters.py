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
        expected_periods = pd.period_range(
            start=a.min(), periods=len(a), freq=a.freqstr
        )
        return a.equals(expected_periods)

    def split(self, X : pd.DataFrame, y = None, groups = None):
        sample_periods = X[self.timestamp].dt.to_period(self.freq)
        periods = pd.PeriodIndex(sample_periods.unique()).sort_values()

        if not self._is_contiguous(periods):
            raise ValueError(
                f"{self.timestamp!r} must contain contiguous {self.freq!r} periods."
            )

        idx_list = [np.where(sample_periods == period)[0] for period in periods]

        for i in range(self.get_n_splits(X, y, groups)):
            train_idx = np.concatenate(idx_list[i : i + self.period_train])
            test_idx = np.concatenate(idx_list[i + self.period_train : i + self.period_train + self.period_test])
            yield train_idx, test_idx

    def get_n_splits(self, X=None, y=None, groups=None):
        periods = pd.to_datetime(X[self.timestamp]).dt.to_period(self.freq).nunique()
        return max(0, periods - self.period_train - self.period_test + 1)
