# Análisis y Machine Learning — FIDE Chess Dataset (Kedro)

[![Powered by Kedro](https://img.shields.io/badge/powered_by-kedro-ffc900?logo=kedro)](https://docs.kedro.org)

Proyecto de **ciencia de datos** para análisis, transformación y modelado del dataset de ajedrez de la FIDE (Fédération Internationale des Échecs), construido con [Kedro 1.3](https://docs.kedro.org). Cubre las competencias de las **Evaluaciones Parciales 1 y 2** de la asignatura SCY1101.

---

## Datasets

| Archivo | Descripción | Columnas |
|---------|-------------|----------|
| `players.csv` | Catálogo de jugadores FIDE (~433K) | `fide_id`, `name`, `federation`, `gender`, `title`, `yob` |
| `ratings_2019.csv` | Ratings mensuales 2019 (~4.7M) | `fide_id`, `year`, `month`, `rating_standard`, `rating_rapid`, `rating_blitz` |
| `ratings_2020.csv` | Ratings mensuales 2020 (~5.1M) | Ídem |
| `ratings_2021.csv` | Ratings mensuales 2021 (~1.7M) | Ídem |

---

## Pipelines

### Evaluación 1 — Transformación y Calidad de Datos

| Pipeline | Descripción |
|----------|-------------|
| `data_ingestion` | Carga los 4 CSV, estandariza columnas, genera reporte de diagnóstico |
| `data_cleaning` | Manejo de nulos, duplicados, tipos mixtos, outliers (IQR) |
| `data_transform` | Joins, groupby, pivot_table, feature engineering, normalización |
| `data_validation` | Verificación de integridad, validación de esquemas, reporte final |

### Evaluación 2 — Machine Learning

| Pipeline | Descripción |
|----------|-------------|
| `model_training` | Entrenamiento de modelos supervisados (RF, LR, SVM, KNN) |
| `model_evaluation` | Validación cruzada, métricas (Accuracy, F1, ROC-AUC) |
| `hyperparameter_tuning` | Optimización con GridSearchCV |
| `unsupervised_learning` | K-Means, PCA, Silhouette Score |

---

## Instalación

```bash
# Crear entorno virtual con Python 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate

# Instalar dependencias
uv pip install -r requirements.txt

# O con pip estándar
pip install -e .
```

## Ejecución

```bash
# Ejecutar todos los pipelines
kedro run

# Ejecutar un pipeline específico
kedro run --pipeline data_ingestion

# Visualizar el DAG de pipelines (desde WSL)
kedro viz run --no-browser
# Luego abrir http://127.0.0.1:4141 en el navegador de Windows
```

## Jupyter Notebooks

```bash
kedro jupyter lab
```

| Notebook | Contenido |
|----------|-----------|
| `01_exploratory_analysis` | EDA completo: distribuciones, correlaciones, calidad de datos |
| `02_supervised_modeling` | Entrenamiento interactivo de modelos de clasificación |
| `03_model_evaluation` | Matrices de confusión, curvas ROC, comparación de modelos |
| `04_hyperparameter_optimization` | GridSearchCV paso a paso |
| `05_final_analysis` | Clustering, PCA y conclusiones finales |

---

## Estructura del proyecto

```
├── conf/base/          # Configuración (catalog.yml, parameters.yml)
├── data/01_raw/        # Datos crudos (CSV)
├── data/02_intermediate/ # Datos tras ingesta y limpieza
├── data/03_primary/    # Dataset integrado
├── data/06_models/     # Modelos entrenados (.pkl)
├── data/08_reporting/  # Reportes y métricas (JSON)
├── notebooks/          # Jupyter Notebooks
├── src/analisis_fide_chess/pipelines/  # Código modular de pipelines
└── pyproject.toml      # Configuración del proyecto
```
