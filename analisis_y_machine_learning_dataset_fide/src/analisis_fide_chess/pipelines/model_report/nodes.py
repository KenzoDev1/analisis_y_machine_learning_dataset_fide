"""Nodos del pipeline de generación del informe HTML técnico (Ev2).

Consume los reportes JSON generados por los pipelines de evaluación,
optimización y clustering, y genera un HTML auto-contenido con diseño
premium alineado a la rúbrica de la Evaluación Parcial 2.
"""
import logging
from datetime import datetime

from .html_template import (
    CSS,
    build_header,
    build_resumen,
    build_marco,
    build_supervised,
    build_cv,
    build_optimization,
    build_unsupervised,
    build_conclusiones,
    build_referencias,
    build_footer,
)

logger = logging.getLogger(__name__)


def generate_html_report(
    evaluation_report: dict,
    optimization_report: dict,
    clustering_metrics: dict,
    model_options: dict,
    split_params: dict,
    tuning_params: dict,
    clustering_params: dict,
    eval_params: dict,
) -> str:
    """Genera el informe HTML técnico completo.

    Args:
        evaluation_report: Métricas de evaluación supervisada y cross-validation.
        optimization_report: Resultados de GridSearchCV / RandomizedSearchCV.
        clustering_metrics: Métricas de K-Means, PCA y método del codo.
        model_options: Features y target (desde parameters.yml).
        split_params: Configuración del split train/test.
        tuning_params: Grillas de hiperparámetros.
        clustering_params: Parámetros de clustering.
        eval_params: Configuración de evaluación (cv).

    Returns:
        String con el documento HTML completo.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Generando informe HTML técnico — {timestamp}")

    sections = [
        build_header(timestamp),
        build_resumen(model_options, split_params),
        build_marco(tuning_params, eval_params, clustering_params),
        build_supervised(evaluation_report),
        build_cv(evaluation_report),
        build_optimization(optimization_report, tuning_params),
        build_unsupervised(clustering_metrics),
        build_conclusiones(evaluation_report, optimization_report, clustering_metrics),
        build_referencias(),
        build_footer(),
    ]

    body = "\n".join(sections)

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="es">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<meta name="description" content="Informe técnico de modelos ML — '
        'Dataset FIDE Chess — Evaluación Parcial 2 SCY1101">\n'
        '<title>Informe Técnico ML — FIDE Chess</title>\n'
        f'<style>{CSS}</style>\n'
        '</head>\n<body>\n'
        f'<div class="container">\n{body}\n</div>\n'
        '</body>\n</html>'
    )

    logger.info(f"Informe HTML generado — {len(html):,} caracteres")
    return html
