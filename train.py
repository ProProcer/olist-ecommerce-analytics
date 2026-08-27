import hydra
from omegaconf import OmegaConf, DictConfig
from src.data.loader import load_data
from src.features import get_feature_transformer
from sklearn.pipeline import Pipeline
from hydra.utils import instantiate, UNSAFE_ALLOW_ALL_TARGETS
import numpy as np
from collections import defaultdict
from sklearn import metrics
from src.utils.resolvers import register_custom_resolvers
from src.evaluation.validator import CrossValidator

@hydra.main(config_path="configs", config_name="config")
def main(cfg: DictConfig):
    register_custom_resolvers()

    df = load_data(
        cfg.data, 
    )
    
    validator = instantiate(cfg.validator, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)

    results = validator.run(df) 
    print(results)

if __name__ == "__main__":
    main()