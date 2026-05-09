"""
This is a boilerplate pipeline 'data_cleaning'
generated using Kedro 0.18.x
"""

from kedro.pipeline import Pipeline, node, pipeline
from .nodes import clean_players, clean_ratings

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=clean_players,
                inputs=[
                    "fide_players_raw",
                    "params:cleaning.min_yob",
                    "params:cleaning.max_yob",
                ],
                outputs="fide_players_clean",
                name="clean_players_node",
            ),
            node(
                func=clean_ratings,
                inputs=[
                    "fide_ratings_2019_raw",
                    "params:cleaning.iqr_factor",
                ],
                outputs="fide_ratings_2019_clean",
                name="clean_ratings_2019_node",
            ),
            node(
                func=clean_ratings,
                inputs=[
                    "fide_ratings_2020_raw",
                    "params:cleaning.iqr_factor",
                ],
                outputs="fide_ratings_2020_clean",
                name="clean_ratings_2020_node",
            ),
            node(
                func=clean_ratings,
                inputs=[
                    "fide_ratings_2021_raw",
                    "params:cleaning.iqr_factor",
                ],
                outputs="fide_ratings_2021_clean",
                name="clean_ratings_2021_node",
            ),
        ]
    )
