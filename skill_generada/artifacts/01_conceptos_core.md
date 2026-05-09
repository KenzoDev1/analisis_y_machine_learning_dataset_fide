# Conceptos Core de Kedro
> Fuente: https://docs.kedro.org/en/1.3.1.post1/getting-started/kedro_concepts/

---

## Los 3 Pilares de Kedro

### 1. Node (Nodo)
Un **nodo** es la unidad mínima de cómputo en Kedro. Envuelve una función Python pura y declara explícitamente sus entradas y salidas.

```python
from kedro.pipeline import node

# Función Python pura
def split_data(data: pd.DataFrame, test_size: float) -> tuple:
    X = data.drop("target", axis=1)
    y = data["target"]
    return train_test_split(X, y, test_size=test_size)

# Nodo Kedro
split_node = node(
    func=split_data,
    inputs=["features_for_ml", "params:test_size"],   # nombres del catálogo
    outputs=["X_train", "X_test", "y_train", "y_test"],
    name="split_data_node",
    tags=["training"]
)
```

**Reglas de oro de los nodos:**
- La función debe ser **pura**: mismas entradas → mismas salidas (sin efectos secundarios)
- Los nombres de inputs/outputs son **nombres del catálogo**, no variables Python
- `params:` es el prefijo para leer valores de `parameters.yml`
- `parameters` (sin prefijo de campo) carga el dict completo de parámetros

---

### 2. Pipeline
Un **pipeline** es un DAG (grafo acíclico dirigido) de nodos. Kedro resuelve el orden de ejecución automáticamente basándose en dependencias de datos.

```python
from kedro.pipeline import Pipeline, pipeline, node

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(func=preprocess, inputs="raw_data", outputs="clean_data", name="preprocess_node"),
        node(func=build_features, inputs="clean_data", outputs="features", name="features_node"),
        node(func=train_model, inputs=["features", "params:model_options"], outputs="model", name="train_node"),
    ])
```

**Propiedades de un Pipeline:**
```python
pipe = create_pipeline()
pipe.nodes          # lista de nodos
pipe.all_inputs()   # todos los datasets que consume
pipe.all_outputs()  # todos los datasets que produce
pipe.inputs()       # inputs que no son outputs de otro nodo (fuentes externas)
pipe.outputs()      # outputs que no son inputs de otro nodo (resultados finales)
pipe.describe()     # descripción textual del grafo
```

---

### 3. Data Catalog
El **Data Catalog** es el registro central de todos los datasets del proyecto. Abstrae el acceso a datos, desacoplando el código de los detalles de almacenamiento.

```python
# Acceso programático
catalog.load("features_for_ml")    # carga el dataset
catalog.save("model", trained_model)  # guarda el dataset
catalog.list()                      # lista todos los datasets registrados
```

---

## Estructura de Directorios

### conf/base/ — Configuración compartida
| Archivo | Propósito |
|---------|-----------|
| `catalog.yml` | Define todos los datasets (tipo, ruta, parámetros) |
| `parameters.yml` | Hiperparámetros, proporciones de split, columnas objetivo |
| `parameters_<pipeline>.yml` | Parámetros específicos de un pipeline |
| `logging.yml` | Configuración de logging |

### conf/local/ — Configuración personal (NO commitear)
| Archivo | Propósito |
|---------|-----------|
| `credentials.yml` | Claves API, contraseñas de BD, tokens |

### data/ — Capas de datos (por convención)
```
01_raw/          ← Datos originales, nunca modificar
02_intermediate/ ← Transformaciones parciales
03_primary/      ← Datos limpios y verificados
04_feature/      ← Features calculadas
05_model_input/  ← Tabla analítica lista para ML
06_models/       ← Modelos serializados (.pkl)
07_model_output/ ← Predicciones del modelo
08_reporting/    ← Métricas, figuras, reportes
```

### src/<proyecto>/pipelines/ — Código de pipelines
Cada pipeline es un **módulo Python** con su propio directorio:
```
pipelines/
└── data_processing/
    ├── __init__.py       ← exporta create_pipeline()
    ├── nodes.py          ← funciones Python puras
    └── pipeline.py       ← ensamblaje de nodos en pipeline
```

---

## pipeline_registry.py — El Registro Central

```python
from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

def register_pipelines() -> dict[str, Pipeline]:
    """Registra todos los pipelines del proyecto."""
    pipelines = find_pipelines()  # descubrimiento automático
    pipelines["__default__"] = (
        pipelines["data_processing"]
        + pipelines["ml_classification"]
        + pipelines["ml_regression"]
    )
    return pipelines
```

---

## settings.py — Configuración del Proyecto

```python
from kedro.config import OmegaConfigLoader
from kedro.framework.hooks import _create_hook_manager

# Config loader
CONFIG_LOADER_CLASS = OmegaConfigLoader
CONFIG_LOADER_ARGS = {
    "base_env": "base",
    "default_run_env": "local",
}

# Hooks personalizados
HOOKS = (MyCustomHook(),)

# Librería de sesión
SESSION_STORE_CLASS = BaseSessionStore
```

---

## Glosario Kedro

| Término | Definición |
|---------|-----------|
| **Node** | Función Python con entradas y salidas nombradas |
| **Pipeline** | DAG de nodos con dependencias resueltas automáticamente |
| **Data Catalog** | Registro de datasets con sus configuraciones de carga/guardado |
| **Dataset** | Un elemento de datos específico (archivo, tabla, objeto en memoria) |
| **MemoryDataset** | Dataset temporal que vive solo en RAM durante la ejecución |
| **Namespace** | Prefijo que permite reusar pipelines con distintos conjuntos de datos |
| **Hook** | Puntos de extensión del ciclo de vida de Kedro (before_node_run, after_pipeline_run, etc.) |
| **Starter** | Plantilla de proyecto Kedro preconfigurable |
| **Tag** | Etiqueta en nodos para ejecutar subconjuntos del pipeline |
| **Slice** | Subconjunto de un pipeline basado en nodos o datasets |
| **Config Loader** | Componente que lee y resuelve YAML de configuración |
| **KedroSession** | Objeto que gestiona el ciclo de vida de una ejecución Kedro |
| **KedroContext** | Acceso al catálogo, config y pipelines desde una sesión |
