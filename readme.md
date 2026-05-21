# Análisis y Machine Learning — FIDE Chess Dataset (Kedro)

[![Powered by Kedro](https://img.shields.io/badge/powered_by-kedro-ffc900?logo=kedro)](https://docs.kedro.org)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/kenzodev1/analisis_y_machine_learning_dataset_fide/blob/main/analisis_y_machine_learning_dataset_fide.ipynb)

Este repositorio contiene un proyecto **Kedro** para analizar el dataset de ajedrez **FIDE**. El pipeline abarca:
- Ingesta de datos
- Limpieza de datos (límites externalizados a `conf/base/parameters.yml`)
- Transformación de datos y **feature engineering**
- Pipelines opcionales de machine learning (entrenamiento, evaluación, etc.)

El proyecto sigue la rúbrica SCY1101, con **Indicador 4** (sin valores hardcodeados) y **Indicador 5** (transformación parametrizada) implementados.

---

## 📊 Datasets

| Archivo | Descripción | Columnas |
|---------|-------------|----------|
| `players.csv` | Catálogo de jugadores FIDE (~433K) | `fide_id`, `name`, `federation`, `gender`, `title`, `yob` |
| `ratings_2019.csv` | Ratings mensuales 2019 (~4.7M) | `fide_id`, `year`, `month`, `rating_standard`, `rating_rapid`, `rating_blitz` |
| `ratings_2020.csv` | Ratings mensuales 2020 (~5.1M) | Ídem |
| `ratings_2021.csv` | Ratings mensuales 2021 (~1.7M) | Ídem |

---

## ⚙️ Pipelines

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

## 🚀 Instalación y Ejecución

Te recomendamos usar **uv** para gestionar el entorno virtual y las dependencias, ya que es mucho más rápido y maneja la versión de Python automáticamente.

### 1. Entrar a la carpeta del proyecto
```bash
cd analisis_y_machine_learning_dataset_fide
```

### 2. Instalar uv (Solo si no lo tienes en Linux/macOS)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### 3. Crear entorno e instalar dependencias
```bash
# Crear entorno virtual con Python 3.12 (uv lo descarga si es necesario)
uv venv --python 3.12 .venv

# Activar el entorno
source .venv/bin/activate

# Instalar dependencias
uv pip install -r requirements.txt
```

---

## 📚 Comandos útiles de Kedro

| Comando | Descripción |
|---|---|
| `kedro run` | Ejecuta el pipeline por defecto (todos los pasos en orden) |
| `kedro run --pipeline data_cleaning` | Ejecuta un pipeline específico |
| `kedro viz run` | Abre el DAG interactivo en tu navegador (en Linux Mint se abre solo) |
| `kedro viz run --no-browser` | Útil si estás en WSL para luego abrir `http://localhost:4141` en Windows |
| `kedro catalog list` | Muestra los datasets registrados en el catálogo |
| `kedro notebook` | Lanza Jupyter con el contexto de Kedro cargado |
| `kedro test` | Ejecuta la suite de pruebas del proyecto |

---

## 📓 Jupyter Notebooks

Ejecuta `kedro jupyter lab` para explorar los siguientes análisis interactivos:

| Notebook | Contenido |
|----------|-----------|
| `01_exploratory_analysis` | EDA completo: distribuciones, correlaciones, calidad de datos |
| `02_supervised_modeling` | Entrenamiento interactivo de modelos de clasificación |
| `03_model_evaluation` | Matrices de confusión, curvas ROC, comparación de modelos |
| `04_hyperparameter_optimization` | GridSearchCV paso a paso |
| `05_final_analysis` | Clustering, PCA y conclusiones finales |

---

## 📑 Evaluación SCY1101: Informe Técnico Completo

> [!IMPORTANT]
> **Aclaración para el Evaluador**
> 
> El **informe técnico completo** exigido por la rúbrica (incluyendo el marco metodológico, análisis experimental, optimización de hiperparámetros, resultados de clustering y la bibliografía/referencias) **no es un documento de texto estático separado** en este repositorio.
> 
> Este informe se genera **automáticamente en formato HTML** (`informe_modelos.html`) como resultado final de la ejecución de nuestro pipeline. Esto asegura que el reporte y sus justificaciones estén siempre sincronizados con el código y los modelos más recientes.

Para generar y visualizar este reporte, debe ejecutar el siguiente comando exacto:

```bash
kedro run --pipeline model_report
```

Una vez ejecutado, el documento resultante se encontrará en:
`data/08_reporting/informe_modelos.html`

---

## 📂 Estructura del proyecto

```text
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
