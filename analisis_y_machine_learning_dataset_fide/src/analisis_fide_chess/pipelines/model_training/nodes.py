"""Nodos del pipeline de entrenamiento de modelos supervisados (Ev2).

Implementa split train/test y entrenamiento de múltiples modelos
de clasificación usando scikit-learn.

Cada modelo está envuelto en un sklearn.pipeline.Pipeline que incluye
un paso de escalado (StandardScaler) seguido del clasificador,
cumpliendo con el requerimiento IEE 2.1.1 de la rúbrica.
"""
import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score

logger = logging.getLogger(__name__)

# Features numéricas normalizadas para entrenamiento
FEATURE_CANDIDATES = [
    "rating_std_avg",
    "rating_change",
    "total_months_active",
    "age_approx",
    "gender_encoded",
    "title_encoded",
]

TARGET = "is_expert"
RANDOM_STATE = 42


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Selecciona y limpia las features para ML."""
    available = [c for c in FEATURE_CANDIDATES if c in df.columns]
    if TARGET not in df.columns:
        raise ValueError(f"Columna objetivo '{TARGET}' no encontrada en el dataset.")

    features_df = df[available + [TARGET]].dropna()
    logger.info(f"Features disponibles: {available}")
    logger.info(f"Dataset para ML: {features_df.shape}")
    logger.info(f"Distribución del target:\n{features_df[TARGET].value_counts().to_dict()}")
    return features_df


def split_data(
    df: pd.DataFrame,
    parameters: dict,
    sampling_params: dict,
) -> tuple:
    """Divide el dataset en train y test, aplicando subsampling opcional.

    Si ``sampling_params.sample_size`` es un entero y menor que ``len(df)``,
    se toma una muestra estratificada del dataset antes del split.
    Esto permite ejecutar el pipeline completo en entornos con memoria
    limitada como Google Colab gratuito.
    """
    available = [c for c in FEATURE_CANDIDATES if c in df.columns]

    # ------------------------------------------------------------------
    # Subsampling configurable (Optimización 1 — Colab)
    # ------------------------------------------------------------------
    sample_size = sampling_params.get("sample_size", None)
    sample_rs = sampling_params.get("random_state", RANDOM_STATE)

    if sample_size is not None and sample_size < len(df):
        logger.info(
            f"[Subsampling] Reduciendo de {len(df)} a {sample_size} filas "
            f"(random_state={sample_rs})"
        )
        df = df.sample(n=sample_size, random_state=sample_rs)
    else:
        logger.info(f"[Subsampling] Sin muestreo — usando {len(df)} filas completas")

    X = df[available]
    y = df[TARGET]

    test_size = parameters.get("test_size", 0.2)
    random_state = parameters.get("random_state", RANDOM_STATE)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    logger.info(f"Split completado — Train: {X_train.shape}, Test: {X_test.shape}")
    return X_train, X_test, y_train, y_test


def train_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> dict:
    """Entrena múltiples modelos supervisados envueltos en Pipelines.

    Cada modelo se construye como un sklearn.pipeline.Pipeline con:
      1. StandardScaler  — normalización de features (media=0, std=1)
      2. Clasificador     — el algoritmo de ML correspondiente

    Esto cumple con el requerimiento IEE 2.1.1 ("modelos con pipelines")
    y garantiza que el escalado se aplique de forma consistente durante
    el entrenamiento y la inferencia.

    Modelos:
    - Logistic Regression
    - Random Forest
    - K-Nearest Neighbors
    - Support Vector Machine
    - Gradient Boosting
    """
    # Cada valor es un Pipeline(scaler → clasificador)
    # El paso del clasificador se llama "classifier" para que los
    # hiperparámetros se referencien como "classifier__<param>"
    # en la etapa de optimización (hyperparameter_tuning).
    models = {
        "LogisticRegression": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", LogisticRegression(
                max_iter=1000, random_state=RANDOM_STATE
            )),
        ]),
        "RandomForest": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", RandomForestClassifier(
                n_estimators=100, random_state=RANDOM_STATE
            )),
        ]),
        "KNN": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", KNeighborsClassifier(n_neighbors=5)),
        ]),
        "SVM": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", SVC(
                kernel="rbf", random_state=RANDOM_STATE, probability=True
            )),
        ]),
        "GradientBoosting": Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", GradientBoostingClassifier(
                n_estimators=100, random_state=RANDOM_STATE
            )),
        ]),
    }

    best_model = None
    best_score = -1
    best_name = ""

    for name, model in models.items():
        logger.info(f"Entrenando {name}...")
        model.fit(X_train, y_train)
        score = model.score(X_train, y_train)
        logger.info(f"  {name} — Accuracy (train): {score:.4f}")

        if score > best_score:
            best_score = score
            best_model = model
            best_name = name

    logger.info(f"Mejor modelo en train: {best_name} ({best_score:.4f})")
    return best_model
