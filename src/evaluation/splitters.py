import pandas as pd
import numpy as np
from sklearn.model_selection import BaseCrossValidator

def get_longest_contiguous_seq(a, descending = True):
    step = -1 if descending else 1
    a = a[np.argsort(a)[::step]]
    breaks = np.where(a[1:] != (a[:-1] + step))[0]
    idx = len(a) if len(breaks) == 0 else breaks[0][0]
    return a[: idx ]

def prepare_for_sliding_window_split(train_df, test_df, period_train, timestamp_col, freq):
    test_periods = test_df[timestamp_col].dt.to_period(freq).unique()
    test_periods = get_longest_contiguous_seq(test_periods, descending = False)
    
    train_periods = train_df[timestamp_col].dt.to_period(freq).unique()
    train_periods = train_periods[pd.Series(train_periods).between(min(test_periods) - period_train, min(test_periods) - 1)] # filter to period_train prior
    train_periods = get_longest_contiguous_seq(train_periods, descending = True)

    test_df = test_df[test_df[timestamp_col].dt.to_period(freq).isin(test_periods)]
    train_df = train_df[train_df[timestamp_col].dt.to_period(freq).isin(train_periods)] # filter to selected period

    df = pd.concat((train_df, test_df))
    
    return df
    
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
