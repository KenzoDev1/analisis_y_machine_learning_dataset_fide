# SKILL KEDRO — Índice Maestro
> Versión: 1.0 · Kedro 1.3.1.post1 · Referencia: https://docs.kedro.org/en/1.3.1.post1/

---

## ¿Qué es esta Skill?

Esta skill convierte al agente Antigravity en un experto en **Kedro**, el framework open-source de Python para construir pipelines de datos reproducibles, mantenibles y modulares. El agente puede ayudarte a:

- Crear, depurar y extender proyectos Kedro desde cero
- Diseñar Data Catalogs para cualquier tipo de dataset (CSV, Parquet, SQLite, JSON, Pickle, etc.)
- Construir nodos y pipelines modulares siguiendo CRISP-DM
- Entrenar y evaluar modelos de clasificación, regresión y clustering
- Trabajar en Jupyter con integración Kedro nativa
- Desplegar con Docker Compose, Airflow, Databricks, Kubeflow y otros
- Aplicar testing, linting, logging y buenas prácticas MLOps

---

## Archivos de la Skill

| # | Archivo | Contenido |
|---|---------|-----------|
| 01 | `01_conceptos_core.md` | Nodo, Pipeline, Data Catalog, estructura de proyecto |
| 02 | `02_data_catalog.md` | catalog.yml completo, tipos de dataset, versioning, factories |
| 03 | `03_nodos_y_pipelines.md` | Definición, sintaxis, tags, merge, slicing, namespaces |
| 04 | `04_configuracion.md` | parameters.yml, credentials, OmegaConf, ConfigLoader |
| 05 | `05_crisp_dm_integrado.md` | 6 fases CRISP-DM mapeadas al flujo Kedro |
| 06 | `06_modelos_ml.md` | Clasificación, regresión, ensambles, evaluación, SHAP |
| 07 | `07_jupyter_notebooks.md` | kedro jupyter lab, %load_ext, secuencia de notebooks |
| 08 | `08_docker_y_despliegue.md` | Docker Compose, bootstrap_data.py, make verify |
| 09 | `09_extensiones_hooks.md` | Hooks, plugins custom, datasets custom, sesión programática |
| 10 | `10_analisis_datasets.md` | Análisis profundo para cualquier dataset tabular |
| 11 | `11_buenas_practicas.md` | .gitignore, reproducibilidad, versionado, seguridad |
| 12 | `12_plataformas_deploy.md` | Airflow, Databricks, Kubeflow, SageMaker, Prefect, etc. |
| 13 | `13_evaluaciones_scy1101.md` | Rúbricas y requisitos para EV Parcial 1 y 2 (SCY1101) |

---

## Comandos Kedro de Referencia Rápida

```bash
# Crear proyecto
kedro new

# Ejecutar pipeline completo
kedro run
python -m kedro run

# Ejecutar pipeline específico
kedro run --pipeline data_processing

# Ejecutar desde/hasta un nodo
kedro run --from-nodes "build_features_node"
kedro run --to-nodes "train_model_node"

# Jupyter con contexto Kedro
kedro jupyter lab
kedro jupyter notebook

# Visualizar grafo del pipeline
kedro viz

# Listar pipelines registrados
kedro pipeline list

# Listar datasets del catálogo
kedro catalog list

# Verificar datasets no resueltos
kedro catalog resolve

# Testing
pytest
make verify

# Empaquetar proyecto
kedro package
```

---

## Estructura de Proyecto Kedro (Completa)

```
mi-proyecto/
├── conf/
│   ├── base/
│   │   ├── catalog.yml          ← definición de datasets
│   │   ├── parameters.yml       ← hiperparámetros y configuración
│   │   ├── parameters_<pipeline>.yml
│   │   └── logging.yml
│   └── local/
│       └── credentials.yml      ← NO commitear (en .gitignore)
├── data/
│   ├── 01_raw/                  ← datos originales sin procesar
│   ├── 02_intermediate/         ← datos parcialmente transformados
│   ├── 03_primary/              ← datos listos para análisis
│   ├── 04_feature/              ← features de ML
│   ├── 05_model_input/          ← tabla analítica final (Parquet)
│   ├── 06_models/               ← modelos .pkl
│   ├── 07_model_output/         ← predicciones
│   └── 08_reporting/            ← métricas JSON, CSVs, figuras
├── docs/
│   └── guias/
├── notebooks/                   ← laboratorios Jupyter (01-08)
├── scripts/
│   └── bootstrap_data.py
├── src/
│   └── <nombre_proyecto>/
│       ├── __init__.py
│       ├── settings.py
│       ├── pipeline_registry.py
│       └── pipelines/
│           ├── data_processing/
│           │   ├── __init__.py
│           │   ├── nodes.py
│           │   └── pipeline.py
│           ├── ml_classification/
│           │   ├── nodes.py
│           │   └── pipeline.py
│           └── ml_regression/
│               ├── nodes.py
│               └── pipeline.py
├── tests/
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── Makefile
└── docker-compose.yml
```
