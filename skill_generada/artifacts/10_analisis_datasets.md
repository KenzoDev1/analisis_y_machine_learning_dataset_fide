# Análisis Profundo de Datasets
> Habilidad especial: análisis exhaustivo de cualquier dataset tabular (Kaggle, CSV, SQL, etc.)
> Fuente: Skillhabilities.txt + Documentacion Teorica 1.txt y 2

---

## Protocolo de Análisis para Cualquier Dataset

Cuando el usuario trae un dataset nuevo (Kaggle, CSV, SQL, etc.), seguir este protocolo:

---

## Paso 1 — Inspección Inicial

```python
import pandas as pd
import numpy as np

# Cargar (adaptado al formato del dataset)
df = pd.read_csv("dataset.csv")         # CSV
df = pd.read_parquet("dataset.parquet") # Parquet
# o desde catálogo Kedro:
df = catalog.load("mi_dataset")

# ── Información básica ────────────────────────────────────────────
print(f"Shape: {df.shape}")
print(f"Memoria: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
print("\nTipos de datos:")
print(df.dtypes.value_counts())

# ── Primeras y últimas filas ──────────────────────────────────────
df.head(5)
df.tail(5)

# ── Muestra aleatoria ─────────────────────────────────────────────
df.sample(10, random_state=42)

# ── Estadísticas descriptivas ─────────────────────────────────────
df.describe(include="all").T
```

---

## Paso 2 — Calidad de Datos

```python
# ── Valores faltantes ─────────────────────────────────────────────
missing = pd.DataFrame({
    "count": df.isnull().sum(),
    "pct": (df.isnull().mean() * 100).round(2),
    "dtype": df.dtypes,
}).sort_values("pct", ascending=False)
print(missing[missing["count"] > 0])

# ── Duplicados ────────────────────────────────────────────────────
print(f"Filas duplicadas: {df.duplicated().sum()} ({df.duplicated().mean():.1%})")
# Duplicados por columnas específicas:
# df.duplicated(subset=["id", "fecha"]).sum()

# ── Cardinalidad (variedad de valores únicos) ─────────────────────
cardinality = df.nunique().sort_values()
print("\nBaja cardinalidad (posibles categorías):")
print(cardinality[cardinality <= 20])
print("\nAlta cardinalidad (posibles IDs):")
print(cardinality[cardinality > df.shape[0] * 0.9])

# ── Outliers en numéricas (IQR) ───────────────────────────────────
def detect_outliers_iqr(series):
    Q1, Q3 = series.quantile([0.25, 0.75])
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
    mask = (series < lower) | (series > upper)
    return mask.sum(), lower, upper

for col in df.select_dtypes(include="number").columns:
    n_out, lo, hi = detect_outliers_iqr(df[col].dropna())
    if n_out > 0:
        print(f"{col}: {n_out} outliers fuera de [{lo:.2f}, {hi:.2f}]")
```

---

## Paso 3 — Análisis de la Variable Objetivo

```python
target_col = "mi_target"

# ── Tipo de problema ──────────────────────────────────────────────
n_unique = df[target_col].nunique()
dtype = df[target_col].dtype

if dtype == "object" or n_unique <= 20:
    print("→ Problema de CLASIFICACIÓN")
    print(df[target_col].value_counts())
    print(df[target_col].value_counts(normalize=True).round(3))

    # Balance de clases
    balance = df[target_col].value_counts(normalize=True)
    min_class = balance.min()
    if min_class < 0.1:
        print(f"⚠️ Dataset muy desbalanceado! Clase minoritaria: {min_class:.1%}")
else:
    print("→ Problema de REGRESIÓN")
    print(df[target_col].describe())

    # Distribución
    import matplotlib.pyplot as plt
    df[target_col].hist(bins=50)
    plt.title(f"Distribución de {target_col}")
    plt.show()

    # Skewness
    skew = df[target_col].skew()
    print(f"Asimetría: {skew:.3f}")
    if abs(skew) > 1:
        print("⚠️ Distribución muy asimétrica. Considerar transformación log.")
```

---

## Paso 4 — Análisis de Features

```python
import seaborn as sns
import matplotlib.pyplot as plt

# ── Distribución de variables numéricas ───────────────────────────
numeric_cols = df.select_dtypes(include="number").columns
df[numeric_cols].hist(bins=30, figsize=(15, 10))
plt.tight_layout()
plt.show()

# ── Correlación con el target ─────────────────────────────────────
if df[target_col].dtype != "object":  # target numérico
    correlations = df[numeric_cols].corrwith(df[target_col]).abs().sort_values(ascending=False)
    print("Correlaciones con el target:")
    print(correlations)

# ── Matriz de correlación ─────────────────────────────────────────
plt.figure(figsize=(12, 10))
corr_matrix = df[numeric_cols].corr()
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm",
            mask=np.triu(np.ones_like(corr_matrix, dtype=bool)))
plt.title("Matriz de Correlación")
plt.show()

# ── Detección de multicolinealidad ────────────────────────────────
high_corr = []
for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
        if abs(corr_matrix.iloc[i, j]) > 0.85:
            high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j],
                              corr_matrix.iloc[i, j]))
if high_corr:
    print("⚠️ Pares con alta correlación (|r| > 0.85):")
    for c1, c2, r in high_corr:
        print(f"  {c1} ↔ {c2}: {r:.3f}")

# ── Variables categóricas ─────────────────────────────────────────
cat_cols = df.select_dtypes(include="object").columns
for col in cat_cols:
    print(f"\n{col}: {df[col].nunique()} valores únicos")
    if df[col].nunique() <= 15:
        print(df[col].value_counts())
```

---

## Paso 5 — Identificar Posibles Problemas

```python
# ── Potencial data leakage ────────────────────────────────────────
# (correlaciones sospechosamente altas con el target)
if df[target_col].dtype != "object":
    suspicious = correlations[correlations > 0.95]
    if not suspicious.empty:
        print("⚠️ Posible data leakage! Features con r > 0.95 con el target:")
        print(suspicious)

# ── Variables temporales (series de tiempo) ───────────────────────
date_cols = df.select_dtypes(include=["datetime64", "object"]).columns
for col in date_cols:
    try:
        pd.to_datetime(df[col])
        print(f"📅 Posible columna temporal: {col}")
        print(f"   Rango: {pd.to_datetime(df[col]).min()} → {pd.to_datetime(df[col]).max()}")
    except:
        pass

# ── IDs y columnas a excluir ──────────────────────────────────────
probable_ids = [col for col in df.columns if df[col].nunique() == df.shape[0]]
print(f"Posibles columnas ID (excluir de features): {probable_ids}")

# ── Columnas constantes (sin información) ─────────────────────────
constant_cols = [col for col in df.columns if df[col].nunique() == 1]
print(f"Columnas constantes (eliminar): {constant_cols}")
```

---

## Paso 6 — Recomendaciones Automáticas

```python
def analyze_dataset_and_recommend(df: pd.DataFrame, target_col: str) -> dict:
    """Genera recomendaciones automáticas para el dataset."""
    recs = []
    n_rows, n_cols = df.shape

    # Tamaño del dataset
    if n_rows < 1000:
        recs.append("⚠️ Dataset pequeño (<1000 filas). Usar CV en lugar de un solo split.")
    if n_rows > 100_000:
        recs.append("ℹ️ Dataset grande. Considerar HistGradientBoosting y Parquet.")

    # Valores faltantes
    missing_pct = df.isnull().mean().max()
    if missing_pct > 0.3:
        recs.append(f"⚠️ Alta proporción de nulos ({missing_pct:.0%}). Revisar estrategia de imputación.")
    elif missing_pct > 0:
        recs.append(f"ℹ️ Hay valores nulos (máx {missing_pct:.0%}). Imputar o eliminar filas/columnas.")

    # Balance de clases (clasificación)
    if df[target_col].dtype == "object" or df[target_col].nunique() <= 20:
        balance = df[target_col].value_counts(normalize=True)
        if balance.min() < 0.1:
            recs.append("⚠️ Clases desbalanceadas. Considerar: stratify en split, class_weight='balanced', SMOTE.")
        recs.append("→ Métricas recomendadas: F1 macro, F1 weighted, classification_report, matriz de confusión.")
    else:
        recs.append("→ Métricas recomendadas: MAE, RMSE, R². Analizar residuos.")

    # Outliers
    num_cols = df.select_dtypes(include="number").columns
    for col in num_cols:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        n_out = ((df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)).sum()
        if n_out / n_rows > 0.05:
            recs.append(f"⚠️ {col}: {n_out/n_rows:.0%} de outliers. Revisar.")

    return {
        "shape": df.shape,
        "recommendations": recs,
        "missing_max_pct": float(missing_pct),
        "n_categories": int(df[target_col].nunique()),
    }
```

---

## Plantilla de catalog.yml para Cualquier Dataset

```yaml
# conf/base/catalog.yml — plantilla genérica

# ── Datos crudos ──────────────────────────────────────────────────
raw_data:
  type: pandas.CSVDataset      # Cambiar según formato: ParquetDataset, SQLTableDataset, etc.
  filepath: data/01_raw/dataset.csv
  load_args:
    sep: ","
    encoding: "utf-8"
  layer: raw

# ── Datos procesados ──────────────────────────────────────────────
preprocessed_data:
  type: pandas.ParquetDataset
  filepath: data/02_intermediate/preprocessed.parquet
  layer: intermediate

# ── Tabla analítica ML ────────────────────────────────────────────
features_for_ml:
  type: pandas.ParquetDataset
  filepath: data/05_model_input/features_for_ml.parquet
  layer: model_input

# ── Modelos ───────────────────────────────────────────────────────
best_model:
  type: pickle.PickleDataset
  filepath: data/06_models/best_model.pkl
  versioned: true
  layer: models

# ── Métricas y reportes ───────────────────────────────────────────
model_metrics:
  type: json.JSONDataset
  filepath: data/08_reporting/metrics.json
  layer: reporting

feature_importance:
  type: pandas.CSVDataset
  filepath: data/08_reporting/feature_importance.csv
  save_args:
    index: false
  layer: reporting

data_profile:
  type: json.JSONDataset
  filepath: data/08_reporting/data_profile.json
  layer: reporting
```

---

## Plantilla de parameters.yml para Cualquier Dataset

```yaml
# conf/base/parameters.yml — plantilla genérica

# ── Configuración del split ───────────────────────────────────────
test_size: 0.2
random_state: 42

# ── Columnas del dataset ─────────────────────────────────────────
target_column: "nombre_columna_objetivo"
feature_columns:
  - "feature_1"
  - "feature_2"
  # añadir más...

# ── Preprocesado ─────────────────────────────────────────────────
preprocessing:
  key_columns: []        # columnas que no pueden tener nulos
  date_columns: []       # columnas a parsear como datetime
  drop_columns: []       # columnas a eliminar (IDs, etc.)
  fill_strategy: null    # null | "median" | "mean" | "mode"
  outlier_method: null   # null | "iqr" | "zscore"

# ── Tipo de problema ─────────────────────────────────────────────
problem_type: "classification"  # classification | regression | clustering

# ── Hiperparámetros ─────────────────────────────────────────────
classifier_params:
  rf:
    n_estimators: 200
    max_depth: 10
    min_samples_leaf: 5

regressor_params:
  ridge:
    alpha: 1.0

clustering_params:
  n_clusters: 5
  pca_components: 2
```
