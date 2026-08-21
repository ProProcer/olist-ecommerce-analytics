import hydra
from omegaconf import OmegaConf, DictConfig
from src.data.loader import load_data
from hydra.utils import instantiate

@hydra.main(config_path="configs", config_name="config")
def main(cfg: DictConfig):
    print(cfg)
    df = load_data(
        path = cfg.data.path, 
        timestamp = cfg.data.timestamp, 
        numerical_cols = list(cfg.data.numerical_cols), 
        categorical_cols = list(cfg.data.categorical_cols)
    )
    print(df)

if __name__ == "__main__":
    main()