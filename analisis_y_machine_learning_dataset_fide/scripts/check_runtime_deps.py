#!/usr/bin/env python3
"""Comprueba dependencias imprescindibles antes de `kedro run` o los tests E2E.

Uso en clase: si alguien ejecuta pytest o Kedro con el Python del sistema en vez del
`.venv` del proyecto, pandas no puede escribir Parquet sin **pyarrow** o **fastparquet**.
Este script falla con instrucciones claras en lugar de un traceback largo.
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Iterable


def _need(module: str, pip_hint: str | None = None) -> tuple[str, str | None]:
    return module, pip_hint


def _check(modules: Iterable[tuple[str, str | None]]) -> list[str]:
    missing: list[str] = []
    for name, hint in modules:
        try:
            importlib.import_module(name)
        except ImportError:
            extra = f" ({hint})" if hint else ""
            missing.append(f"{name}{extra}")
    return missing


def main() -> int:
    required = [
        _need("pandas"),
        _need("numpy"),
        _need("sklearn", "pip install scikit-learn"),
        _need("kedro"),
        _need(
            "pyarrow",
            "requerido para Parquet; en este repo: uv sync  o  pip install -e .",
        ),
        _need("sqlalchemy"),
    ]
    missing = _check(required)
    if missing:
        print(
            "Faltan módulos en el intérprete actual (¿activaste el venv del proyecto?).",
            file=sys.stderr,
        )
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        print(
            "\nSolución típica desde la raíz del repo:\n"
            "  python -m venv .venv && source .venv/bin/activate  # o Windows: .venv\\Scripts\\activate\n"
            "  uv sync --extra dev\n"
            '  # o: pip install -e ".[dev]"',
            file=sys.stderr,
        )
        return 1

    pd = importlib.import_module("pandas")
    pa = importlib.import_module("pyarrow")
    _ = pa.__version__

    try:
        pd.io.parquet.get_engine("pyarrow")
    except ImportError as e:
        print(
            "pandas no puede usar el motor Parquet:",
            e,
            file=sys.stderr,
        )
        return 1

    print("OK: dependencias runtime (incl. Parquet/pyarrow) disponibles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
