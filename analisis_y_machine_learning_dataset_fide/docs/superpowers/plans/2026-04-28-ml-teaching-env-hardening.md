# ML Teaching Environment Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Leave the repository reproducible for class delivery with `uv`, Docker, Jupyter, Kedro Viz, SQLite validation, robust Kedro pipelines, verified notebooks, and ML teaching labs.

**Architecture:** Keep Kedro as the project pipeline and sklearn `Pipeline` inside model notebooks. Use `uv.lock` as the reproducible Python source, Docker volumes separated by purpose, and notebook execution as a verification target.

**Tech Stack:** Python, uv, Kedro, Kedro Viz, Jupyter, scikit-learn, pandas, Docker Compose, pytest, nbclient.

---

### Task 1: Dependency And Runtime Reproducibility

**Files:**
- Modify: `pyproject.toml`
- Modify: `requirements.txt`
- Create: `uv.lock`
- Modify: `Dockerfile`
- Modify: `Makefile`

- [x] Add `kedro-viz`, `nbconvert`, and `ipykernel` with `uv add`.
- [x] Keep `requirements.txt` aligned for users who cannot use `uv`.
- [x] Install dependencies in Docker with `uv pip install --system`.
- [x] Add `make sync` and `make verify-notebooks`.

### Task 2: Data And Model Robustness

**Files:**
- Modify: `scripts/bootstrap_data.py`
- Modify: `src/analisis_equipos_de_football/pipelines/data_processing/nodes.py`
- Modify: `src/analisis_equipos_de_football/pipelines/ml_classification/nodes.py`
- Create: `tests/test_data_and_model_robustness.py`

- [x] Add SQLite integrity/schema validation before reusing an existing DB.
- [x] Drop rows with missing goals before deriving labels.
- [x] Make KNN safe for small training splits.
- [x] Make classification reports safe when a class is absent.
- [x] Add regression tests for all four cases.

### Task 3: Docker, Volumes, Jupyter, Kedro Viz

**Files:**
- Modify: `docker-compose.yml`
- Modify: `docs/DESARROLLO_Y_DOCKER.md`

- [x] Separate `football_data` from `football_test_data`.
- [x] Avoid `--force` for class/demo services.
- [x] Keep forced regeneration only in the isolated test volume.
- [x] Add `--allow-root` for containerized Jupyter.
- [x] Add a `kedro-viz` service on port `4141`.

### Task 4: Notebook Curriculum And Verification

**Files:**
- Modify: `notebooks/*.ipynb`
- Create: `notebooks/07_validacion_cruzada_hiperparametros.ipynb`
- Create: `notebooks/08_no_supervisado_clustering.ipynb`
- Create: `scripts/verify_notebooks.py`
- Modify: `notebooks/README.md`

- [x] Clear stale notebook outputs.
- [x] Add a common preflight cell for project root and SQLite existence.
- [x] Add cross-validation and hyperparameter search lab.
- [x] Add unsupervised PCA/K-Means lab.
- [x] Add notebook execution script.

### Task 5: Final Verification And Upload

**Files:**
- All changed files

- [ ] Run `ruff format src tests scripts`.
- [ ] Run `ruff check src tests scripts`.
- [ ] Run `python -m pytest tests/ -q --tb=short`.
- [ ] Run `python -m kedro run`.
- [ ] Run `python scripts/verify_notebooks.py`.
- [ ] Run `docker-compose config` and `docker-compose --profile lab --profile viz config`.
- [ ] Review `git diff`.
- [ ] Commit and push the branch after all checks pass.
