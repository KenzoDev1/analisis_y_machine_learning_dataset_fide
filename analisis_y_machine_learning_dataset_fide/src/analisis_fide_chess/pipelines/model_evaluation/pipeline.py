"""Pipeline de evaluación de modelos (Ev2)."""
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import evaluate_model


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=evaluate_model,
                inputs=[
                    "supervised_model",
                    "X_train",
                    "X_test",
                    "y_train",
                    "y_test",
                ],
                outputs="evaluation_report",
                name="evaluate_model_node",
            ),
        ]
    )
