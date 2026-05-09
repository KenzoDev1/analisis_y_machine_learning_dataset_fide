# Modelos ML — Clasificación, Regresión y Clustering en Kedro
> Fuente: Documentacion Teorica 2 + Documentacion Teorica 1.txt

---

## Pipeline de Clasificación Completo

### nodes.py — ml_classification

```python
import logging
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline as SkPipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import f1_score, accuracy_score, classification_report
from sklearn.inspection import permutation_importance

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────
# ENTRENAMIENTO
# ──────────────────────────────────────────────────────────────────

def train_classifiers(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    parameters: dict,
) -> dict:
    """Entrena todos los clasificadores definidos en parameters.yml."""
    p = parameters.get("classifier_params", {})

    models = {
        "logistic_regression": SkPipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                C=p.get("logistic", {}).get("C", 1.0),
                max_iter=p.get("logistic", {}).get("max_iter", 500),
                random_state=42,
            )),
        ]),
        "linear_svc": SkPipeline([
            ("scaler", StandardScaler()),
            ("clf", LinearSVC(
                C=p.get("svc", {}).get("C", 1.0),
                dual=False,
                random_state=42,
            )),
        ]),
        "knn": SkPipeline([
            ("scaler", StandardScaler()),
            ("clf", KNeighborsClassifier(
                n_neighbors=p.get("knn", {}).get("n_neighbors", 15),
                weights="distance",
            )),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=p.get("rf", {}).get("n_estimators", 200),
            max_depth=p.get("rf", {}).get("max_depth", 10),
            min_samples_leaf=p.get("rf", {}).get("min_samples_leaf", 5),
            random_state=42, n_jobs=-1,
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=p.get("hgb", {}).get("max_iter", 200),
            learning_rate=p.get("hgb", {}).get("learning_rate", 0.05),
            max_depth=p.get("hgb", {}).get("max_depth", 4),
            random_state=42,
        ),
    }

    for name, model in models.items():
        model.fit(X_train, y_train)
        logger.info(f"Modelo entrenado: {name}")

    return models


# ──────────────────────────────────────────────────────────────────
# EVALUACIÓN
# ──────────────────────────────────────────────────────────────────

def evaluate_classifiers(
    models: dict,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple[dict, object]:
    """Evalúa modelos, crea leaderboard y devuelve el mejor."""
    results = {}
    best_name, best_f1 = None, -1.0

    for name, model in models.items():
        y_pred = model.predict(X_test)
        f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
        results[name] = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "f1_macro": f1,
            "f1_weighted": float(f1_score(y_test, y_pred, average="weighted")),
            "report": classification_report(y_test, y_pred, output_dict=True),
        }
        logger.info(f"{name:30s} → F1 macro={f1:.4f}")
        if f1 > best_f1:
            best_f1, best_name = f1, name

    results["_meta"] = {"best_model": best_name, "best_f1_macro": best_f1}
    logger.info(f"Mejor modelo: {best_name} (F1 macro={best_f1:.4f})")

    return results, models[best_name]


# ──────────────────────────────────────────────────────────────────
# IMPORTANCIA DE VARIABLES
# ──────────────────────────────────────────────────────────────────

def compute_feature_importance(
    best_model: object,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    n_repeats: int = 10,
) -> pd.DataFrame:
    """Calcula importancia por permutación para el mejor modelo."""
    result = permutation_importance(
        best_model, X_test, y_test,
        n_repeats=n_repeats,
        random_state=42,
        scoring="f1_macro",
        n_jobs=-1,
    )

    importance_df = pd.DataFrame({
        "feature": X_test.columns,
        "importance_mean": result.importances_mean,
        "importance_std": result.importances_std,
    }).sort_values("importance_mean", ascending=False)

    return importance_df
```

---

## Pipeline de Regresión Completo

### nodes.py — ml_regression

```python
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train_regressors(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    parameters: dict,
) -> dict:
    """Entrena múltiples modelos de regresión."""
    p = parameters.get("regressor_params", {})

    models = {
        "ridge": SkPipeline([
            ("scaler", StandardScaler()),
            ("reg", Ridge(alpha=p.get("ridge", {}).get("alpha", 1.0))),
        ]),
        "random_forest": RandomForestRegressor(
            n_estimators=p.get("rf", {}).get("n_estimators", 100),
            max_depth=p.get("rf", {}).get("max_depth", 8),
            random_state=42, n_jobs=-1,
        ),
        "hist_gradient_boosting": HistGradientBoostingRegressor(
            max_iter=p.get("hgb", {}).get("max_iter", 200),
            learning_rate=p.get("hgb", {}).get("learning_rate", 0.05),
            random_state=42,
        ),
    }

    for name, model in models.items():
        model.fit(X_train, y_train)

    return models


def evaluate_regressors(
    models: dict,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple[dict, object]:
    """Evalúa modelos de regresión y devuelve métricas + mejor modelo."""
    results = {}
    best_name, best_r2 = None, -np.inf

    for name, model in models.items():
        y_pred = model.predict(X_test)
        r2 = float(r2_score(y_test, y_pred))
        results[name] = {
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "r2": r2,
        }
        logger.info(f"{name:30s} → R²={r2:.4f}")
        if r2 > best_r2:
            best_r2, best_name = r2, name

    results["_meta"] = {"best_model": best_name, "best_r2": best_r2}
    return results, models[best_name]
```

---

## Clustering (No Supervisado)

```python
# nodes.py — clustering
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def apply_clustering(
    data: pd.DataFrame,
    feature_columns: list,
    n_clusters: int,
    pca_components: int,
    random_state: int,
) -> tuple[pd.DataFrame, dict]:
    """Aplica PCA + K-Means y evalúa con silhouette score."""
    X = data[feature_columns].dropna()

    # Escalado
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Reducción dimensional
    pca = PCA(n_components=pca_components, random_state=random_state)
    X_pca = pca.fit_transform(X_scaled)

    # Clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")
    labels = kmeans.fit_predict(X_pca)

    # Métricas
    sil_score = float(silhouette_score(X_pca, labels))
    inertia = float(kmeans.inertia_)

    # Resultados
    result_df = data.copy()
    result_df["cluster"] = labels

    metrics = {
        "n_clusters": n_clusters,
        "silhouette_score": sil_score,
        "inertia": inertia,
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "total_explained_variance": float(pca.explained_variance_ratio_.sum()),
        "cluster_sizes": pd.Series(labels).value_counts().to_dict(),
    }

    logger.info(f"Silhouette Score: {sil_score:.4f} | Inercia: {inertia:.2f}")
    return result_df, metrics
```

---

## Explicabilidad de Modelos

### Importancia por Permutación (cualquier modelo)

```python
from sklearn.inspection import permutation_importance

def permutation_feature_importance(model, X_test, y_test, scoring="f1_macro"):
    result = permutation_importance(
        model, X_test, y_test,
        n_repeats=10, random_state=42, scoring=scoring
    )
    return pd.DataFrame({
        "feature": X_test.columns,
        "mean": result.importances_mean,
        "std": result.importances_std,
    }).sort_values("mean", ascending=False)
```

### SHAP (modelos de árbol — opcional)

```python
# Requiere: pip install shap
import shap

def compute_shap_values(model, X_train, X_test):
    """SHAP para modelos basados en árboles (RandomForest, GBM)."""
    # Extraer el estimador del SkPipeline si aplica
    estimator = model["clf"] if hasattr(model, "__getitem__") else model

    explainer = shap.TreeExplainer(estimator)
    shap_values = explainer.shap_values(X_test)

    return shap_values, explainer
```

---

## Validación Cruzada (Notebooks — no en Kedro run)

```python
# notebook 07 — StratifiedKFold para clasificación
from sklearn.model_selection import StratifiedKFold, cross_validate, GridSearchCV

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# cross_validate muestra inestabilidad del split
scores = cross_validate(
    model, X, y, cv=cv,
    scoring=["f1_macro", "accuracy"],
    return_train_score=True,
)

# GridSearchCV para búsqueda de hiperparámetros
param_grid = {"clf__C": [0.01, 0.1, 1.0, 10.0]}
grid = GridSearchCV(model, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1)
grid.fit(X_train, y_train)
print(f"Mejor C: {grid.best_params_}")
```

---

## Guía de Cuándo Usar Cada Modelo

| Modelo | Cuándo usarlo | Requiere escalado | Interpretable |
|--------|--------------|-------------------|---------------|
| Regresión Logística | Baseline interpretable, frontera lineal | ✅ Sí | ✅ Coeficientes |
| LinearSVC | Igual que logística, diferente manejo de outliers | ✅ Sí | Parcial |
| k-NN | Datasets pequeños, relaciones locales | ✅ Sí | ❌ No |
| Random Forest | Baseline no lineal, importancia nativa | ❌ No | Parcial (importancia) |
| HistGradientBoosting | Mayor rendimiento en tablas, datos faltantes | ❌ No | Con SHAP |
| Ridge | Regresión con features correlacionadas | ✅ Sí | ✅ Coeficientes |
| K-Means | Segmentación, exploración, sin etiquetas | ✅ Sí | Con interpretación manual |

---

## FAQ para Oral / Revisión de Código

**¿Por qué escalar antes de logística, SVM y k-NN?**
Usan distancias o penalizaciones sensibles a la magnitud. Sin escalado, una variable con rango 0-1000 domina sobre una de 0-1.

**¿Por qué Random Forest no necesita escalado?**
Los árboles ordenan por umbrales en cada variable; un escalado monotónico por columna no cambia los splits óptimos.

**¿El mejor modelo en test es el mejor en producción?**
No necesariamente: hay varianza del split, posible fuga temporal (si mezclamos períodos), y deriva del conjunto de datos con el tiempo.

**¿Por qué kedro run no usa GridSearch ni CV?**
Para mantener el pipeline corto y didáctico. GridSearch y CV van en notebook 07. Kedro es el "cierre CRISP-DM"; el notebook es el "laboratorio".

**¿Qué es metodología vs código?**
Metodología = decisiones documentadas (qué columnas, qué split, por qué ese modelo). Código = implementación que las respeta. Kedro ayuda a no perder las decisiones entre notebooks y entregas.
