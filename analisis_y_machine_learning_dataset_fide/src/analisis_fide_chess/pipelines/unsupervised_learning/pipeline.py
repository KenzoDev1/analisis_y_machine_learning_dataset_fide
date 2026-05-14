"""Pipeline de aprendizaje no supervisado (Ev2)."""
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import run_unsupervised


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=run_unsupervised,
                inputs=["fide_preprocessed_data", "params:clustering"],
                outputs=["unsupervised_model", "clustering_metrics"],
                name="run_unsupervised_node",
            ),
        ]
    )
