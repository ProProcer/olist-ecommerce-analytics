from src.evaluation.metrics import outlier_fraction

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
        for train_idx, test_idx in self.splitter.split(df):
            train_df = df.loc[train_idx]
            X_train = self.feature_transformer.fit_transform(train_df)
            y_train = train_df[self.target_col]
    
            test_df = df.loc[test_idx]
            X_test = self.feature_transformer.transform(test_df)
            y_test = test_df[self.target_col]
    
            self.model.fit(X_train, y_train)
            preds = self.model.predict(X_test, y_test)
            print(self.evaluator.compute(y_test, preds))
        return None