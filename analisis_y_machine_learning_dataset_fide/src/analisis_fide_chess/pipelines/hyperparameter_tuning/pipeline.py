"""Pipeline de optimización de hiperparámetros (Ev2)."""
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import optimize_hyperparameters


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=optimize_hyperparameters,
                inputs=["X_train", "y_train", "X_test", "y_test", "params:tuning"],
                outputs=["optimized_model", "optimization_report"],
                name="optimize_hyperparameters_node",
            ),
        ]
    )
