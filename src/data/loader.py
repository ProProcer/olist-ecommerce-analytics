import pandas as pd
from hydra.utils import instantiate, UNSAFE_ALLOW_ALL_TARGETS

def load_data(cfg):
    df = pd.read_csv(cfg.path)

    for fn in cfg.transforms:
        fn = instantiate(fn, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)
        df = df.pipe(fn)

    return df