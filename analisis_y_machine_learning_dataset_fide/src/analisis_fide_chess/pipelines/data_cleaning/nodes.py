"""Nodos del pipeline de limpieza de datos (AD 1.2).

Manejo de nulos, eliminación de duplicados, corrección de tipos,
estandarización de strings y tratamiento de outliers con IQR.

Columnas reales:
  players → fide_id, name, federation, gender, title, yob
  ratings → fide_id, year, month, rating_standard, rating_rapid, rating_blitz
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

RATING_COLS = ["rating_standard", "rating_rapid", "rating_blitz"]


def clean_players(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia el dataset de jugadores FIDE."""
    logger.info(f"[clean_players] Inicio — filas: {len(df)}")

    # 1. Eliminar duplicados
    n_dup = df.duplicated().sum()
    df = df.drop_duplicates()
    logger.info(f"  Duplicados eliminados: {n_dup}")

    # 2. Eliminar filas sin fide_id (clave primaria)
    df = df.dropna(subset=["fide_id"])
    df["fide_id"] = df["fide_id"].astype(int)

    # 3. Estandarizar strings
    if "name" in df.columns:
        df["name"] = df["name"].str.strip()
    if "federation" in df.columns:
        df["federation"] = df["federation"].str.strip().str.upper()
    if "gender" in df.columns:
        df["gender"] = df["gender"].str.strip().str.upper()

    # 4. Manejo de título nulo → "None" (sin título FIDE)
    if "title" in df.columns:
        df["title"] = df["title"].fillna("None").str.strip().str.upper()

    # 5. Año de nacimiento: convertir a numérico, eliminar imposibles
    if "yob" in df.columns:
        df["yob"] = pd.to_numeric(df["yob"], errors="coerce")
        # Rango razonable: nacidos entre 1900 y 2015
        df = df[(df["yob"].isna()) | ((df["yob"] >= 1900) & (df["yob"] <= 2015))]

    logger.info(f"[clean_players] Fin — filas: {len(df)}")
    return df


def clean_ratings(df: pd.DataFrame) -> pd.DataFrame:
    """Limpia un dataset de ratings FIDE (aplica a cada año por separado)."""
    logger.info(f"[clean_ratings] Inicio — filas: {len(df)}")

    # 1. Eliminar duplicados
    n_dup = df.duplicated().sum()
    df = df.drop_duplicates()
    logger.info(f"  Duplicados eliminados: {n_dup}")

    # 2. fide_id no puede ser nulo
    df = df.dropna(subset=["fide_id"])
    df["fide_id"] = df["fide_id"].astype(int)

    # 3. Convertir columnas de rating a numérico
    for col in RATING_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 4. Necesitamos al menos rating_standard válido
    if "rating_standard" in df.columns:
        df = df.dropna(subset=["rating_standard"])
        df = df[df["rating_standard"] > 0]

    # 5. Tratamiento de outliers con IQR en rating_standard
    if "rating_standard" in df.columns:
        q1 = df["rating_standard"].quantile(0.25)
        q3 = df["rating_standard"].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        before = len(df)
        df = df[(df["rating_standard"] >= lower) & (df["rating_standard"] <= upper)]
        logger.info(
            f"  Outliers IQR rating_standard: eliminados {before - len(df)} "
            f"(rango válido: {lower:.0f}-{upper:.0f})"
        )

    # 6. year y month a entero
    for col in ["year", "month"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    logger.info(f"[clean_ratings] Fin — filas: {len(df)}")
    return df
