import hydra
from omegaconf import DictConfig
from src.data.loader import load_data
from hydra.utils import instantiate, UNSAFE_ALLOW_ALL_TARGETS
from src.utils.resolvers import register_custom_resolvers

@hydra.main(config_path="configs", config_name="config")
def main(cfg: DictConfig):
    register_custom_resolvers()

    df = load_data(cfg.data)
    
    validator = instantiate(cfg.validator, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)

    result = validator.run(df) 

    tracker = instantiate(cfg.tracker, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)
    tracker.log_run(
        run_name = cfg.run_name, 
        config = cfg, 
        result = result
    )

if __name__ == "__main__":
    main()