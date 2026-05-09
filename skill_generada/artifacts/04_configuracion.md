# Configuración Kedro — parameters.yml, credentials y OmegaConf
> Fuente: https://docs.kedro.org/en/1.3.1.post1/configure/

---

## parameters.yml — Parámetros del Proyecto

### Estructura base

```yaml
# conf/base/parameters.yml

# ── Split de datos ──────────────────────────────────────────────
test_size: 0.2
random_state: 42

# ── Columnas del dataset ─────────────────────────────────────────
target_column: "resultado"          # columna a predecir (clasificación)
target_column_reg: "ventas_totales" # columna a predecir (regresión)
feature_columns:
  - "feature_1"
  - "feature_2"
  - "feature_3"

# ── Preprocesado ─────────────────────────────────────────────────
preprocessing:
  key_columns:
    - "id"
    - "fecha"
  fill_strategy: "median"
  outlier_method: "iqr"
  iqr_factor: 1.5

# ── Opciones de modelo ───────────────────────────────────────────
model_options:
  test_size: 0.2
  random_state: 42
  cv_folds: 5
  scoring: "f1_macro"
```

### Parámetros por pipeline

```yaml
# conf/base/parameters_data_processing.yml
key_columns: ["id", "fecha"]
drop_duplicates: true
date_columns: ["fecha_inicio", "fecha_fin"]

# conf/base/parameters_ml_classification.yml
classifier_params:
  logistic:
    C: 1.0
    max_iter: 500
    solver: "lbfgs"
    multi_class: "auto"
  random_forest:
    n_estimators: 200
    max_depth: 10
    min_samples_leaf: 5
    random_state: 42
  gradient_boosting:
    max_iter: 200
    learning_rate: 0.05
    max_depth: 4
    random_state: 42

# conf/base/parameters_ml_regression.yml
regressor_params:
  ridge:
    alpha: 1.0
  random_forest:
    n_estimators: 100
    max_depth: 8
```

---

## Leer Parámetros en Nodos

### Método 1: params: (recomendado para valores individuales)

```python
# En pipeline.py:
node(
    func=split_data,
    inputs=["features_for_ml", "params:test_size", "params:random_state"],
    outputs=["X_train", "X_test", "y_train", "y_test"],
    name="split_node",
)

# En nodes.py:
def split_data(data, test_size, random_state):
    return train_test_split(data, test_size=test_size, random_state=random_state)
```

### Método 2: parameters (diccionario completo)

```python
# En pipeline.py:
node(
    func=train_all_models,
    inputs=["X_train", "y_train", "parameters"],
    outputs="all_models",
    name="train_all_node",
)

# En nodes.py:
def train_all_models(X_train, y_train, parameters):
    config = parameters["classifier_params"]
    # usar config["logistic"]["C"], etc.
```

### Método 3: params: con ruta de acceso anidada

```python
# En pipeline.py (para parámetros anidados):
inputs=["data", "params:preprocessing.key_columns"]

# En nodes.py:
def process(data, key_columns):  # recibe la lista directamente
    ...
```

---

## OmegaConf — Configuración Avanzada

Kedro 1.3 usa OmegaConf como config loader por defecto.

### Interpolación entre archivos

```yaml
# conf/base/parameters.yml
experiment_name: "experimento_clasificacion"
output_dir: "data/08_reporting"
metrics_path: "${output_dir}/metrics_${experiment_name}.json"  # ← interpolación
```

### Overrides por entorno

```yaml
# conf/local/parameters.yml  ← sobreescribe base durante desarrollo
test_size: 0.3       # más datos de test en local
random_state: 0      # semilla diferente
```

### Variables de entorno

```yaml
# conf/base/credentials.yml
database:
  password: ${oc.env:DB_PASSWORD}   # lee la variable de entorno DB_PASSWORD
  host: ${oc.env:DB_HOST,localhost} # con valor por defecto
```

### Resolvers custom (OmegaConf)

```python
# En settings.py
from omegaconf import OmegaConf

OmegaConf.register_new_resolver(
    "timestamp",
    lambda: datetime.now().strftime("%Y%m%d_%H%M%S")
)

# En YAML
run_id: "run_${timestamp:}"
```

---

## Credentials — Gestión Segura

```yaml
# conf/local/credentials.yml  ← NUNCA en Git

# Base de datos relacional
postgres:
  con: "postgresql://usuario:contraseña@host:5432/base_datos"

# SQLite (relativa al proyecto)
sqlite:
  con: "sqlite:///data/raw/database.sqlite"

# AWS S3
s3:
  client_kwargs:
    aws_access_key_id: AKIAIOSFODNN7EXAMPLE
    aws_secret_access_key: wJalrXUtnFEMI/K7MDENG

# Google Cloud Storage
gcs:
  project: "mi-proyecto-gcp"
  credentials:
    type: service_account
    project_id: "mi-proyecto-gcp"
    private_key_id: "key_id"
    private_key: "-----BEGIN RSA PRIVATE KEY-----\n..."

# Azure Blob Storage
azure:
  account_name: "mi_storage"
  account_key: "key..."

# Databricks
databricks:
  host: "https://mi-workspace.azuredatabricks.net"
  token: "dapi..."
```

---

## Validación de Parámetros

Con Pydantic en Kedro 1.3:

```python
# src/myproject/parameters_schema.py
from pydantic import BaseModel, Field, validator
from typing import Literal

class SplitConfig(BaseModel):
    test_size: float = Field(default=0.2, ge=0.05, le=0.5)
    random_state: int = Field(default=42, ge=0)

class ModelConfig(BaseModel):
    algorithm: Literal["logistic", "random_forest", "gradient_boosting"]
    hyperparams: dict

class ProjectParameters(BaseModel):
    split: SplitConfig
    model: ModelConfig
    target_column: str
    feature_columns: list[str]

    @validator("feature_columns")
    def features_not_empty(cls, v):
        assert len(v) > 0, "feature_columns no puede estar vacío"
        return v
```

```yaml
# conf/base/parameters.yml (con validación activada)
split:
  test_size: 0.2
  random_state: 42
model:
  algorithm: "random_forest"
  hyperparams:
    n_estimators: 100
target_column: "outcome"
feature_columns: ["col1", "col2"]
```

---

## Configuration Basics — Resolución de Archivos

Kedro carga y **fusiona** la configuración en este orden de prioridad:
1. `conf/base/` — configuración compartida y versionada
2. `conf/local/` — configuración personal/local (gitignoreada)
3. Variables de entorno (si se configura OmegaConf)

La configuración local **sobreescribe** la base en las claves coincidentes.

```
conf/base/parameters.yml       → test_size: 0.2
conf/local/parameters.yml      → test_size: 0.3   ← gana este
```

### Acceso programático a la config

```python
# En sesión Kedro o notebook
from kedro.config import OmegaConfigLoader
from kedro.framework.project import settings

conf_loader = OmegaConfigLoader(conf_source=str(settings.CONF_SOURCE))
params = conf_loader["parameters"]
catalog_conf = conf_loader["catalog"]

# En notebook (con %load_ext kedro.ipython)
params = context.params
catalog = context.catalog
```
