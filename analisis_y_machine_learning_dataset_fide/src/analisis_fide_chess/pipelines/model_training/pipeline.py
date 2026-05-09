"""Pipeline de entrenamiento de modelos supervisados (Ev2)."""
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import prepare_features, split_data, train_models


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=prepare_features,
                inputs="fide_preprocessed_data",
                outputs="fide_features",
                name="prepare_features_node",
            ),
            node(
                func=split_data,
                inputs=["fide_features", "params:split"],
                outputs=["X_train", "X_test", "y_train", "y_test"],
                name="split_data_node",
            ),
            node(
                func=train_models,
                inputs=["X_train", "y_train"],
                outputs="supervised_model",
                name="train_models_node",
            ),
        ]
    )
