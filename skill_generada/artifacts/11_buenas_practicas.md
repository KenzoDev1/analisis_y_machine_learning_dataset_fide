# Buenas Prácticas en Proyectos Kedro
> Fuente: Readme Ejemplo.txt + Documentacion Teorica 1.txt

---

## .gitignore — Qué NO Commitear

```gitignore
# ── Datos (nunca commitear datos sensibles o grandes) ─────────────
data/01_raw/
data/02_intermediate/
data/03_primary/
data/04_feature/
data/05_model_input/
data/06_models/
data/07_model_output/
data/08_reporting/
!data/.gitkeep
!data/*/.gitkeep

# ── Credenciales (CRÍTICO: nunca commitear) ───────────────────────
conf/local/
!conf/local/.gitkeep

# ── Entornos virtuales ────────────────────────────────────────────
.venv/
venv/
env/
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# ── Notebooks (outputs) ───────────────────────────────────────────
# Considerar: nbstripout para limpiar outputs antes de commitear
.ipynb_checkpoints/

# ── IDEs ──────────────────────────────────────────────────────────
.vscode/
.idea/
*.swp

# ── Kedro ─────────────────────────────────────────────────────────
.kedro/
```

---

## Gestión de Dependencias

### pyproject.toml (recomendado)

```toml
[project]
name = "mi-proyecto-kedro"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
    "kedro>=1.3.0",
    "kedro-datasets[pandas,pickle,json,matplotlib]>=3.0.0",
    "scikit-learn>=1.4",
    "pandas>=2.0",
    "numpy>=1.26",
    "pyarrow>=14.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "ruff>=0.3",
    "ipykernel",
    "kedro-viz",
    "nbstripout",
]
explain = [
    "shap>=0.44",
    "matplotlib>=3.7",
    "seaborn>=0.13",
]
docker = [
    "jupyter>=1.0",
]

[project.entry-points."kedro.hooks"]

[tool.kedro]
package_name = "mi_proyecto"
project_name = "Mi Proyecto Kedro"
kedro_init_version = "1.3.0"
tools = "['Linting', 'Testing', 'Custom Logging', 'Documentation', 'Data Structure']"
example_pipeline = "False"
source_dir = "src"
```

### requirements.txt (alternativa)

```text
kedro>=1.3.0
kedro-datasets[pandas,pickle,json,matplotlib]>=3.0.0
scikit-learn>=1.4
pandas>=2.0
numpy>=1.26
pyarrow>=14.0
```

---

## Makefile — Automatización de Tareas

```makefile
.PHONY: help verify verify-notebooks install format lint test run clean

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Instala dependencias de desarrollo
	pip install -e ".[dev]"

format:  ## Formatea código con Ruff
	ruff format src/ tests/

lint:  ## Linting con Ruff
	ruff check src/ tests/

test:  ## Ejecuta tests con pytest
	pytest tests/ -q --cov=src/

run:  ## Ejecuta el pipeline completo
	python scripts/bootstrap_data.py --source minimal
	kedro run

verify: format lint test run  ## Suite completa de verificación

verify-notebooks:  ## Ejecuta notebooks en memoria (sin guardar)
	jupyter nbconvert --to notebook --execute notebooks/*.ipynb \
		--ExecutePreprocessor.timeout=600 --output-dir /tmp/

clean:  ## Limpia artefactos generados
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/ .coverage
```

---

## Principios de Reproducibilidad

### ✅ DO — Buenas prácticas

```python
# 1. Semillas aleatorias fijas
train_test_split(..., random_state=42)
RandomForestClassifier(..., random_state=42)

# 2. Funciones puras en nodos (sin efectos secundarios)
def build_features(data: pd.DataFrame) -> pd.DataFrame:
    return data.assign(nueva_feature=data["a"] / data["b"])

# 3. Logging descriptivo
import logging
logger = logging.getLogger(__name__)
logger.info(f"Dataset procesado: {df.shape}")

# 4. Tipos anotados en funciones
def split_data(
    data: pd.DataFrame,
    test_size: float,
    random_state: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    ...

# 5. Parámetros en YAML, no hardcodeados
# ❌ Mal:  test_size = 0.2
# ✅ Bien: inputs=["data", "params:test_size"]

# 6. Versionar modelos
# catalog.yml: versioned: true
```

### ❌ DON'T — Antipatrones

```python
# ❌ No usar variables globales en nodos
global_state = {}
def bad_node(data):
    global_state["data"] = data  # ← efecto secundario

# ❌ No hardcodear rutas de archivos
df = pd.read_csv("/home/usuario/datos.csv")  # ← no reproducible

# ❌ No commitear datos sensibles
git add data/raw/database.sqlite  # ← NUNCA

# ❌ No usar print() en producción — usar logger
print("Procesando...")  # ← usar logger.info()

# ❌ No mezclar exploración y producción
# El notebook es para explorar; el pipeline para producir

# ❌ No olvidar el reset_index después de filtrar
df = df[df["col"] > 0]  # ← el índice puede quedar discontinuo
df = df.reset_index(drop=True)  # ← siempre
```

---

## Logging Configurado (logging.yml)

```yaml
# conf/base/logging.yml
version: 1
disable_existing_loggers: false

formatters:
  simple:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  colored:
    (): colorlog.ColoredFormatter
    format: "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s - %(message)s"

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: simple
    stream: ext://sys.stdout

  file:
    class: logging.FileHandler
    level: DEBUG
    formatter: simple
    filename: logs/kedro_run.log
    mode: a

loggers:
  kedro:
    level: INFO
    handlers: [console]
    propagate: false

  mi_proyecto:
    level: DEBUG
    handlers: [console, file]
    propagate: false

root:
  level: WARNING
  handlers: [console]
```

---

## Testing de Pipelines

```python
# tests/pipelines/test_data_processing.py
import pytest
import pandas as pd
from src.mi_proyecto.pipelines.data_processing.nodes import (
    preprocess_data, build_ml_features_table
)


@pytest.fixture
def sample_data():
    """Datos de prueba mínimos."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4, 5],
        "feature_1": [0.5, 1.2, None, 0.8, 2.1],
        "feature_2": [10, 20, 30, 40, 50],
        "target": ["A", "B", "A", "B", "A"],
    })


def test_preprocess_removes_nulls(sample_data):
    result = preprocess_data(sample_data, key_columns=["id"], date_columns=[])
    assert result.isnull().sum().sum() == 0


def test_preprocess_removes_duplicates():
    data = pd.DataFrame({"id": [1, 1, 2], "val": [1, 1, 2]})
    result = preprocess_data(data, key_columns=["id"], date_columns=[])
    assert len(result) == 2


def test_build_features_selects_correct_columns(sample_data):
    result = build_ml_features_table(
        sample_data.dropna(),
        target_column="target",
        feature_columns=["feature_1", "feature_2"],
        test_size=0.2,
        random_state=42,
    )
    X_train, X_test, y_train, y_test = result
    assert "target" not in X_train.columns
    assert "feature_1" in X_train.columns


def test_split_proportions(sample_data):
    data = pd.DataFrame({
        "feature_1": range(100),
        "feature_2": range(100),
        "target": ["A"] * 50 + ["B"] * 50,
    })
    X_train, X_test, y_train, y_test = build_ml_features_table(
        data, "target", ["feature_1", "feature_2"], 0.2, 42
    )
    assert len(X_test) == pytest.approx(20, abs=2)
```

---

## Seguridad — Checklist

- [ ] `conf/local/` está en `.gitignore`
- [ ] No hay contraseñas hardcodeadas en `catalog.yml` (usar `credentials:`)
- [ ] La base de datos de datos no está en el repositorio (`.gitignore` en `data/`)
- [ ] Los tokens de API están en variables de entorno o `conf/local/credentials.yml`
- [ ] El `pyproject.toml` fija versiones mínimas de dependencias (no `latest`)
- [ ] Los notebooks tienen outputs borrados antes del commit (`nbstripout`)
- [ ] Los modelos versioned en `catalog.yml` no se commitean
