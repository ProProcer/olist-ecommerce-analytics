import hydra
from omegaconf import DictConfig
from src.data.loader import load_data
from hydra.utils import instantiate, UNSAFE_ALLOW_ALL_TARGETS
from src.utils.resolvers import register_custom_resolvers
import pandas as pd
import numpy as np

@hydra.main(config_path="../configs", config_name="config")
def main(cfg: DictConfig):
    register_custom_resolvers()

    df_train = load_data(cfg.data)
    cfg.data.path = cfg.data.test_path
    df_test = load_data(cfg.data)
    df = pd.concat((df_train, df_test), ignore_index = True)
    
    validator = instantiate(cfg.validator, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)

    result = validator.run(df) 

    oof_pred = (result.oof_predictions.upper_bound < df[cfg.data.target]).astype(np.float32)
    oof_pred[np.isnan(result.oof_predictions.upper_bound)] = pd.NA
    oof_pred.index = df['order_id']
    oof_pred.to_csv(f'data/processed/oof_predictions_{cfg.data.target}.csv')

if __name__ == "__main__":
    main()