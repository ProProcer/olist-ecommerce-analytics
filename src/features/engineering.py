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
            .to_frame(name="is_within_state")
        )

    return FunctionTransformer(transform)
    