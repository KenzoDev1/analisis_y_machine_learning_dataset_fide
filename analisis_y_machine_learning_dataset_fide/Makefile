.PHONY: help sync verify verify-all verify-notebooks format lint test kedro-run bootstrap-minimal kedro-viz check-runtime

help:
	@echo "Objetivos útiles:"
	@echo "  make sync            - instalar dependencias con uv"
	@echo "  make check-runtime   - comprobar pyarrow/sklearn/kedro en el Python activo"
	@echo "  make verify          - format, lint, SQLite mínima, check-runtime, pytest, kedro run"
	@echo "  make verify-all      - verify + ejecutar todos los notebooks (ensayo pre-clase)"
	@echo "  make verify-notebooks - solo notebooks en memoria con nbclient"
	@echo "  make test / lint / format / kedro-run / bootstrap-minimal - piezas sueltas"
	@echo "Documentación: docs/GUIA_ESTUDIANTES.md y docs/README.md"

sync:
	uv sync --extra dev

# Formato + lint + datos sintéticos + intérprete correcto + pruebas + pipeline completo
verify: format lint bootstrap-minimal check-runtime test kedro-run

verify-all: verify verify-notebooks

check-runtime:
	python scripts/check_runtime_deps.py

verify-notebooks:
	python scripts/verify_notebooks.py

format:
	ruff format src tests scripts

lint:
	ruff check src tests scripts

bootstrap-minimal:
	python scripts/bootstrap_data.py --source minimal

test:
	python -m pytest tests/ -q --tb=short

kedro-run:
	python -m kedro run

kedro-viz:
	kedro viz
