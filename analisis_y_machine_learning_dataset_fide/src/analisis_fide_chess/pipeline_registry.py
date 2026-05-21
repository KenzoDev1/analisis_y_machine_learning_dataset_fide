"""Registro de pipelines para Evaluación 1 y 2 - FIDE Chess.
"""

from __future__ import annotations

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

_DEFAULT_PIPELINE_ORDER = (
    # Evaluación 1: Calidad y Transformación de Datos
    "data_ingestion",
    "data_cleaning",
    "data_transform",
    "data_validation",
    # Evaluación 2: Machine Learning
    "model_training",
    "model_evaluation",
    "hyperparameter_tuning",
    "unsupervised_learning",
    # Informe HTML técnico (se genera al final)
    "model_report",
)

def register_pipelines() -> dict[str, Pipeline]:
    """Devuelve todos los pipelines del paquete y define ``__default__`` como la suma ordenada.

    Returns:
        Diccionario nombre → ``Pipeline``.
    """
    pipelines = find_pipelines(raise_errors=True)
    modular = {k: v for k, v in pipelines.items() if k != "__default__"}
    ordered = [modular[name] for name in _DEFAULT_PIPELINE_ORDER if name in modular]
    if ordered:
        pipelines["__default__"] = sum(ordered)
    else:
        pipelines["__default__"] = Pipeline([])
    return pipelines
