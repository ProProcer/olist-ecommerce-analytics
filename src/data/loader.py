import pandas as pd

def load_data(path, timestamp, numerical_cols, categorical_cols):
    df = pd.read_csv(path)
    df = df[[timestamp] + numerical_cols + categorical_cols]
    df[timestamp] = pd.to_datetime(df[timestamp])
    df[numerical_cols] = df[numerical_cols].astype(pd.Float32Dtype)
    df[categorical_cols] = df[categorical_cols].astype(str).astype('category')
    return df