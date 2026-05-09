"""Nodos del pipeline de optimización de hiperparámetros (Ev2).

Implementa GridSearchCV y RandomizedSearchCV para encontrar
la mejor configuración del modelo.

- GridSearchCV       → modelos con espacio de búsqueda pequeño (LogisticRegression).
- RandomizedSearchCV → modelos con espacio de búsqueda grande (RandomForest, GradientBoosting).

Los modelos llegan envueltos en sklearn.pipeline.Pipeline (scaler + classifier),
por lo que todos los nombres de hiperparámetros usan el prefijo "classifier__".
Esto cumple con el requerimiento IEE 2.3.1 de la rúbrica.
"""
import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
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

    Estrategia de búsqueda (IEE 2.3.1):
      - GridSearchCV         → LogisticRegression (espacio pequeño, búsqueda exhaustiva).
      - RandomizedSearchCV   → RandomForest y GradientBoosting (espacio grande,
                                búsqueda estocástica más eficiente con n_iter).

    Los modelos se construyen como Pipelines (StandardScaler → classifier)
    para ser consistentes con el pipeline de entrenamiento (IEE 2.1.1).
    Por ello, los nombres de hiperparámetros llevan el prefijo "classifier__".

    Returns:
        Tuple[modelo_optimizado, reporte_dict]
    """
    logger.info("=" * 60)
    logger.info("OPTIMIZACIÓN DE HIPERPARÁMETROS")
    logger.info("=" * 60)

    # ----- Definir espacios de búsqueda -----
    # Los nombres de params usan el prefijo "classifier__" porque cada
    # modelo está envuelto en un Pipeline con el paso llamado "classifier".
    search_spaces = {
        "LogisticRegression": {
            "model": Pipeline([
                ("scaler", StandardScaler()),
                ("classifier", LogisticRegression(
                    max_iter=1000, random_state=RANDOM_STATE
                )),
            ]),
            "params": {
                "classifier__C": [0.01, 0.1, 1, 10, 100],
                "classifier__penalty": ["l1", "l2"],
                "classifier__solver": ["liblinear", "saga"],
            },
            # Espacio pequeño (5×2×2 = 20 combinaciones) → GridSearchCV
            "search": "grid",
        },
        "RandomForest": {
            "model": Pipeline([
                ("scaler", StandardScaler()),
                ("classifier", RandomForestClassifier(random_state=RANDOM_STATE)),
            ]),
            "params": {
                "classifier__n_estimators": [50, 100, 200],
                "classifier__max_depth": [5, 10, 20, None],
                "classifier__min_samples_split": [2, 5, 10],
                "classifier__min_samples_leaf": [1, 2, 4],
            },
            # Espacio grande (3×4×3×3 = 108 combinaciones) → RandomizedSearchCV
            "search": "random",
            "n_iter": 30,
        },
        "GradientBoosting": {
            "model": Pipeline([
                ("scaler", StandardScaler()),
                ("classifier", GradientBoostingClassifier(random_state=RANDOM_STATE)),
            ]),
            "params": {
                "classifier__n_estimators": [50, 100, 200],
                "classifier__max_depth": [3, 5, 7],
                "classifier__learning_rate": [0.01, 0.1, 0.2],
                "classifier__min_samples_split": [2, 5],
            },
            # Espacio grande (3×3×3×2 = 54 combinaciones) → RandomizedSearchCV
            "search": "random",
            "n_iter": 20,
        },
    }

    all_results = {}
    best_overall_model = None
    best_overall_score = -1
    best_overall_name = ""

    for name, config in search_spaces.items():
        search_type = config.get("search", "grid")

        if search_type == "random":
            # -----------------------------------------------------------
            # RandomizedSearchCV: muestreo estocástico del espacio de
            # búsqueda. Más eficiente para espacios grandes (IEE 2.3.1).
            # -----------------------------------------------------------
            logger.info(f"\n--- RandomizedSearchCV para {name} (n_iter={config['n_iter']}) ---")
            searcher = RandomizedSearchCV(
                estimator=config["model"],
                param_distributions=config["params"],
                n_iter=config["n_iter"],
                cv=5,
                scoring="f1",
                n_jobs=-1,
                verbose=0,
                random_state=RANDOM_STATE,
                return_train_score=True,
            )
        else:
            # -----------------------------------------------------------
            # GridSearchCV: búsqueda exhaustiva. Adecuado cuando el
            # espacio de hiperparámetros es reducido (IEE 2.3.1).
            # -----------------------------------------------------------
            logger.info(f"\n--- GridSearchCV para {name} ---")
            searcher = GridSearchCV(
                estimator=config["model"],
                param_grid=config["params"],
                cv=5,
                scoring="f1",
                n_jobs=-1,
                verbose=0,
                return_train_score=True,
            )

        searcher.fit(X_train, y_train)

        # Evaluar en test
        y_pred = searcher.predict(X_test)
        test_acc = accuracy_score(y_test, y_pred)
        test_f1 = f1_score(y_test, y_pred, zero_division=0)

        logger.info(f"  Método: {search_type.upper()}")
        logger.info(f"  Mejor Score CV: {searcher.best_score_:.4f}")
        logger.info(f"  Mejores Params: {searcher.best_params_}")
        logger.info(f"  Test Accuracy: {test_acc:.4f}, Test F1: {test_f1:.4f}")

        all_results[name] = {
            "search_method": search_type,
            "best_cv_score": round(float(searcher.best_score_), 4),
            "best_params": {k: str(v) for k, v in searcher.best_params_.items()},
            "test_accuracy": round(test_acc, 4),
            "test_f1": round(test_f1, 4),
        }

        if searcher.best_score_ > best_overall_score:
            best_overall_score = searcher.best_score_
            best_overall_model = searcher.best_estimator_
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
