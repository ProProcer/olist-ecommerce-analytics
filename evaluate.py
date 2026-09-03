import hydra
from omegaconf import DictConfig
from src.data.loader import load_test_data
from src.utils.hydra import instantiate_unsafe
from src.utils.resolvers import register_custom_resolvers

@hydra.main(config_path="configs", config_name="config")
def main(cfg: DictConfig):
    register_custom_resolvers()

    df = load_test_data(cfg.data, cfg.split)

    validator = instantiate_unsafe(cfg.validator)

    result = validator.run(df) 

    tracker = instantiate_unsafe(cfg.tracker)
    tracker.log_run(
        run_name = cfg.run_name + "_test", 
        config = cfg, 
        result = result
    )

if __name__ == "__main__":
    main()