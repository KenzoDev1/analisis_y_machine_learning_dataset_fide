# Guía para estudiantes: cómo ejecutar y probar el proyecto

Esta guía es el **punto de entrada** para trabajar en el laboratorio. Sigue los pasos en orden la primera vez; después solo necesitas activar el entorno y, si hace falta, regenerar datos.

---

## 1. Qué incluye este proyecto

- **Datos:** partidos de fútbol en SQLite (`Match`, `League`, etc.). En clase usamos sobre todo cuotas **Bet365** y goles para clasificación (resultado) y regresión (goles del local).
- **Notebooks (Jupyter):** exploración paso a paso alineada con **CRISP-DM**.
- **Kedro:** mismo flujo de datos y modelos de forma **reproducible** desde la terminal (`kedro run`).
- **Pruebas:** `pytest` y `make verify` comprueban que el pipeline funciona.

---

## 2. Requisitos en tu computador

| Requisito | Versión / nota |
|-----------|----------------|
| **Python** | 3.10 o superior (recomendado 3.11) |
| **uv** | Recomendado para instalar exactamente lo definido en `uv.lock` |
| **Git** | Opcional, para clonar el repositorio |
| **Git LFS** | Recomendado si quieres recibir la base SQLite completa incluida para la clase |
| **Espacio** | ~500 MB si descargas la base completa; la base **mínima** sintética es mucho más pequeña |

No hace falta instalar SQLite a mano: Python ya trae el módulo `sqlite3`.

---

## 3. Primera instalación (solo una vez)

Abre una terminal en la **carpeta raíz del proyecto** (donde está `pyproject.toml` y la carpeta `src/`).

### 3.1 Entorno virtual (recomendado)

Evita mezclar librerías con otros proyectos.

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell o CMD):**

```bat
python -m venv .venv
.venv\Scripts\activate
```

Deberías ver `(.venv)` al inicio de la línea en la terminal.

### 3.2 Instalar dependencias con `uv` (recomendado)

```bash
python -m pip install --upgrade pip uv
uv sync --extra dev
```

Esto crea/actualiza `.venv` y deja instaladas las dependencias necesarias para notebooks, Kedro, Kedro Viz y pruebas.

Alternativa con `pip` si no puedes usar `uv`:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
```

Opcional (gráficos SHAP en algunos notebooks):

```bash
uv sync --extra dev --extra explain
```

### 3.3 Crear o traer la base de datos local

Para esta clase, **`data/raw/database.sqlite`** está trackeado con **Git LFS**. Si clonaste el repo y el archivo no se descargó completo, ejecuta:

```bash
git lfs pull
```

Si no tienes Git LFS o quieres regenerar una base local:

```bash
python scripts/bootstrap_data.py
```

- Con **internet**, intenta bajar la base pública (réplica del *European Soccer Database*).
- Si falla la red, genera una base **sintética mínima** (suficiente para prácticas y para `kedro run`).

Para forzar solo la sintética:

```bash
python scripts/bootstrap_data.py --source minimal --force
```

### 3.4 Comprobar que “todo corre”

**Importante:** ejecuta estos comandos con el **mismo Python** donde instalaste el proyecto (entorno virtual activo o `uv run …`). Si usas el Python del sistema sin `pyarrow`, `kedro run` fallará al guardar Parquet; el script `scripts/check_runtime_deps.py` (lo invoca `make verify`) te lo indica antes con un mensaje claro.

Desde la raíz del proyecto:

```bash
make verify
```

Esto ejecuta: formato/lint (Ruff), bootstrap mínimo de SQLite si aplica, **comprobación de dependencias** (`pyarrow`, sklearn, Kedro…), **pytest** y **`kedro run`**. Si termina sin errores, tu entorno está bien configurado.

**Ensayo completo antes de una clase (recomendado para el docente):** incluye además la ejecución de los 9 notebooks en memoria (~3 minutos o más según máquina):

```bash
make verify-all
```

Si tienes `make`, puedes ver todos los comandos del proyecto con `make help`.

Con **uv** sin activar el venv manualmente:

```bash
uv run make verify
uv run make verify-all
```

Si no tienes `make` instalado (algunos Windows), ejecuta manualmente:

```bash
python scripts/check_runtime_deps.py
python scripts/bootstrap_data.py --source minimal --force
pytest -q
python -m kedro run
```

Para comprobar que los notebooks corren de principio a fin:

```bash
make verify-notebooks
```

---

## 4. Trabajar con Jupyter (notebooks)

**Siempre** inicia Jupyter **desde la raíz del proyecto** para que Kedro encuentre `conf/` y los datos.

```bash
# Con el entorno virtual activado
kedro jupyter lab
```

O:

```bash
kedro jupyter notebook
```

En la primera celda de los notebooks suele aparecer:

```python
%load_ext kedro.ipython
```

Eso carga `catalog`, `context`, etc.

### Orden sugerido de notebooks

| Orden | Archivo | Qué haces ahí |
|-------|---------|----------------|
| 1 | `01_comprension_negocio_y_datos.ipynb` | Entender el problema y explorar tablas |
| 2 | `02_preparacion_datos.ipynb` | Construir la tabla de modelado |
| 3 | `03_clasificacion_resultado.ipynb` | Modelos de clasificación y métricas |
| 4 | `04_regresion_goles.ipynb` | Regresión y errores |
| 5 | `05_explicabilidad_evaluacion.ipynb` | Importancia de variables, SHAP opcional |
| 6 | `06_pipeline_Kedro.ipynb` | Lanzar el pipeline completo desde el notebook |
| 7 | `07_validacion_cruzada_hiperparametros.ipynb` | KFold, cross validation y búsqueda de hiperparámetros |
| 8 | `08_no_supervisado_clustering.ipynb` | PCA, K-Means y evaluación no supervisada |

**Atajo:** `Exploracion_de_datos.ipynb` concentra varias etapas en un solo archivo (repaso o demo rápida).

Más detalle: [notebooks/README.md](../notebooks/README.md).

---

## 5. Pipeline Kedro desde la terminal

Con la base ya creada:

```bash
python -m kedro run
```

Etapas (en orden):

1. **data_processing** → genera `data/05_model_input/features_for_ml.parquet`
2. **ml_classification** → métricas JSON, modelo `.pkl`, CSV de importancias
3. **ml_regression** → lo mismo para regresión

Solo una parte:

```bash
python -m kedro run --pipeline data_processing
```

Parámetros editables (columnas, fracción test): `conf/base/parameters.yml`.  
Catálogo de datasets: `conf/base/catalog.yml`.

---

## 6. Estructura útil del repositorio

```
├── conf/base/           # Parámetros y catálogo Kedro
├── data/raw/            # database.sqlite (la generas tú)
├── data/05_model_input/ # Tabla lista para modelar (Parquet)
├── data/06_models/      # Modelos entrenados (.pkl)
├── data/08_reporting/   # Métricas JSON, CSV de importancias
├── docs/guias/          # CRISP-DM, modelos, flujo integrado
├── notebooks/           # Laboratorios 01–06
├── scripts/             # bootstrap_data.py (crear SQLite)
├── src/.../pipelines/   # Nodos Kedro (código Python del pipeline)
└── tests/               # Pruebas automáticas
```

---

## 7. Problemas frecuentes

| Síntoma | Qué probar |
|---------|------------|
| `no such table` o error al cargar `match` | Ejecuta `python scripts/bootstrap_data.py` |
| `kedro: command not found` | Activa el `.venv` y `pip install -r requirements.txt` |
| `No module named 'analisis_fide_chess'` | Desde la raíz: `pip install -e .` |
| Jupyter no ve el `catalog` | Abre Jupyter con `kedro jupyter lab` desde la **raíz** del repo |
| Quiero ver el flujo visual de Kedro | Ejecuta `kedro viz` o `docker compose --profile viz up kedro-viz` |
| Notebooks 01–02 bien pero tablas de jugadores vacías | Normal con la base **sintética**; para datos reales usa descarga completa |
| `make: command not found` | Instala `make` o usa los comandos manuales del apartado 3.4 |

---

## 8. Dónde está la teoría y el guion del curso

| Documento | Contenido |
|-------------|-----------|
| [crispdm_y_machine_learning.md](guias/crispdm_y_machine_learning.md) | Fases CRISP-DM, métricas, enlace con el repo |
| [modelos_y_flujo_integrado.md](guias/modelos_y_flujo_integrado.md) | Explicación de algoritmos, diagramas, FAQ |
| [DESARROLLO_Y_DOCKER.md](DESARROLLO_Y_DOCKER.md) | Docker, bootstrap avanzado, CI |

---

## 9. Buenas prácticas para entregas

- No subas **`database.sqlite`** ni credenciales a Git (ya están ignorados).
- Documenta en tu informe **qué hiciste en cada fase CRISP-DM** y qué decisiones tomaste (features, métrica, split).
- Si cambias `parameters.yml`, indícalo en el README de tu entrega o en el informe.

Si algo no cuadra con esta guía, avisa al docente con **captura del error completo** y el comando que ejecutaste.
