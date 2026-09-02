import hydra
from omegaconf import DictConfig, OmegaConf
from src.data.loader import load_data
from hydra.utils import instantiate, UNSAFE_ALLOW_ALL_TARGETS
from src.utils.resolvers import register_custom_resolvers
import pandas as pd
import numpy as np
from pathlib import Path

@hydra.main(config_path="../configs", config_name="config")
def main(cfg: DictConfig):
    register_custom_resolvers()

    df_train = load_data(cfg.data)
    test_data_cfg = OmegaConf.create(OmegaConf.to_container(cfg.data, resolve=True))
    test_data_cfg.path = cfg.data.test_path
    df_test = load_data(test_data_cfg)
    df = pd.concat((df_train, df_test), ignore_index = True)

    id_col = cfg.data.id_col
    if id_col not in df:
        raise KeyError(f"Configured ID column {id_col!r} is not present in the data.")
    
    validator = instantiate(cfg.validator, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)

    result = validator.run(df) 

    upper_bound = result.oof_predictions.upper_bound
    is_scored = ~np.isnan(upper_bound)
    export_df = df[[id_col, cfg.data.timestamp, cfg.data.target]].copy()
    export_df = export_df.rename(columns={cfg.data.target: "actual_value"})
    export_df["prediction_center"] = result.oof_predictions.center
    export_df["upper_bound"] = upper_bound
    export_df["is_oof_scored"] = is_scored
    export_df["is_anomaly"] = pd.Series(pd.NA, index=export_df.index, dtype="boolean")
    export_df.loc[is_scored, "is_anomaly"] = (
        export_df.loc[is_scored, "actual_value"]
        > export_df.loc[is_scored, "upper_bound"]
    )

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "processed" / f"oof_predictions_{cfg.data.target}.csv"
    export_df.to_csv(output_path, index=False)
    print(f"Exported {len(export_df):,} rows to {output_path}")

if __name__ == "__main__":
    main()
