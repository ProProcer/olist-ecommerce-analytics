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


def aggregate_metrics(results):
    return  {
        'outlier_frac' : np.average(results['outlier_frac'], weights = results['N']).item(),
        'rmse_outlier_frac' : np.sqrt(((results['outlier_frac'] - 0.05)**2).mean()).item(),
        'weighted_rmse_outlier_frac' : np.sqrt(np.average((results['outlier_frac'] - 0.05)**2, weights = results['N'])).item(),
        'rmse_center' : np.sqrt(np.average(results['rmse_center'] ** 2, weights = results['N'])).item()
    }

@hydra.main(config_path="configs", config_name="config")
def main(cfg: DictConfig):
    register_custom_resolvers()

    df = load_data(
        path = cfg.data.path, 
        transforms = cfg.transforms
    )
    
    feature_transformer = instantiate(cfg.features, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)
    
    model = instantiate(cfg.model, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)
    splitter = instantiate(cfg.split, _target_whitelist_ = UNSAFE_ALLOW_ALL_TARGETS)
    results = defaultdict(list)
    for train_idx, test_idx in splitter.split(df):
        train_df = df.loc[train_idx]
        X_train = feature_transformer.fit_transform(train_df)
        y_train = train_df[cfg.data.target]

        test_df = df.loc[test_idx]
        X_test = feature_transformer.transform(test_df)
        y_test = test_df[cfg.data.target]

        model.fit(X_train, y_train)
        preds = model.predict(X_test, y_test)
        results['outlier_frac'].append(preds['is_outlier'].mean().item())
        results['rmse_center'].append(metrics.root_mean_squared_error(y_test, preds['center']))
        results['N'].append(len(y_test))
        
    for k in results.keys():
        results[k] = np.array(results[k])
    
    print(aggregate_metrics(results))

if __name__ == "__main__":
    main()