"""Nodos del pipeline de transformación de datos (AD 1.3).

Joins/merges de las 4 tablas, groupby, pivot_table, creación de features
derivadas, normalización y codificación de categóricas.

Columnas reales:
  players → fide_id, name, federation, gender, title, yob
  ratings → fide_id, year, month, rating_standard, rating_rapid, rating_blitz
"""
import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import MinMaxScaler, LabelEncoder

logger = logging.getLogger(__name__)


def merge_and_transform(
    players: pd.DataFrame,
    ratings_2019: pd.DataFrame,
    ratings_2020: pd.DataFrame,
    ratings_2021: pd.DataFrame,
    expert_threshold: int,
    base_year: int,
) -> pd.DataFrame:
    """Integra las 4 tablas y genera features derivadas para ML.

    Args:
        players: DataFrame limpio de jugadores.
        ratings_2019: DataFrame limpio de ratings 2019.
        ratings_2020: DataFrame limpio de ratings 2020.
        ratings_2021: DataFrame limpio de ratings 2021.
        expert_threshold: ELO mínimo para clasificar como "experto"
                          (parámetro inyectado desde parameters.yml).
        base_year: Año de referencia para calcular la edad aproximada
                   (parámetro inyectado desde parameters.yml).

    Pasos:
    1. Agregar ratings por jugador-año (groupby + media anual)
    2. Pivotar para tener una columna por año
    3. Merge con tabla de jugadores
    4. Feature engineering
    5. Normalización y codificación
    """
    # ---------------------------------------------------------------
    # 1. Concatenar los 3 años de ratings
    # ---------------------------------------------------------------
    all_ratings = pd.concat(
        [ratings_2019, ratings_2020, ratings_2021], ignore_index=True
    )
    logger.info(f"Ratings concatenados: {all_ratings.shape}")

    # ---------------------------------------------------------------
    # 2. GroupBy: rating promedio anual por jugador (AD 1.3)
    # ---------------------------------------------------------------
    annual_avg = (
        all_ratings.groupby(["fide_id", "year"])
        .agg(
            rating_std_mean=("rating_standard", "mean"),
            rating_rapid_mean=("rating_rapid", "mean"),
            rating_blitz_mean=("rating_blitz", "mean"),
            games_count=("month", "count"),  # meses con rating = proxy de actividad
        )
        .reset_index()
    )
    logger.info(f"Agregación anual: {annual_avg.shape}")

    # ---------------------------------------------------------------
    # 3. Pivot Table: una fila por jugador, columnas por año (AD 1.3)
    # ---------------------------------------------------------------
    pivot_std = annual_avg.pivot_table(
        index="fide_id",
        columns="year",
        values="rating_std_mean",
        aggfunc="mean",
    )
    pivot_std.columns = [f"rating_std_{int(y)}" for y in pivot_std.columns]
    pivot_std = pivot_std.reset_index()

    # Actividad total (meses con rating)
    activity = (
        annual_avg.groupby("fide_id")["games_count"]
        .sum()
        .reset_index()
        .rename(columns={"games_count": "total_months_active"})
    )

    # ---------------------------------------------------------------
    # 4. Merge con jugadores
    # ---------------------------------------------------------------
    df = players.merge(pivot_std, on="fide_id", how="inner")
    df = df.merge(activity, on="fide_id", how="left")
    logger.info(f"Merge players + ratings pivot: {df.shape}")

    # ---------------------------------------------------------------
    # 5. Feature Engineering — variables derivadas
    # ---------------------------------------------------------------
    rating_cols_present = [c for c in df.columns if c.startswith("rating_std_")]
    years_present = sorted([int(c.split("_")[-1]) for c in rating_cols_present])

    if len(years_present) >= 2:
        first_year = f"rating_std_{years_present[0]}"
        last_year = f"rating_std_{years_present[-1]}"
        df["rating_change"] = df[last_year] - df[first_year]
        df["rating_change_pct"] = (
            df["rating_change"] / df[first_year].replace(0, np.nan) * 100
        )

    # Promedio general de rating estándar
    if rating_cols_present:
        df["rating_std_avg"] = df[rating_cols_present].mean(axis=1)

    # Variable objetivo para clasificación: ¿es experto? (ELO > expert_threshold)
    if "rating_std_avg" in df.columns:
        df["is_expert"] = (df["rating_std_avg"] > expert_threshold).astype(int)
        logger.info(f"  Umbral experto (expert_threshold): {expert_threshold}")

    # Edad aproximada (respecto a base_year, parametrizado)
    if "yob" in df.columns:
        df["age_approx"] = base_year - df["yob"]
        logger.info(f"  Año base para edad (base_year): {base_year}")

    # ---------------------------------------------------------------
    # 6. Codificación de categóricas (AD 1.3)
    # ---------------------------------------------------------------
    le_gender = LabelEncoder()
    if "gender" in df.columns:
        df["gender_encoded"] = le_gender.fit_transform(df["gender"].fillna("U"))

    le_title = LabelEncoder()
    if "title" in df.columns:
        df["title_encoded"] = le_title.fit_transform(df["title"].fillna("NONE"))

    # ---------------------------------------------------------------
    # 7. Normalización de features numéricas (AD 1.3)
    # ---------------------------------------------------------------
    numeric_features = [
        c
        for c in df.select_dtypes(include=[np.number]).columns
        if c not in ("fide_id", "yob", "is_expert")
    ]
    if numeric_features:
        scaler = MinMaxScaler()
        df[[f"{c}_norm" for c in numeric_features]] = scaler.fit_transform(
            df[numeric_features].fillna(0)
        )

    # ---------------------------------------------------------------
    # 8. Limpieza final
    # ---------------------------------------------------------------
    # Eliminar filas sin rating promedio (jugadores sin partidas)
    if "rating_std_avg" in df.columns:
        df = df.dropna(subset=["rating_std_avg"])

    logger.info(f"Dataset transformado final: {df.shape}")
    logger.info(f"Columnas: {df.columns.tolist()}")
    return df
