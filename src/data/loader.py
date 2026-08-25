import pandas as pd
from hydra.utils import instantiate, UNSAFE_ALLOW_ALL_TARGETS

def load_data(path, transforms):
    df = pd.read_csv(path)

    for fn in transforms:
        fn = instantiate(fn, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)
        df = df.pipe(fn)

    return df