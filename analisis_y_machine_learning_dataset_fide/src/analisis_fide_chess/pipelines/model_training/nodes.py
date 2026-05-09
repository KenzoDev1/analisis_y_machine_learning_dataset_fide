"""Nodos del pipeline de entrenamiento de modelos supervisados (Ev2).

Implementa split train/test y entrenamiento de múltiples modelos
de clasificación usando scikit-learn.
"""
import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split
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
) -> tuple:
    """Divide el dataset en train y test."""
    available = [c for c in FEATURE_CANDIDATES if c in df.columns]

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
    """Entrena múltiples modelos supervisados y retorna el mejor.

    Modelos:
    - Logistic Regression
    - Random Forest
    - K-Nearest Neighbors
    - Support Vector Machine
    - Gradient Boosting
    """
    models = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, random_state=RANDOM_STATE
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100, random_state=RANDOM_STATE
        ),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "SVM": SVC(kernel="rbf", random_state=RANDOM_STATE, probability=True),
        "GradientBoosting": GradientBoostingClassifier(
            n_estimators=100, random_state=RANDOM_STATE
        ),
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
