from sklearn.preprocessing import FunctionTransformer

def dow(cols):
    cols = list(cols)
    transformer = FunctionTransformer(lambda x : x[cols].apply(lambda x : x.dt.dayofweek, axis = 0))
    return transformer