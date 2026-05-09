"""
This is a boilerplate pipeline 'data_validation'
generated using Kedro 0.18.x
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import validate_data

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=validate_data,
                inputs="fide_preprocessed_data",
                outputs="validation_report",
                name="validate_data_node",
            )
        ]
    )
