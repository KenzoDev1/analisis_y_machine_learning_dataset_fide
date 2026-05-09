"""Nodos del pipeline de optimización de hiperparámetros (Ev2).

Implementa GridSearchCV y RandomizedSearchCV para encontrar
la mejor configuración del modelo.
"""
import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score

logger = logging.getLogger(__name__)

RANDOM_STATE = 42


def optimize_hyperparameters(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple:
    """Optimiza hiperparámetros de múltiples modelos.

    Usa GridSearchCV con validación cruzada 5-fold.

    Returns:
        Tuple[modelo_optimizado, reporte_dict]
    """
    logger.info("=" * 60)
    logger.info("OPTIMIZACIÓN DE HIPERPARÁMETROS")
    logger.info("=" * 60)

    # ----- Definir grids de búsqueda -----
    search_spaces = {
        "RandomForest": {
            "model": RandomForestClassifier(random_state=RANDOM_STATE),
            "params": {
                "n_estimators": [50, 100, 200],
                "max_depth": [5, 10, 20, None],
                "min_samples_split": [2, 5, 10],
                "min_samples_leaf": [1, 2, 4],
            },
        },
        "GradientBoosting": {
            "model": GradientBoostingClassifier(random_state=RANDOM_STATE),
            "params": {
                "n_estimators": [50, 100, 200],
                "max_depth": [3, 5, 7],
                "learning_rate": [0.01, 0.1, 0.2],
                "min_samples_split": [2, 5],
            },
        },
        "LogisticRegression": {
            "model": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            "params": {
                "C": [0.01, 0.1, 1, 10, 100],
                "penalty": ["l1", "l2"],
                "solver": ["liblinear", "saga"],
            },
        },
    }

    all_results = {}
    best_overall_model = None
    best_overall_score = -1
    best_overall_name = ""

    for name, config in search_spaces.items():
        logger.info(f"\n--- GridSearchCV para {name} ---")

        grid = GridSearchCV(
            estimator=config["model"],
            param_grid=config["params"],
            cv=5,
            scoring="f1",
            n_jobs=-1,
            verbose=0,
            return_train_score=True,
        )

        grid.fit(X_train, y_train)

        # Evaluar en test
        y_pred = grid.predict(X_test)
        test_acc = accuracy_score(y_test, y_pred)
        test_f1 = f1_score(y_test, y_pred, zero_division=0)

        logger.info(f"  Mejor Score CV: {grid.best_score_:.4f}")
        logger.info(f"  Mejores Params: {grid.best_params_}")
        logger.info(f"  Test Accuracy: {test_acc:.4f}, Test F1: {test_f1:.4f}")

        all_results[name] = {
            "best_cv_score": round(float(grid.best_score_), 4),
            "best_params": {k: str(v) for k, v in grid.best_params_.items()},
            "test_accuracy": round(test_acc, 4),
            "test_f1": round(test_f1, 4),
        }

        if grid.best_score_ > best_overall_score:
            best_overall_score = grid.best_score_
            best_overall_model = grid.best_estimator_
            best_overall_name = name

    # ----- Reporte -----
    report = {
        "best_model": best_overall_name,
        "best_cv_score": round(float(best_overall_score), 4),
        "all_results": all_results,
    }

    logger.info(f"\n{'='*60}")
    logger.info(f"MEJOR MODELO OPTIMIZADO: {best_overall_name} (F1 CV: {best_overall_score:.4f})")
    logger.info(f"{'='*60}")

    return best_overall_model, report
