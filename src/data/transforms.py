import pandas as pd
from typing import List, Callable

def apply_transforms(df, transforms: List[Callable]):
    df = df.copy()
    for fn in transforms:
        df = df.pipe(fn)
    return df

def parse_datetime(df: pd.DataFrame, cols : List[str]) -> pd.DataFrame:
    for col in cols:
        df[col] = pd.to_datetime(df[col])
    return df

def cast_dtypes(df : pd.DataFrame, cols : List[str], dtype : str) -> pd.DataFrame:
    cols = list(cols)
    df[cols] = df[cols].astype(dtype)
    return df

def select_columns(df : pd.DataFrame, cols : List[str]) -> pd.DataFrame:
    return df[cols]

if __name__ == '__main__':
    df = pd.DataFrame({
        'date1' : ['2018-01-01', '2018-01-02'],
        'date2' : ['2019-01-01', '2019-01-02']
    })
    print(parse_datetime(df, ['date1', 'date2']))