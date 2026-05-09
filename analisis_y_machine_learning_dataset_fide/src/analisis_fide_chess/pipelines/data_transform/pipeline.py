"""
This is a boilerplate pipeline 'data_transform'
generated using Kedro 0.18.x
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import merge_and_transform

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=merge_and_transform,
                inputs=[
                    "fide_players_clean",
                    "fide_ratings_2019_clean",
                    "fide_ratings_2020_clean",
                    "fide_ratings_2021_clean"
                ],
                outputs="fide_preprocessed_data",
                name="merge_and_transform_data_node",
            )
        ]
    )
