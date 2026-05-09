# Plataformas de Despliegue Kedro
> Fuente: https://docs.kedro.org/en/1.3.1.post1/deploy/

---

## Resumen de Plataformas Soportadas

| Plataforma | Caso de uso | Tipo |
|-----------|------------|------|
| Apache Airflow | Orquestación en producción | On-premise / Cloud |
| Databricks | Big Data con Spark | Cloud |
| Kubeflow Pipelines | ML en Kubernetes | Cloud / On-premise |
| Amazon SageMaker | MLOps en AWS | Cloud AWS |
| AWS Step Functions | Orquestación serverless AWS | Cloud AWS |
| Amazon EMR Serverless | Spark serverless | Cloud AWS |
| Azure ML Pipelines | MLOps en Azure | Cloud Azure |
| VertexAI | MLOps en GCP | Cloud GCP |
| Prefect | Orquestación moderna | Cloud / On-premise |
| Dagster | Pipeline observability | Cloud / On-premise |
| Dask | Computación paralela local | Local / Cluster |
| Argo Workflows | K8s nativo | Kubernetes |
| AWS Batch | Jobs en lote | Cloud AWS |

---

## Apache Airflow

```bash
# Instalar plugin
pip install kedro-airflow
```

```python
# Genera DAGs de Airflow desde el pipeline Kedro
# kedro-airflow convierte automáticamente cada nodo en un AirflowOperator

# En el directorio del proyecto:
kedro airflow create        # genera DAG en dags/
kedro airflow convert       # convierte pipeline a DAG

# Ejemplo de DAG generado:
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG("kedro_pipeline", start_date=datetime(2024, 1, 1), schedule="@daily") as dag:
    preprocess = PythonOperator(task_id="preprocess_node", python_callable=run_node_preprocess)
    train = PythonOperator(task_id="train_node", python_callable=run_node_train)
    preprocess >> train
```

### Configuración recomendada

```yaml
# conf/base/airflow.yml
default_args:
  owner: "data-team"
  retries: 1
  retry_delay_minutes: 5
schedule_interval: "@daily"
catchup: false
```

---

## Databricks

```bash
pip install kedro-databricks
```

```python
# Configurar el workspace
# conf/local/credentials.yml
databricks:
  host: "https://mi-workspace.azuredatabricks.net"
  token: "${oc.env:DATABRICKS_TOKEN}"

# Ejecutar pipeline en Databricks
kedro databricks run --cluster-id "cluster-abc123"
```

### Consideraciones para Spark

```python
# nodes.py — compatibilidad con Spark
from pyspark.sql import DataFrame as SparkDF
import pandas as pd

def process_with_spark(data: SparkDF, params: dict) -> SparkDF:
    """Nodo que opera sobre Spark DataFrame."""
    return data.filter(data["columna"] > params["threshold"])

# catalog.yml — dataset Spark
mi_tabla_spark:
  type: spark.SparkDataset
  filepath: s3://mi-bucket/datos/
  file_format: parquet
  load_args:
    header: true
    inferSchema: true
```

---

## Kubeflow Pipelines

```bash
pip install kedro-kubeflow
```

```bash
# Compilar pipeline a formato Kubeflow
kedro kubeflow compile

# Desplegar en el clúster
kedro kubeflow upload-pipeline

# Ejecutar desde CLI
kedro kubeflow run-once
```

```python
# Cada nodo Kedro se convierte en un componente Kubeflow
# Los datasets pasan a través de volúmenes o object storage (GCS/S3)
```

---

## Amazon SageMaker

```bash
pip install kedro-sagemaker
```

```python
# conf/local/credentials.yml
aws:
  aws_access_key_id: "${oc.env:AWS_ACCESS_KEY_ID}"
  aws_secret_access_key: "${oc.env:AWS_SECRET_ACCESS_KEY}"
  region_name: "us-east-1"

# conf/base/sagemaker.yml
pipeline_name: "mi-kedro-pipeline"
role_arn: "arn:aws:iam::123456789:role/SageMakerRole"
instance_type: "ml.m5.large"
s3_bucket: "mi-bucket-ml"
```

```bash
# Desplegar y ejecutar
kedro sagemaker run
```

---

## Prefect

```bash
pip install kedro-prefect
```

```python
# Convierte el pipeline Kedro en un Flow de Prefect
from prefect import flow
from kedro.framework.session import KedroSession

@flow(name="kedro-ml-pipeline")
def run_kedro_pipeline():
    with KedroSession.create(project_path=".") as session:
        session.run()

# Ejecutar localmente
if __name__ == "__main__":
    run_kedro_pipeline()

# Desplegar en Prefect Cloud
prefect deployment build run_pipeline.py:run_kedro_pipeline \
    --name "produccion" --cron "0 6 * * *"
```

---

## Empaquetado del Proyecto

```bash
# Empaquetar como wheel de Python
kedro package

# Genera: dist/mi_proyecto-0.1.0-py3-none-any.whl

# Instalar en otro entorno
pip install dist/mi_proyecto-0.1.0-py3-none-any.whl

# Ejecutar pipeline instalado
python -m kedro run
```

---

## Despliegue en Máquina Única (Single Machine)

```bash
# Ejecución directa (sin Docker)
cd /ruta/al/proyecto
source .venv/bin/activate
python -m kedro run

# Con diferentes configuraciones (entornos)
KEDRO_ENV=staging kedro run
KEDRO_ENV=production kedro run

# Programar con cron (Linux)
# Editar crontab:
crontab -e
# Añadir:
# 0 6 * * * /ruta/.venv/bin/python -m kedro run >> /logs/kedro_$(date +\%Y\%m\%d).log 2>&1
```

---

## Agrupación de Nodos (Node Grouping)

Para optimizar el despliegue distribuido:

```python
# Agrupar nodos costosos en el mismo worker
node(func=heavy_computation, inputs="data", outputs="result", tags=["gpu"]),

# Ejecutar solo nodos con tag "gpu" en máquinas GPU
kedro run --tags gpu

# Asignar recursos por tag en plataformas cloud
# (configurado en el plugin específico: kedro-sagemaker, kedro-kubeflow, etc.)
```

---

## CI/CD con GitHub Actions

```yaml
# .github/workflows/kedro_ci.yml
name: Kedro CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Lint
        run: ruff check src/ tests/

      - name: Test
        run: pytest tests/ -q --cov=src/

      - name: Run pipeline (datos sintéticos)
        run: |
          python scripts/bootstrap_data.py --source minimal --force
          kedro run

      - name: Verify artifacts
        run: |
          test -f data/05_model_input/features_for_ml.parquet
          test -f data/08_reporting/classification_metrics.json
```

---

## Distribución de Configuración por Entorno

```
conf/
├── base/              ← compartida, versionada en Git
│   ├── catalog.yml
│   ├── parameters.yml
│   └── logging.yml
├── local/             ← personal, gitignoreada
│   └── credentials.yml
├── staging/           ← entorno de staging
│   └── parameters.yml (sobreescribe base)
└── production/        ← entorno de producción
    ├── parameters.yml
    └── catalog.yml    (rutas S3 en lugar de local)
```

```bash
# Ejecutar con configuración de producción
KEDRO_ENV=production kedro run
```
