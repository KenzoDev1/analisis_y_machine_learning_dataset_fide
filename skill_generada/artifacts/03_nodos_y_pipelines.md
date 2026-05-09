# Nodos y Pipelines — Referencia Completa
> Fuente: https://docs.kedro.org/en/1.3.1.post1/build/nodes/ y pipeline_introduction/

---

## Definición de Nodos

### Sintaxis básica

```python
from kedro.pipeline import node

node(
    func=mi_funcion,           # función Python pura (OBLIGATORIO)
    inputs="dataset_entrada",  # str, list[str] o dict (OBLIGATORIO, puede ser None)
    outputs="dataset_salida",  # str, list[str] o dict (OBLIGATORIO, puede ser None)
    name="nombre_descriptivo", # identificador único (recomendado)
    tags=["etiqueta"],         # lista de tags (opcional)
    confirms=["dataset"],      # confirmar uso de dataset antes de continuar
)
```

---

### Sintaxis para inputs

```python
# Un input → string
inputs="ventas_raw"

# Múltiples inputs → lista (posicional con la función)
inputs=["X_train", "y_train", "params:test_size"]

# Mapeo nombre_catalogo → nombre_argumento de la función
inputs={"data": "ventas_raw", "config": "params:model_options"}

# Sin inputs (genera datos desde cero)
inputs=None

# Parámetros desde parameters.yml
inputs="params:test_size"          # un parámetro específico
inputs="parameters"                # el diccionario completo
```

### Sintaxis para outputs

```python
# Un output → string
outputs="features_for_ml"

# Múltiples outputs → lista (debe coincidir con la tupla retornada)
outputs=["X_train", "X_test", "y_train", "y_test"]

# Sin outputs (función de efectos secundarios)
outputs=None

# Dict para mapear posición → nombre catálogo
outputs={"model": "trained_classifier", "metrics": "classification_metrics"}
```

---

### Funciones con *args y **kwargs

```python
# Función que acepta *args
def concatenate(*dfs: pd.DataFrame) -> pd.DataFrame:
    return pd.concat(dfs, ignore_index=True)

node(
    func=concatenate,
    inputs=["df_2020", "df_2021", "df_2022"],  # pasa como positional args
    outputs="df_completo",
)

# Función que acepta **kwargs (recibe dict)
def train_all_models(**model_configs) -> dict:
    results = {}
    for name, config in model_configs.items():
        results[name] = train_model(**config)
    return results

node(
    func=train_all_models,
    inputs={"logistic": "params:logistic_config", "forest": "params:forest_config"},
    outputs="all_model_results",
)
```

---

### Funciones generadoras (para datasets grandes)

```python
# Cargar datos en chunks con generador
def load_large_dataset(filepath: str):
    for chunk in pd.read_csv(filepath, chunksize=10000):
        yield chunk

# Nodo que guarda en streaming
node(
    func=load_large_dataset,
    inputs="params:large_file_path",
    outputs="large_dataset",
)
```

---

### Preview de nodos (Kedro Viz)

```python
from kedro.pipeline import node
from kedro_datasets.pandas import ParquetDataset

def add_preview(outputs, *args, **kwargs):
    """Agrega preview a un nodo para Kedro Viz."""
    ...

# Decorador de preview
@node_preview(
    preview_type="text",
    preview_func=lambda df: df.describe().to_string()
)
def build_features(data: pd.DataFrame) -> pd.DataFrame:
    return data
```

---

## Construcción de Pipelines

### Pipeline básico

```python
from kedro.pipeline import Pipeline, node, pipeline

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=preprocess_data,
            inputs=["raw_data", "params:preprocessing"],
            outputs="clean_data",
            name="preprocess_node",
        ),
        node(
            func=build_features,
            inputs="clean_data",
            outputs="features",
            name="features_node",
        ),
        node(
            func=train_model,
            inputs=["features", "params:model_options"],
            outputs=["trained_model", "metrics"],
            name="train_node",
            tags=["training"],
        ),
    ])
```

---

### Merge de pipelines

```python
# En pipeline_registry.py
from src.myproject.pipelines import data_processing, ml_classification, ml_regression

def register_pipelines() -> dict:
    dp = data_processing.create_pipeline()
    clf = ml_classification.create_pipeline()
    reg = ml_regression.create_pipeline()

    return {
        "data_processing": dp,
        "ml_classification": clf,
        "ml_regression": reg,
        "__default__": dp + clf + reg,  # ← merge con +
    }
```

---

### Slicing de pipelines

```python
# Ejecutar desde un nodo específico
kedro run --from-nodes "train_node"

# Ejecutar hasta un nodo específico
kedro run --to-nodes "features_node"

# Ejecutar solo nodos con un tag
kedro run --tags training

# Ejecutar solo nodos específicos
kedro run --nodes "preprocess_node,features_node"

# Ejecutar desde un dataset
kedro run --from-inputs "clean_data"

# Ejecutar hasta un dataset (y no más allá)
kedro run --to-outputs "features"
```

---

### Namespaces (Reutilización de Pipelines)

Los namespaces permiten reusar el mismo pipeline con distintos datos:

```python
from kedro.pipeline import pipeline

# Pipeline base
training_pipeline = create_training_pipeline()

# Instancias con diferentes namespaces
pipeline_v1 = pipeline(
    pipe=training_pipeline,
    namespace="modelo_v1",
    inputs={"raw_data": "ventas_2023"},       # mapeo de inputs externos
    outputs={"trained_model": "model_v1_pkl"} # mapeo de outputs externos
)

pipeline_v2 = pipeline(
    pipe=training_pipeline,
    namespace="modelo_v2",
    inputs={"raw_data": "ventas_2024"},
    outputs={"trained_model": "model_v2_pkl"}
)

# Combinar
full_pipeline = pipeline_v1 + pipeline_v2
```

---

### Tags en nodos y pipelines

```python
# Tag en nodo individual
node(func=fn, inputs="x", outputs="y", tags=["preprocessing", "critical"])

# Añadir tags a todo un pipeline
pipeline(pipe=my_pipeline, tags=["ml"])

# Ejecutar solo nodos con cierto tag
kedro run --tags preprocessing
```

---

## Información del Pipeline

```python
pipe = create_pipeline()

# Nodos
pipe.nodes                    # lista de objetos Node
pipe.node_dependencies        # dict: nombre_nodo → set de nodos dependientes

# Datasets
pipe.all_inputs()             # todos los inputs de todos los nodos
pipe.all_outputs()            # todos los outputs de todos los nodos
pipe.inputs()                 # inputs que no son outputs de ningún nodo
pipe.outputs()                # outputs que no son inputs de ningún nodo
pipe.data_sets()              # todos los datasets mencionados

# Descripción
print(pipe.describe())        # vista textual del DAG

# Filtrar
pipe.only_nodes("node_a", "node_b")      # solo esos nodos
pipe.only_nodes_with_tags("training")    # solo nodos con ese tag
pipe.from_nodes("split_node")            # desde ese nodo en adelante
pipe.to_nodes("train_node")              # hasta ese nodo
pipe.from_inputs("raw_data")            # a partir de ese input
pipe.to_outputs("features")             # hasta ese output
```

---

## Errores Comunes en Pipelines

### Pipeline con nodos que producen el mismo output
```python
# ❌ Error: dos nodos producen "features"
node(func=fn1, inputs="a", outputs="features"),
node(func=fn2, inputs="b", outputs="features"),  # ← conflicto
```

### Dependencias circulares
```python
# ❌ Error: A necesita B, B necesita A
node(func=fn_a, inputs="dataset_b", outputs="dataset_a"),
node(func=fn_b, inputs="dataset_a", outputs="dataset_b"),
```

### Nombres con punto (dot notation) — no permitidos como inputs/outputs
```python
# ❌ Error
outputs="model.metrics"  # el punto tiene significado especial en namespaces

# ✓ Correcto
outputs="model_metrics"
```

---

## nodes.py — Patrón Recomendado

```python
# src/myproject/pipelines/data_processing/nodes.py
import logging
import pandas as pd
from typing import Any

logger = logging.getLogger(__name__)


def preprocess_data(data: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Limpia y prepara el dataset para análisis.

    Args:
        data: DataFrame con datos crudos.
        params: Diccionario de parámetros de preprocesado.

    Returns:
        DataFrame limpio y preprocesado.
    """
    logger.info(f"Dataset recibido: {data.shape[0]} filas, {data.shape[1]} columnas")

    # Eliminar duplicados
    data = data.drop_duplicates()

    # Eliminar filas con NaN en columnas clave
    key_cols = params.get("key_columns", [])
    data = data.dropna(subset=key_cols)

    # Resetear índice
    data = data.reset_index(drop=True)

    logger.info(f"Dataset limpio: {data.shape[0]} filas")
    return data


def build_ml_features_table(
    data: pd.DataFrame,
    target_col: str,
    feature_cols: list[str],
) -> pd.DataFrame:
    """Construye la tabla analítica para ML.

    Args:
        data: DataFrame preprocesado.
        target_col: Nombre de la columna objetivo.
        feature_cols: Lista de columnas a usar como features.

    Returns:
        DataFrame con features y target seleccionados.
    """
    cols_to_keep = feature_cols + [target_col]
    available = [c for c in cols_to_keep if c in data.columns]
    missing = set(cols_to_keep) - set(available)

    if missing:
        logger.warning(f"Columnas no encontradas y omitidas: {missing}")

    return data[available].dropna().reset_index(drop=True)
```

---

## pipeline.py — Patrón Recomendado

```python
# src/myproject/pipelines/data_processing/pipeline.py
from kedro.pipeline import Pipeline, node, pipeline
from .nodes import preprocess_data, build_ml_features_table


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=preprocess_data,
            inputs=["raw_data", "params:preprocessing"],
            outputs="preprocessed_data",
            name="preprocess_data_node",
            tags=["preprocessing"],
        ),
        node(
            func=build_ml_features_table,
            inputs=[
                "preprocessed_data",
                "params:target_column",
                "params:feature_columns",
            ],
            outputs="features_for_ml",
            name="build_features_node",
            tags=["feature_engineering"],
        ),
    ])
```
