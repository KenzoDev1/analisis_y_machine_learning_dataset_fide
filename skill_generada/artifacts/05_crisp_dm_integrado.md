# CRISP-DM Integrado con Kedro
> Fuente: Documentacion Teorica 1.txt + https://docs.kedro.org

---

## Las 6 Fases CRISP-DM en Kedro

CRISP-DM (Cross Industry Standard Process for Data Mining) es el estándar de la industria para proyectos de ciencia de datos. Kedro no impone metodología, pero su estructura de capas de datos y pipelines **encaja naturalmente** con las 6 fases CRISP-DM.

> ⚠️ CRISP-DM es **iterativo**: es normal volver a fases anteriores tras la evaluación.

---

## Fase 1 — Comprensión del Negocio (Business Understanding)

**Objetivo:** Formular el problema en términos medibles y acotar expectativas.

### Preguntas clave antes de tocar datos:
- ¿Es un problema de **clasificación**, **regresión** o **descripción/clustering**?
- ¿Cuál es la métrica de éxito del negocio (no del modelo)?
- ¿Qué decisión se apoyará en la predicción?
- ¿Qué error es más costoso: falsos positivos o falsos negativos?
- ¿El uso es ético y razonable?
- ¿Hay restricciones de latencia, interpretabilidad o regulación?

### En Kedro:
```yaml
# conf/base/parameters.yml — documenta decisiones de negocio
problema:
  tipo: "clasificacion"           # clasificacion | regresion | clustering
  descripcion: "Predecir X a partir de Y"
  metrica_negocio: "f1_macro"
  clase_positiva: "si"
  umbral_aceptacion: 0.70         # F1 mínimo aceptable

target_column: "resultado"
feature_columns:
  - "feature_A"
  - "feature_B"
```

---

## Fase 2 — Comprensión de los Datos (Data Understanding)

**Objetivo:** Conocer origen, granularidad, calidad, sesgos y limitaciones.

### Pipeline de exploración (data_understanding)

```python
# nodes.py
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def profile_dataset(data: pd.DataFrame) -> dict:
    """Genera un perfil estadístico del dataset."""
    profile = {
        "shape": {"rows": data.shape[0], "cols": data.shape[1]},
        "columns": list(data.columns),
        "dtypes": data.dtypes.astype(str).to_dict(),
        "missing_values": data.isnull().sum().to_dict(),
        "missing_pct": (data.isnull().mean() * 100).round(2).to_dict(),
        "duplicates": int(data.duplicated().sum()),
        "numeric_stats": data.describe().to_dict(),
        "cardinality": {col: data[col].nunique() for col in data.columns},
    }
    logger.info(f"Dataset: {profile['shape']['rows']} filas, {profile['shape']['cols']} cols")
    logger.info(f"Missing values totales: {data.isnull().sum().sum()}")
    logger.info(f"Duplicados: {profile['duplicates']}")
    return profile
```

### Catálogo para fase 2:
```yaml
# conf/base/catalog.yml
raw_data:
  type: pandas.CSVDataset
  filepath: data/01_raw/dataset.csv
  layer: raw

data_profile:
  type: json.JSONDataset
  filepath: data/08_reporting/data_profile.json
  layer: reporting
```

---

## Fase 3 — Preparación de los Datos (Data Preparation)

**Objetivo:** Construir un dataset analítico limpio con objetivo, predictores y particiones.

### Pipeline data_processing — patrón completo

```python
# nodes.py
def preprocess_data(
    data: pd.DataFrame,
    key_columns: list,
    date_columns: list,
) -> pd.DataFrame:
    """Limpia datos crudos."""
    # 1. Eliminar duplicados
    data = data.drop_duplicates()

    # 2. Parsear fechas
    for col in date_columns:
        if col in data.columns:
            data[col] = pd.to_datetime(data[col], errors="coerce")

    # 3. Eliminar filas con NaN en columnas clave
    data = data.dropna(subset=key_columns)

    return data.reset_index(drop=True)


def build_ml_features_table(
    data: pd.DataFrame,
    target_column: str,
    feature_columns: list,
    test_size: float,
    random_state: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Crea la tabla analítica y hace el split train/test."""
    from sklearn.model_selection import train_test_split

    # Seleccionar columnas disponibles
    available_features = [c for c in feature_columns if c in data.columns]
    df = data[available_features + [target_column]].dropna()

    X = df[available_features]
    y = df[target_column]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y if y.nunique() <= 20 else None,  # estratificar en clasificación
    )

    return X_train, X_test, y_train, y_test
```

### Debate de calidad de datos (preguntas clave):
- ¿Es adecuado un split aleatorio, o hay dependencia temporal (validación por tiempo)?
- ¿Hay fuga de información (data leakage)? ¿Algún predictor ocurre después del target?
- ¿El dataset está desbalanceado? ¿Aplicar SMOTE, pesos de clase o subsampling?
- ¿Las variables categóricas necesitan encoding especial (ordinal, target encoding)?

---

## Fase 4 — Modelado (Modeling)

**Objetivo:** Probar varias técnicas, entender supuestos y límites de cada familia.

### Pipeline de modelado genérico

```python
# nodes.py — clasificación multiclase
from sklearn.pipeline import Pipeline as SkPipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.svm import LinearSVC
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd

def train_classifiers(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    params: dict,
) -> dict:
    """Entrena múltiples clasificadores y los retorna en un dict."""
    models = {
        "logistic": SkPipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                C=params.get("logistic_C", 1.0),
                max_iter=params.get("max_iter", 500),
                random_state=42,
            )),
        ]),
        "linear_svc": SkPipeline([
            ("scaler", StandardScaler()),
            ("clf", LinearSVC(
                C=params.get("svc_C", 1.0),
                dual=False,
                random_state=42,
            )),
        ]),
        "knn": SkPipeline([
            ("scaler", StandardScaler()),
            ("clf", KNeighborsClassifier(
                n_neighbors=params.get("knn_k", 15),
                weights="distance",
            )),
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=params.get("rf_n_estimators", 200),
            max_depth=params.get("rf_max_depth", 10),
            min_samples_leaf=params.get("rf_min_leaf", 5),
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting": HistGradientBoostingClassifier(
            max_iter=params.get("hgb_max_iter", 200),
            learning_rate=params.get("hgb_lr", 0.05),
            max_depth=params.get("hgb_max_depth", 4),
            random_state=42,
        ),
    }

    for name, model in models.items():
        model.fit(X_train, y_train)

    return models
```

---

## Fase 5 — Evaluación (Evaluation)

**Objetivo:** Medir rendimiento con métricas alineadas al problema.

```python
# nodes.py — evaluación de clasificadores
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report,
    confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
)
import numpy as np
import json

def evaluate_classifiers(
    models: dict,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> tuple[dict, str]:
    """Evalúa todos los modelos en test y elige el mejor por F1 macro."""
    metrics = {}
    best_name, best_f1 = None, -1.0

    for name, model in models.items():
        y_pred = model.predict(X_test)
        f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        metrics[name] = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "f1_macro": float(f1),
            "f1_weighted": float(f1_score(y_test, y_pred, average="weighted")),
            "report": classification_report(y_test, y_pred, output_dict=True),
        }
        if f1 > best_f1:
            best_f1, best_name = f1, name

    metrics["best_model"] = best_name
    metrics["best_f1_macro"] = best_f1
    return metrics, best_name


def evaluate_regressors(
    models: dict,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict:
    """Evalúa modelos de regresión."""
    metrics = {}
    best_name, best_r2 = None, -np.inf

    for name, model in models.items():
        y_pred = model.predict(X_test)
        r2 = float(r2_score(y_test, y_pred))
        metrics[name] = {
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "r2": r2,
        }
        if r2 > best_r2:
            best_r2, best_name = r2, name

    metrics["best_model"] = best_name
    metrics["best_r2"] = best_r2
    return metrics
```

### Tabla de métricas de referencia

| Métrica | Tarea | Cuándo usarla |
|---------|-------|---------------|
| Accuracy | Clasificación | Clases balanceadas |
| F1 Macro | Clasificación | Clases desbalanceadas, igual peso por clase |
| F1 Weighted | Clasificación | Considera soporte de cada clase |
| Precision/Recall | Clasificación | Cuando importa FP vs FN diferencial |
| Confusion Matrix | Clasificación | Diagnóstico visual de errores |
| MAE | Regresión | Error en unidades originales |
| RMSE | Regresión | Penaliza errores grandes |
| R² | Regresión | Fracción de varianza explicada |

---

## Fase 6 — Despliegue (Deployment)

**Objetivo:** Pasar de experimento a algo reproducible, versionable y documentado.

### En Kedro esto significa:
1. `kedro run` — flujo reproducible end-to-end
2. Parámetros en YAML — sin hardcoding en el código
3. Artefactos en rutas estándar de `data/`
4. `.gitignore` correcto — no commitear datos ni credenciales
5. `requirements.txt` / `pyproject.toml` — dependencias fijadas
6. Tests con `pytest` — verificar el pipeline
7. `Docker Compose` — entorno reproducible en cualquier máquina

```bash
# Ciclo CRISP-DM completo con Kedro
kedro run                          # ejecuta todo el pipeline
kedro run --pipeline data_processing   # solo preparación
kedro run --pipeline ml_classification # solo modelado
pytest -q                          # verificar tests
make verify                        # format + lint + bootstrap + test + run
```
