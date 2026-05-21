"""Pipeline de generación del informe HTML técnico de modelos (Ev2)."""
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import generate_html_report


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=generate_html_report,
                inputs=[
                    "evaluation_report",
                    "optimization_report",
                    "clustering_metrics",
                    "params:model_options",
                    "params:split",
                    "params:tuning",
                    "params:clustering",
                    "params:evaluation",
                ],
                outputs="model_report_html",
                name="generate_html_report_node",
            ),
        ]
    )
