# Docker y Despliegue Local
> Fuente: Desarrollo Docker.txt

---

## 1. Obtener Datos del Proyecto

### Opción A — Git LFS (datos versionados con el repo)

```bash
# Si el repo usa Git LFS y falta el archivo de datos:
git lfs pull
```

### Opción B — Script bootstrap_data.py (recomendado)

```bash
# Modo automático (intenta descarga → fallback a sintético)
python scripts/bootstrap_data.py

# Solo datos sintéticos mínimos (sin red, para CI/CD, Docker)
python scripts/bootstrap_data.py --source minimal --force

# Solo descarga (error si no hay red)
python scripts/bootstrap_data.py --source download --force
```

**¿Qué hace el bootstrap?**
1. Intenta descargar la base pública desde Hugging Face (u otra fuente)
2. Si la red falla → genera un SQLite mínimo sintético con las tablas necesarias
3. El SQLite mínimo tiene las tablas del catálogo, suficiente para `kedro run` y notebooks

### Opción C — Kaggle u otra fuente

```bash
# Copiar archivo descargado manualmente
cp ~/Descargas/database.sqlite data/raw/database.sqlite
# El proyecto espera el esquema estándar
```

---

## 2. Probar el Pipeline en Local

### Con Makefile (recomendado)

```bash
# Instalar dependencias de desarrollo primero
pip install -e ".[dev]"
# o con uv:
uv sync --extra dev

# Ejecutar suite completa de verificación:
# format (Ruff) + lint + bootstrap mínimo + pytest + kedro run
make verify

# Ver todos los objetivos disponibles
make help

# Solo ejecutar notebooks en memoria (sin guardar)
make verify-notebooks
```

### Pasos manuales equivalentes

```bash
# 1. Sincronizar dependencias
uv sync --extra dev

# 2. Generar datos (modo auto: intenta HF, fallback sintético)
python scripts/bootstrap_data.py

# 3. Ejecutar el pipeline completo
kedro run

# 4. Ejecutar tests
pytest -q

# 5. Verificar artefactos generados
ls data/05_model_input/features_for_ml.parquet
ls data/08_reporting/classification_metrics.json
ls data/08_reporting/regression_metrics.json
ls data/06_models/*.pkl
```

---

## 3. Docker Compose — Entornos Reproducibles

### Requisitos

```bash
# Docker Engine en ejecución
docker --version
docker compose version

# Si ves: "Cannot connect to the Docker daemon"
# → Iniciar el servicio de Docker primero
sudo systemctl start docker      # Linux systemd
# o abrir Docker Desktop (Windows/Mac)
```

### Construir imagen

```bash
docker compose build
# Equivalente según instalación:
docker-compose build
```

### Servicios disponibles

```bash
# Pipeline completo (intenta descarga → fallback sintético)
docker compose run --rm pipeline

# Solo datos sintéticos + pipeline (sin depender de red externa)
docker compose run --rm pipeline-minimal

# Tests en contenedor aislado (volumen separado)
docker compose run --rm test

# JupyterLab con extensión Kedro
docker compose --profile lab up jupyter
# → Abrir: http://localhost:8888  (ver token en logs del contenedor)

# Kedro Viz — grafo interactivo del pipeline
docker compose --profile viz up kedro-viz
# → Abrir: http://localhost:4141
```

---

## 4. Volúmenes Docker

| Volumen | Propósito |
|---------|-----------|
| `project_data` | Datos persistentes (data/raw/ + salidas Kedro) |
| `project_test_data` | Datos aislados para tests — no contamina datos de clase |

```bash
# Resetear datos de la demo (eliminar volumen)
docker volume rm mi-proyecto_project_data

# Los servicios pipeline-minimal, jupyter y kedro-viz NO usan --force
# → No reemplazan datos existentes válidos automáticamente
```

---

## 5. Estructura del docker-compose.yml

```yaml
# docker-compose.yml (estructura típica de proyecto Kedro)
version: "3.9"

services:
  pipeline:
    build: .
    volumes:
      - project_data:/app/data
    command: >
      sh -c "python scripts/bootstrap_data.py &&
             kedro run"

  pipeline-minimal:
    build: .
    volumes:
      - project_data:/app/data
    command: >
      sh -c "python scripts/bootstrap_data.py --source minimal &&
             kedro run"

  test:
    build: .
    volumes:
      - project_test_data:/app/data
    command: >
      sh -c "python scripts/bootstrap_data.py --source minimal --force &&
             pytest -q"

  jupyter:
    profiles: ["lab"]
    build: .
    ports:
      - "8888:8888"
    volumes:
      - project_data:/app/data
      - ./notebooks:/app/notebooks
    command: kedro jupyter lab --ip=0.0.0.0 --no-browser --allow-root

  kedro-viz:
    profiles: ["viz"]
    build: .
    ports:
      - "4141:4141"
    command: kedro viz --host 0.0.0.0

volumes:
  project_data:
  project_test_data:
```

---

## 6. Dockerfile Típico

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Copiar código fuente
COPY src/ ./src/
COPY conf/ ./conf/
COPY scripts/ ./scripts/
COPY notebooks/ ./notebooks/
COPY Makefile ./

# Crear directorios de datos
RUN mkdir -p data/01_raw data/02_intermediate data/03_primary \
    data/04_feature data/05_model_input data/06_models \
    data/07_model_output data/08_reporting

CMD ["kedro", "run"]
```

---

## 7. Limitaciones de los Datos Sintéticos

| Aspecto | Base sintética | Base completa |
|---------|---------------|--------------|
| Tabla principal | ✅ Poblada (Bootstrap) | ✅ Poblada (original) |
| Tablas secundarias | ⚠️ Vacías | ✅ Completas |
| Para `kedro run` | ✅ Funciona | ✅ Funciona |
| Para notebooks 01-06 | ✅ Funciona | ✅ Funciona |
| Para análisis realista | ❌ Limitado | ✅ Ideal |
| Para CI/CD | ✅ Ideal | ❌ Demasiado grande |

---

## 8. Pipelines Kedro Registrados

Orden de ejecución por defecto en `kedro run`:
1. `data_processing` → genera `features_for_ml` (Parquet)
2. `ml_classification` → genera métricas, modelo .pkl, importancias CSV
3. `ml_regression` → igual para tarea de regresión

```bash
# Ejecutar solo un pipeline
kedro run --pipeline data_processing
kedro run --pipeline ml_classification
kedro run --pipeline ml_regression

# Listar pipelines registrados
kedro pipeline list

# Ver el grafo visual
kedro viz
```
