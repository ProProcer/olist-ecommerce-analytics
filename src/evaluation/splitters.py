import pandas as pd
import numpy as np

class SlidingWindowSplitter:
    def __init__(self, period_train, period_test, timestamp, freq = 'M'):
        self.period_train = period_train
        self.period_test = period_test
        self.timestamp = timestamp
        self.freq = freq

    def _is_contiguous_(self, periods):
        return periods.isin(min(periods) + np.arange(0, len(periods))).all()

    def _prepare_data_(self, test_df : pd.DataFrame, train_df : pd.DataFrame = None):
        
        test_periods = test_df[self.timestamp].dt.to_period(self.freq).unique()
        assert self._is_contiguous_(test_periods)

        if train_df is not None:

            train_periods = train_df[self.timestamp].dt.to_period(self.freq).unique()
            train_periods = train_periods[pd.Series(train_periods).between(min(test_periods) - self.period_train, min(test_periods) - 1)] # filter to period_train prior
            train_periods = self._longest_contiguous_seq_(train_periods, descending = True)
            train_df = train_df[train_df[self.timestamp].dt.to_period(self.freq).isin(train_periods)] # filter to selected period

        df = pd.concat((train_df, test_df))
        
        return df

    def _longest_contiguous_seq_(self, a, descending = True):
        step = -1 if descending else 1
        a = a[np.argsort(a)[::step]]
        breaks = np.where(a[1:] != (a[:-1] + step))[0]
        idx = len(a) if len(breaks) == 0 else breaks[0][0]
        return a[: idx ]

    def split(self, test_df : pd.DataFrame, train_df : pd.DataFrame = None):
        df = self._prepare_data_(test_df, train_df)
        periods = df[self.timestamp].dt.to_period(self.freq).unique()
        periods = periods[periods.argsort()]

        idx_list = [np.where(df[self.timestamp].dt.to_period(self.freq) == p)[0] for p in periods]

        N = len(idx_list) - self.period_train - self.period_test + 1
        for i in range(N):
            train_idx = np.concatenate(idx_list[i : i + self.period_train])
            test_idx = np.concatenate(idx_list[i + self.period_train : i + self.period_train + self.period_test])
            yield train_idx, test_idx        
