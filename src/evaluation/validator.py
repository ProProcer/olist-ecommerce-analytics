from src.evaluation.metrics import outlier_fraction
from sklearn.base import clone
from src.schemas.evaluation import ValidationResult
from dataclasses import asdict, fields
import numpy as np
from collections import defaultdict

def create_empty_buffer(shape: int, dtype) -> np.ndarray:
    """Pre-allocates an OOF buffer matching the dtype and sentinel."""

    if np.issubdtype(dtype, np.floating):
        return np.full(shape, np.nan, dtype=dtype)
    elif np.issubdtype(dtype, np.integer):
        return np.full(shape, -1, dtype=dtype)
    elif np.issubdtype(dtype, np.bool_):
        # Convert bool to int8 sentinel so -1 represents unvisited
        return np.full(shape, -1, dtype=np.int8)
    else:
        return np.full(shape, None, dtype=object)

class CrossValidator:
    def __init__(
            self, 
            model, 
            splitter, 
            feature_transformer, 
            target_col, 
            evaluator
        ):
        self.model = model
        self.splitter = splitter
        self.feature_transformer = feature_transformer
        self.target_col = target_col
        self.evaluator = evaluator

    def run(self, df):
        n_samples = len(df) 

        pred_class = None

        train_metrics = []
        fold_metrics = []
        oof_preds_buffer = {}
        fitted_models = []
        evaluated_idx = []
        
        for train_idx, test_idx in self.splitter.split(df):
            train_df = df.loc[train_idx]
            X_train = self.feature_transformer.fit_transform(train_df)
            y_train = train_df[self.target_col]
    
            test_df = df.loc[test_idx]
            X_test = self.feature_transformer.transform(test_df)
            y_test = test_df[self.target_col]

            fold_model = clone(self.model)
            fold_model.fit(X_train, y_train)

            train_preds = fold_model.predict(X_train)
            test_preds = fold_model.predict(X_test)

            train_metrics.append(self.evaluator.compute(y_train, train_preds))
            fold_metrics.append(self.evaluator.compute(y_test, test_preds))
            if not oof_preds_buffer:
                pred_class = type(test_preds)
                for f in fields(test_preds):
                    dtype = getattr(test_preds, f.name).dtype
                    oof_preds_buffer[f.name] = create_empty_buffer(n_samples, dtype)

            for f in fields(test_preds):
                oof_preds_buffer[f.name][test_idx] = getattr(test_preds, f.name)
            fitted_models.append(fold_model)
            evaluated_idx.extend(test_idx)

        filtered_preds_buffer = {
            k : oof_preds_buffer[k][np.unique(evaluated_idx)] for k in oof_preds_buffer
        }
        y = df[self.target_col]

        oof_metrics = self.evaluator.compute(y[np.unique(evaluated_idx)], pred_class(**filtered_preds_buffer))

        oof_predictions = pred_class(**oof_preds_buffer)
        
        mean_metrics = defaultdict(list)
        std_metrics = defaultdict(list)
        for k in fold_metrics[0].keys():
            mean_metrics[k].append(np.mean([val[k] for val in fold_metrics]))
            std_metrics[k].append(np.std([val[k] for val in fold_metrics]))
            
        return ValidationResult(
            oof_metrics = oof_metrics,
            fold_metrics = fold_metrics,
            mean_metrics = mean_metrics,
            std_metrics = std_metrics,
            train_metrics = train_metrics,
            oof_predictions = oof_predictions,
            fitted_models = fitted_models
        )