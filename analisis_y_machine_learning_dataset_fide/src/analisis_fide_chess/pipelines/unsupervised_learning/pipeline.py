"""Pipeline de aprendizaje no supervisado (Ev2)."""
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import run_unsupervised


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=run_unsupervised,
                inputs=["fide_preprocessed_data", "params:clustering"],
                outputs=["clustering_metrics", "unsupervised_model", "fide_clustered_data"],
                name="run_unsupervised_node",
            ),
        ]
    )
