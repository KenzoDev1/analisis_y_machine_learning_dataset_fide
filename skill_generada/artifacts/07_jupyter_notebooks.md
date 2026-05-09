# Jupyter Notebooks con Kedro
> Fuente: Documentacion Teorica 3.txt + https://docs.kedro.org/en/1.3.1.post1/tutorials/notebooks_tutorial/

---

## Configuración del Entorno

### Antes de abrir cualquier notebook

```bash
# 1. Estar en la raíz del proyecto (donde está pyproject.toml)
cd /ruta/al/proyecto

# 2. Activar entorno virtual
source .venv/bin/activate          # Linux/Mac
.venv\Scripts\activate             # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
pip install -e .
# ó con uv:
uv sync --extra dev

# 4. (Si aplica) generar la base de datos o datos de prueba
python scripts/bootstrap_data.py

# 5. Lanzar Jupyter con contexto Kedro
kedro jupyter lab      # ← siempre desde la raíz del proyecto
# o
kedro jupyter notebook
```

### Primera celda obligatoria en cada notebook

```python
# Activar la extensión Kedro
%load_ext kedro.ipython

# Variables automáticamente disponibles:
# catalog  → DataCatalog del proyecto
# context  → KedroContext
# session  → KedroSession
# params   → diccionario de parámetros
# pipelines → diccionario de pipelines
```

---

## Variables Disponibles en el Notebook

```python
# Cargar cualquier dataset del catálogo
df = catalog.load("raw_data")
features = catalog.load("features_for_ml")

# Guardar un dataset al catálogo
catalog.save("mi_dataset_procesado", df_procesado)

# Acceder a parámetros
test_size = params["test_size"]
target_col = params["target_column"]

# Ejecutar un pipeline desde el notebook
session.run(pipeline_name="data_processing")
# o
from kedro.framework.session import KedroSession
with KedroSession.create(project_path=".") as session:
    session.run()

# Listar datasets disponibles
catalog.list()
```

---

## Secuencia de Notebooks Recomendada (CRISP-DM)

| Orden | Notebook | Fase CRISP-DM | Contenido | Tiempo |
|-------|---------|---------------|-----------|--------|
| 01 | `01_comprension_negocio_y_datos.ipynb` | 1–2 | Definición del problema, exploración inicial, calidad de datos | ~45 min |
| 02 | `02_preparacion_datos.ipynb` | 3 | Limpieza, features, comparación con Kedro | ~30 min |
| 03 | `03_clasificacion_resultado.ipynb` | 4–5 | Clasificadores, métricas, matriz de confusión | ~60 min |
| 04 | `04_regresion.ipynb` | 4–5 | Ridge, bosques, boosting; MAE, RMSE, R², residuos | ~45 min |
| 05 | `05_explicabilidad.ipynb` | 5 | Permutación, coeficientes logísticos, SHAP | ~30 min |
| 06 | `06_pipeline_kedro.ipynb` | 6 | Parámetros YAML, session.run(), leer salidas | ~30 min |
| 07 | `07_validacion_cruzada.ipynb` | 4–5 | KFold, cross_validate, GridSearchCV, RandomizedSearchCV | ~60 min |
| 08 | `08_clustering.ipynb` | 2–4 | PCA, K-Means, silhouette, interpretación de clusters | ~45 min |

Opcional: `Exploracion_de_datos.ipynb` — Todo en uno para repaso rápido.

---

## Notebook 01 — Comprensión de Negocio y Datos

```python
# 1. Cargar datos crudos desde el catálogo
%load_ext kedro.ipython
df = catalog.load("raw_data")

# 2. Vista general
print(f"Shape: {df.shape}")
print(df.dtypes)
df.head()

# 3. Valores faltantes
missing = df.isnull().sum().sort_values(ascending=False)
print(missing[missing > 0])
print(f"\nPorcentaje faltante:\n{(missing / len(df) * 100).round(2)}")

# 4. Estadísticas descriptivas
df.describe()

# 5. Distribución del target
import matplotlib.pyplot as plt
target_col = params["target_column"]
df[target_col].value_counts().plot(kind="bar")
plt.title(f"Distribución de {target_col}")
plt.show()

# 6. Correlaciones
import seaborn as sns
numeric_df = df.select_dtypes(include="number")
plt.figure(figsize=(12, 8))
sns.heatmap(numeric_df.corr(), annot=True, fmt=".2f", cmap="coolwarm")
plt.title("Matriz de Correlación")
plt.show()
```

---

## Notebook 03 — Clasificación

```python
# Cargar features y target
features = catalog.load("features_for_ml")
target_col = params["target_column"]
feature_cols = params["feature_columns"]

X = features[feature_cols]
y = features[target_col]

# Split
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=params["test_size"],
    random_state=params["random_state"], stratify=y
)

# Entrenar y evaluar clasificadores
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, classification_report

models = {
    "Logistic": LogisticRegression(max_iter=500, random_state=42),
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
}

results = []
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred, average="macro")
    results.append({"model": name, "f1_macro": f1})
    print(f"\n=== {name} ===")
    print(classification_report(y_test, y_pred))

# Comparar modelos
import pandas as pd
pd.DataFrame(results).sort_values("f1_macro", ascending=False).plot(
    x="model", y="f1_macro", kind="bar"
)
plt.title("Comparación de F1 Macro")
plt.show()
```

---

## Notebook 07 — Validación Cruzada e Hiperparámetros

```python
# La diferencia con Kedro run: CV evalúa varianza del split
from sklearn.model_selection import StratifiedKFold, cross_validate, GridSearchCV

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Evaluar instabilidad del split
scores = cross_validate(
    model, X, y, cv=cv,
    scoring=["f1_macro", "accuracy"],
    return_train_score=True,
)
print(f"F1 macro CV: {scores['test_f1_macro'].mean():.4f} ± {scores['test_f1_macro'].std():.4f}")

# GridSearchCV
from sklearn.pipeline import Pipeline as SkPipeline
from sklearn.preprocessing import StandardScaler
pipe = SkPipeline([("scaler", StandardScaler()), ("clf", LogisticRegression())])
param_grid = {"clf__C": [0.01, 0.1, 1.0, 10.0], "clf__max_iter": [100, 500]}
grid = GridSearchCV(pipe, param_grid, cv=cv, scoring="f1_macro", n_jobs=-1)
grid.fit(X_train, y_train)
print(f"Mejor configuración: {grid.best_params_}")
print(f"Mejor F1 macro en CV: {grid.best_score_:.4f}")

# ⚠️ Mensaje clave: Kedro run responde ¿cómo dejo versionado un flujo?
# Notebook 07 responde ¿el número que vi en test fue suerte del split?
```

---

## Notebook 08 — Clustering No Supervisado

```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# Cargar datos y seleccionar features numéricas
df = catalog.load("features_for_ml")
feature_cols = df.select_dtypes(include="number").columns.tolist()
X = df[feature_cols].dropna()

# Escalado + PCA
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_scaled)
print(f"Varianza explicada: {pca.explained_variance_ratio_.sum():.2%}")

# Elegir k con elbow method
inertias = []
sil_scores = []
k_range = range(2, 11)
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init="auto")
    labels = km.fit_predict(X_pca)
    inertias.append(km.inertia_)
    sil_scores.append(silhouette_score(X_pca, labels))

# Gráfica del codo
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.plot(k_range, inertias, "o-")
ax1.set_title("Elbow Method (Inercia)")
ax2.plot(k_range, sil_scores, "s-", color="orange")
ax2.set_title("Silhouette Score")
plt.show()
```

---

## Diferencia Notebook vs Kedro Run

| Aspecto | Notebook (exploración) | `kedro run` (producción) |
|---------|----------------------|--------------------------|
| Propósito | Pensar, iterar, enseñar | Cerrar el ciclo CRISP-DM |
| Artefactos | En memoria (temporales) | Parquet, JSON, pkl en disk |
| Reproducibilidad | Depende del orden de celdas | Garantizada por el DAG |
| Hiperparámetros | En celdas Python | En YAML |
| CV / GridSearch | ✅ Sí (notebook 07) | ❌ No (a propósito) |
| Recomendado para | Análisis exploratorio | Entrega, CI/CD |

> **Regla de oro:** El notebook sirve para **pensar**. Kedro sirve para **entregar**.

---

## Salidas Generadas por `kedro run`

```
data/05_model_input/
└── features_for_ml.parquet          ← tabla analítica

data/06_models/
├── best_classifier.pkl              ← mejor clasificador
└── best_regressor.pkl               ← mejor regresor

data/08_reporting/
├── classification_metrics.json      ← F1, accuracy, report por clase
├── regression_metrics.json          ← MAE, RMSE, R²
├── feature_importance_clf.csv       ← importancia por permutación (clf)
└── feature_importance_reg.csv       ← importancia por permutación (reg)
```
