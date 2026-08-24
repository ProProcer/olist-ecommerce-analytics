from sklearn.compose import ColumnTransformer 
from sklearn.pipeline import Pipeline

def get_feature_transformer(**kwargs):
    group_transformer_list = []
    for group_name, group in kwargs.items():
        transformers = [(name, trans, slice(None)) for name, trans in group.items() if name != 'passthrough']
        
        group_transformer = ColumnTransformer(
            transformers,
            verbose_feature_names_out= True
        )
        if 'passthrough' in group:
            passthrough_cols = list(group.get('passthrough'))
            group_transformer = ColumnTransformer(
                [
                    (group_name, group_transformer, slice(None)), 
                    ('passthrough', 'passthrough', passthrough_cols)
                ],
                verbose_feature_names_out= False
            )
        
        
        group_transformer_list.append((group_name, group_transformer))

    return Pipeline(group_transformer_list).set_output(transform = 'pandas')