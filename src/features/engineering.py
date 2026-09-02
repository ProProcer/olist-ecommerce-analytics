import pandas as pd
from sklearn.preprocessing import FunctionTransformer

def dow(cols):
    cols = list(cols)
    transformer = FunctionTransformer(lambda x : x[cols].apply(lambda x : x.dt.dayofweek, axis = 0))
    return transformer

def is_equal(cols):
    cols = list(cols)

    def transform(x):
        return (
            x[cols]
            .eq(x[cols].iloc[:, 0], axis=0)
            .all(axis=1)
            .to_frame(name="")
        )

    return FunctionTransformer(transform)

def interaction_categorical(cols):
    cols = list(cols)

    def transform(x):
        x = x.astype(str)
        return x.sum(axis = 1).to_frame(name="")

    return FunctionTransformer(transform)

def dow_is_within_state_design(cols):
    cols = list(cols)
    ts_col, seller_col, customer_col = cols

    def transform(x):
        dow = x[ts_col].dt.dayofweek.astype(int)
        within = x[seller_col].eq(x[customer_col])

        out = {f'dow_{d}' : (dow == d).astype(int) for d in range(1, 7)}
        out['is_within_state'] = within.astype(int)
        for d in range(1, 7):
            out[f'dow_{d}_x_within'] = ((dow == d) & within).astype(int)

        return pd.DataFrame(out)

    return FunctionTransformer(transform)