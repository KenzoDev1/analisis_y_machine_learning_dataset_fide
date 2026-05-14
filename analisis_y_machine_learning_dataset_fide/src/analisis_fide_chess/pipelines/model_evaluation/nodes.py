"""Nodos del pipeline de evaluación de modelos (Ev2).

Validación cruzada, métricas múltiples y comparación entre modelos.
"""
import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

logger = logging.getLogger(__name__)

RANDOM_STATE = 42


def evaluate_model(
    model,
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    eval_params: dict,
) -> dict:
    """Evalúa el modelo principal y compara con otros usando validación cruzada.

    Genera un reporte completo con:
    - Métricas en test (Accuracy, Precision, Recall, F1, ROC-AUC)
    - Validación cruzada (cv configurable) para cada modelo
    - Comparación entre modelos
    - Matriz de confusión

    El número de folds se lee desde ``eval_params`` (Optimización 3 — Colab).
    """
    # ------------------------------------------------------------------
    # Leer cv parametrizado (Optimización 3 — Colab)
    # ------------------------------------------------------------------
    cv = eval_params.get("cv", 3)
    logger.info(f"Evaluación con cv={cv}")

    # ----- 1. Evaluar modelo principal en test -----
    y_pred = model.predict(X_test)
    y_proba = (
        model.predict_proba(X_test)[:, 1]
        if hasattr(model, "predict_proba")
        else None
    )

    main_metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
    }
    if y_proba is not None:
        main_metrics["roc_auc"] = round(roc_auc_score(y_test, y_proba), 4)

    cm = confusion_matrix(y_test, y_pred).tolist()
    report_text = classification_report(y_test, y_pred, zero_division=0)
    logger.info(f"Classification Report:\n{report_text}")

    # ----- 2. Validación cruzada del modelo principal -----
    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    cv_results = cross_validate(
        model, X_train, y_train, cv=cv, scoring=scoring, return_train_score=False
    )
    cv_summary = {}
    for metric in scoring:
        key = f"test_{metric}"
        if key in cv_results:
            scores = cv_results[key]
            cv_summary[metric] = {
                "mean": round(float(np.mean(scores)), 4),
                "std": round(float(np.std(scores)), 4),
                "scores": [round(float(s), 4) for s in scores],
            }

    # ----- 3. Comparar con todos los modelos -----
    all_models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "SVM": SVC(kernel="rbf", random_state=RANDOM_STATE, probability=True),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=RANDOM_STATE),
    }

    comparison = {}
    for name, m in all_models.items():
        logger.info(f"Evaluando {name} con cross-validation (cv={cv})...")
        cv_acc = cross_val_score(m, X_train, y_train, cv=cv, scoring="accuracy")
        cv_f1 = cross_val_score(m, X_train, y_train, cv=cv, scoring="f1")
        comparison[name] = {
            "cv_accuracy_mean": round(float(np.mean(cv_acc)), 4),
            "cv_accuracy_std": round(float(np.std(cv_acc)), 4),
            "cv_f1_mean": round(float(np.mean(cv_f1)), 4),
            "cv_f1_std": round(float(np.std(cv_f1)), 4),
        }
        logger.info(f"  {name} — CV Accuracy: {np.mean(cv_acc):.4f} ± {np.std(cv_acc):.4f}")

    # ----- Construir reporte -----
    report = {
        "best_model": type(model).__name__,
        "test_metrics": main_metrics,
        "confusion_matrix": cm,
        "cross_validation": cv_summary,
        "model_comparison": comparison,
    }

    logger.info(f"Evaluación completada. Mejor modelo: {type(model).__name__}")
    return report
