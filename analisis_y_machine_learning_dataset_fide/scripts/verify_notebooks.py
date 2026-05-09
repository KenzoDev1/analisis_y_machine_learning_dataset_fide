#!/usr/bin/env python3
"""Ejecuta notebooks Jupyter en memoria para verificar que la clase no falle."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
TIMEOUT_SECONDS = 600


def execute_notebook(path: Path) -> None:
    """Ejecuta un notebook sin sobrescribirlo; falla si alguna celda falla."""
    print(f"Ejecutando {path.relative_to(PROJECT_ROOT)} ...", flush=True)
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=TIMEOUT_SECONDS,
        resources={"metadata": {"path": str(PROJECT_ROOT)}},
    )
    try:
        client.execute()
    except CellExecutionError as exc:
        print(f"ERROR en {path.relative_to(PROJECT_ROOT)}", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        raise


def main() -> int:
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("KEDRO_DISABLE_TELEMETRY", "1")

    notebooks = sorted(NOTEBOOKS_DIR.glob("*.ipynb"))
    if not notebooks:
        print("No se encontraron notebooks para verificar.", file=sys.stderr)
        return 1

    for notebook in notebooks:
        execute_notebook(notebook)

    print(f"OK: {len(notebooks)} notebooks ejecutados sin errores.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
