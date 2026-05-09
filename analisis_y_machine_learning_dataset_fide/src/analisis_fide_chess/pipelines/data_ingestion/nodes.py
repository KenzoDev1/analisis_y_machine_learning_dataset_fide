"""Nodos del pipeline de ingesta de datos (AD 1.1).

Carga los CSVs crudos, estandariza columnas y genera un reporte
de diagnóstico inicial con forma, tipos, head(), describe() e info().
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def preprocess_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza nombres de columnas a snake_case y loguea perfil inicial."""
    logger.info("=" * 60)
    logger.info(f"Ingestando dataset — dimensiones: {df.shape}")
    logger.info(f"Columnas originales: {df.columns.tolist()}")

    # Estandarizar columnas a snake_case
    df.columns = [col.lower().strip().replace(" ", "_") for col in df.columns]

    # Profiling inicial por columna
    logger.info("Tipos de datos:")
    for col in df.columns:
        n_null = df[col].isnull().sum()
        pct = n_null / len(df) * 100
        logger.info(f"  {col:25s} | {str(df[col].dtype):10s} | nulos: {n_null} ({pct:.1f}%)")

    logger.info(f"Duplicados totales: {df.duplicated().sum()}")
    logger.info("=" * 60)
    return df


def build_ingestion_report(
    players: pd.DataFrame,
    ratings_2019: pd.DataFrame,
    ratings_2020: pd.DataFrame,
    ratings_2021: pd.DataFrame,
) -> dict:
    """Genera un reporte JSON con el diagnóstico inicial de los 4 datasets.

    Incluye forma, columnas, tipos, nulos y duplicados para cada tabla.
    """

    def _profile(name: str, df: pd.DataFrame) -> dict:
        return {
            "dataset": name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": df.isnull().sum().to_dict(),
            "missing_pct": (df.isnull().mean() * 100).round(2).to_dict(),
            "duplicates": int(df.duplicated().sum()),
            "describe": df.describe(include="all").to_dict(),
        }

    report = {
        "players": _profile("players", players),
        "ratings_2019": _profile("ratings_2019", ratings_2019),
        "ratings_2020": _profile("ratings_2020", ratings_2020),
        "ratings_2021": _profile("ratings_2021", ratings_2021),
    }

    logger.info("Reporte de diagnóstico generado con éxito.")
    return report
