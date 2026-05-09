# Extensiones — Hooks, Plugins y Datasets Personalizados
> Fuente: https://docs.kedro.org/en/1.3.1.post1/extend/

---

## Hooks — Puntos de Extensión del Ciclo de Vida

Los Hooks permiten inyectar comportamiento en puntos clave de la ejecución sin modificar el código del pipeline.

### Puntos de extensión disponibles

| Hook | Cuándo se ejecuta |
|------|------------------|
| `before_node_run` | Antes de ejecutar cada nodo |
| `after_node_run` | Después de ejecutar cada nodo |
| `on_node_error` | Si un nodo falla |
| `before_pipeline_run` | Antes de ejecutar el pipeline |
| `after_pipeline_run` | Después de ejecutar el pipeline |
| `on_pipeline_error` | Si el pipeline falla |
| `before_dataset_loaded` | Antes de cargar un dataset |
| `after_dataset_loaded` | Después de cargar un dataset |
| `before_dataset_saved` | Antes de guardar un dataset |
| `after_dataset_saved` | Después de guardar un dataset |

---

### Ejemplo: Hook de Logging de Métricas

```python
# src/myproject/hooks.py
import logging
from kedro.framework.hooks import hook_impl
from kedro.pipeline.node import Node
from kedro.io import DataCatalog

logger = logging.getLogger(__name__)


class LoggingHook:
    """Hook que registra información de cada nodo."""

    @hook_impl
    def before_node_run(self, node: Node, catalog: DataCatalog, inputs: dict, run_id: str):
        logger.info(f"▶ Ejecutando nodo: {node.name}")
        logger.info(f"  Inputs: {list(inputs.keys())}")

    @hook_impl
    def after_node_run(
        self, node: Node, catalog: DataCatalog,
        inputs: dict, outputs: dict, run_id: str
    ):
        logger.info(f"✓ Nodo completado: {node.name}")
        for name, value in outputs.items():
            if hasattr(value, "shape"):
                logger.info(f"  Output '{name}': shape={value.shape}")

    @hook_impl
    def on_node_error(self, error: Exception, node: Node, run_id: str):
        logger.error(f"✗ Error en nodo {node.name}: {error}")
```

---

### Ejemplo: Hook de MLflow para experimentos

```python
# src/myproject/hooks.py
import mlflow
from kedro.framework.hooks import hook_impl


class MLflowHook:
    """Hook que registra experimentos en MLflow."""

    @hook_impl
    def before_pipeline_run(self, run_params: dict, pipeline, catalog):
        mlflow.start_run(run_name=run_params.get("run_id", "kedro_run"))
        mlflow.log_params(run_params)

    @hook_impl
    def after_dataset_saved(self, dataset_name: str, data, run_id: str):
        # Registrar métricas automáticamente
        if dataset_name.endswith("_metrics") and isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(f"{dataset_name}.{key}", value)

    @hook_impl
    def after_pipeline_run(self, run_params: dict, run_result, pipeline, catalog):
        mlflow.end_run()

    @hook_impl
    def on_pipeline_error(self, error: Exception, run_params: dict, pipeline, catalog):
        mlflow.end_run(status="FAILED")
```

---

### Registrar Hooks en settings.py

```python
# src/myproject/settings.py
from myproject.hooks import LoggingHook, MLflowHook

HOOKS = (
    LoggingHook(),
    MLflowHook(),
)
```

---

## Datasets Personalizados

Cuando ningún dataset estándar se ajusta a tu fuente de datos:

```python
# src/myproject/datasets/custom_api_dataset.py
import requests
from kedro.io import AbstractDataset
from typing import Any


class RestAPIDataset(AbstractDataset):
    """Dataset que carga datos desde una API REST."""

    def __init__(self, url: str, headers: dict = None, params: dict = None):
        self._url = url
        self._headers = headers or {}
        self._params = params or {}

    def _load(self) -> dict:
        """Descarga datos de la API."""
        response = requests.get(self._url, headers=self._headers, params=self._params)
        response.raise_for_status()
        return response.json()

    def _save(self, data: dict) -> None:
        """No implementado — API de solo lectura."""
        raise NotImplementedError("RestAPIDataset es de solo lectura.")

    def _describe(self) -> dict:
        """Descripción del dataset para logging."""
        return {"url": self._url, "params": self._params}


# Uso en catalog.yml:
# mis_datos_api:
#   type: myproject.datasets.custom_api_dataset.RestAPIDataset
#   url: "https://api.ejemplo.com/datos"
#   params:
#     limit: 1000
```

---

### Dataset con validación de esquema (Pandera)

```python
# src/myproject/datasets/validated_dataset.py
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema
from kedro.io import AbstractDataset


class ValidatedCSVDataset(AbstractDataset):
    """Dataset CSV con validación de esquema Pandera."""

    def __init__(self, filepath: str, schema: dict):
        self._filepath = filepath
        self._schema = DataFrameSchema({
            col: Column(dtype_info["dtype"], nullable=dtype_info.get("nullable", False))
            for col, dtype_info in schema.items()
        })

    def _load(self) -> pd.DataFrame:
        df = pd.read_csv(self._filepath)
        validated_df = self._schema.validate(df)  # lanza error si falla validación
        return validated_df

    def _save(self, data: pd.DataFrame) -> None:
        self._schema.validate(data)
        data.to_csv(self._filepath, index=False)

    def _describe(self) -> dict:
        return {"filepath": self._filepath}
```

---

## Uso Programático (KedroSession)

```python
# Ejecutar Kedro desde un script Python externo
from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project
from pathlib import Path

project_path = Path("/ruta/al/proyecto")
bootstrap_project(project_path)

with KedroSession.create(project_path=project_path) as session:
    # Ejecutar el pipeline completo
    session.run()

    # Ejecutar un pipeline específico
    session.run(pipeline_name="ml_classification")

    # Ejecutar desde un nodo
    session.run(from_nodes=["split_data_node"])

    # Acceder al contexto
    context = session.load_context()
    catalog = context.catalog
    df = catalog.load("features_for_ml")
```

---

## Plugins Personalizados

Un plugin Kedro es un paquete Python que extiende la CLI o el comportamiento:

```python
# setup.py / pyproject.toml
# [project.entry-points."kedro.hooks"]
# my_plugin = "my_package.hooks:MyPlugin"

# [project.entry-points."kedro.project_commands"]
# mi_comando = "my_package.cli:mi_grupo_cli"
```

```python
# my_package/cli.py
import click
from kedro.framework.cli.utils import KedroCliError


@click.group(name="mi-plugin")
def mi_grupo_cli():
    """Comandos del plugin personalizado."""
    pass


@mi_grupo_cli.command()
@click.option("--output", default="report.html")
def generate_report(output):
    """Genera un reporte HTML del pipeline."""
    click.echo(f"Generando reporte en {output}...")
    # lógica del reporte
```

---

## Starters Personalizados

Un starter es una plantilla de proyecto Kedro:

```bash
# Crear proyecto desde starter oficial
kedro new --starter spaceflights

# Listar starters disponibles
kedro starter list

# Crear desde starter propio (Git)
kedro new --starter https://github.com/mi-org/mi-starter.git
```

---

## LLM Context Node (Experimental — Kedro 1.3)

```python
# Nodo especial para integrar LLMs en el pipeline
from kedro.pipeline import node
from kedro.pipeline.modular_pipeline import pipeline

# El LLM Context Node permite pasar contexto del catálogo a un LLM
# para análisis o generación de código asistido
llm_node = node(
    func=my_llm_analysis_function,
    inputs=["features_for_ml", "params:llm_prompt"],
    outputs="llm_insights",
    name="llm_analysis_node",
    tags=["experimental", "llm"],
)
```
