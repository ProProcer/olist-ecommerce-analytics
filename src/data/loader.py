import pandas as pd
import numpy as np
from src.data.transforms import apply_transforms
from src.utils.hydra import instantiate_unsafe

def load_data(cfg):
    df = pd.read_csv(cfg.path)
    return apply_transforms(df, instantiate_unsafe(cfg.transforms))

def load_test_data(cfg_data, cfg_split):
    train_df = pd.read_csv(cfg_data.path)
    test_df = pd.read_csv(cfg_data.test_path)
    df = prepare_for_sliding_window_split(train_df, test_df, cfg_split.period_train, cfg_data.timestamp, cfg_split.freq)
    return apply_transforms(df, instantiate_unsafe(cfg_data.transforms))

def get_longest_contiguous_seq(a, descending = True):
    step = -1 if descending else 1
    a = a[np.argsort(a)[::step]]
    breaks = np.where(a[1:] != (a[:-1] + step))[0]
    idx = len(a) if len(breaks) == 0 else breaks[0][0]
    return a[: idx ]

def prepare_for_sliding_window_split(train_df, test_df, period_train, timestamp_col, freq):
    train_df[timestamp_col] = pd.to_datetime(train_df[timestamp_col])
    test_df[timestamp_col] = pd.to_datetime(test_df[timestamp_col])

    test_periods = test_df[timestamp_col].dt.to_period(freq).unique()
    test_periods = get_longest_contiguous_seq(test_periods, descending = False)
    
    train_periods = train_df[timestamp_col].dt.to_period(freq).unique()
    train_periods = train_periods[pd.Series(train_periods).between(min(test_periods) - period_train, min(test_periods) - 1)] # filter to period_train prior
    train_periods = get_longest_contiguous_seq(train_periods, descending = True)

    test_df = test_df[test_df[timestamp_col].dt.to_period(freq).isin(test_periods)]
    train_df = train_df[train_df[timestamp_col].dt.to_period(freq).isin(train_periods)] # filter to selected period

    df = pd.concat((train_df, test_df), ignore_index = True)
    
    return df