"""Pipeline de ingesta de datos (AD 1.1).

Carga los 4 CSVs, estandariza columnas y produce un reporte de diagnóstico.
"""
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import preprocess_columns, build_ingestion_report


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            # --- Estandarizar columnas de cada dataset ---
            node(
                func=preprocess_columns,
                inputs="fide_players",
                outputs="fide_players_raw",
                name="ingest_players_node",
            ),
            node(
                func=preprocess_columns,
                inputs="fide_ratings_2019",
                outputs="fide_ratings_2019_raw",
                name="ingest_ratings_2019_node",
            ),
            node(
                func=preprocess_columns,
                inputs="fide_ratings_2020",
                outputs="fide_ratings_2020_raw",
                name="ingest_ratings_2020_node",
            ),
            node(
                func=preprocess_columns,
                inputs="fide_ratings_2021",
                outputs="fide_ratings_2021_raw",
                name="ingest_ratings_2021_node",
            ),
            # --- Reporte de diagnóstico inicial ---
            node(
                func=build_ingestion_report,
                inputs=[
                    "fide_players_raw",
                    "fide_ratings_2019_raw",
                    "fide_ratings_2020_raw",
                    "fide_ratings_2021_raw",
                ],
                outputs="ingestion_report",
                name="build_ingestion_report_node",
            ),
        ]
    )
