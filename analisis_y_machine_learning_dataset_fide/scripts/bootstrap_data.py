#!/usr/bin/env python3
"""Descarga o genera `data/raw/database.sqlite` para desarrollo, pruebas y Docker.

Orden por defecto:
1) Intentar descarga desde Hugging Face (réplica del European Soccer Database).
2) Si falla, generar una base **mínima** sintética (mismas tablas que el catálogo; solo `Match` poblada).

Uso:
  python scripts/bootstrap_data.py
  python scripts/bootstrap_data.py --source minimal
  python scripts/bootstrap_data.py --source download --force
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from http import HTTPStatus
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = PROJECT_ROOT / "data" / "raw" / "database.sqlite"
# Umbral: archivo mayor = asumimos base completa y no sobrescribimos sin --force
MIN_BYTES_SKIP_REGEN = 500_000

# Réplica pública del dataset de Kaggle (Hugging Face). Puede fallar intermitentemente.
HF_SQLITE_URL = (
    "https://huggingface.co/datasets/julien-c/kaggle-hugomathien-soccer/"
    "resolve/main/database.sqlite"
)
REQUIRED_MATCH_COLUMNS = {
    "home_team_goal",
    "away_team_goal",
    "B365H",
    "B365D",
    "B365A",
}


def has_expected_sqlite_schema(db_path: Path) -> bool:
    """Comprueba que SQLite exista, sea legible y tenga las columnas usadas en clase."""
    if not db_path.is_file():
        return False
    try:
        with sqlite3.connect(db_path) as con:
            integrity = con.execute("PRAGMA integrity_check").fetchone()
            if not integrity or integrity[0] != "ok":
                return False
            table_exists = con.execute(
                """
                SELECT 1
                FROM sqlite_master
                WHERE type = 'table' AND name = 'Match'
                """
            ).fetchone()
            if not table_exists:
                return False
            columns = {
                row[1] for row in con.execute("PRAGMA table_info('Match')").fetchall()
            }
            return REQUIRED_MATCH_COLUMNS.issubset(columns)
    except sqlite3.Error:
        return False


def download_file(url: str, dest: Path, timeout: int = 600) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "analisis-equipos-de-football-bootstrap/1.0"},
    )
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            if tmp.exists():
                tmp.unlink()
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                code = getattr(resp, "status", None) or resp.getcode()
                if code != HTTPStatus.OK:
                    raise urllib.error.HTTPError(
                        url, code, getattr(resp, "reason", ""), resp.headers, None
                    )
                chunk = 8 * 1024 * 1024
                with tmp.open("wb") as f:
                    while True:
                        b = resp.read(chunk)
                        if not b:
                            break
                        f.write(b)
            tmp.replace(dest)
            return
        except (
            TimeoutError,
            urllib.error.URLError,
            urllib.error.HTTPError,
            OSError,
        ) as e:
            last_err = e
            if tmp.exists():
                try:
                    tmp.unlink()
                except OSError:
                    pass
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"No se pudo descargar {url}: {last_err}") from last_err


def create_minimal_database(
    dest: Path, *, n_matches: int = 4_000, seed: int = 42
) -> None:
    """SQLite mínima: tablas vacías o stub + `Match` con cuotas y goles (reproducible)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    rng = np.random.default_rng(seed)
    con = sqlite3.connect(dest)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE Country (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE League (
            id INTEGER PRIMARY KEY,
            country_id INTEGER,
            name TEXT
        );
        CREATE TABLE Match (
            id INTEGER PRIMARY KEY,
            country_id INTEGER,
            league_id INTEGER,
            season INTEGER,
            home_team_goal INTEGER,
            away_team_goal INTEGER,
            B365H REAL,
            B365D REAL,
            B365A REAL
        );
        CREATE TABLE Player (id INTEGER PRIMARY KEY);
        CREATE TABLE Player_Attributes (id INTEGER PRIMARY KEY);
        CREATE TABLE Team (id INTEGER PRIMARY KEY);
        CREATE TABLE Team_Attributes (id INTEGER PRIMARY KEY);
        """
    )
    cur.execute("INSERT INTO Country (id, name) VALUES (1, 'Demo')")
    cur.execute(
        "INSERT INTO League (id, country_id, name) VALUES (1, 1, 'Demo League')"
    )

    # Cuotas plausibles; goles 0–5; empates y resultados variados
    for i in range(1, n_matches + 1):
        h = int(rng.integers(0, 6))
        a = int(rng.integers(0, 6))
        implied = rng.uniform(1.15, 8.0, size=3)
        b365h, b365d, b365a = float(implied[0]), float(implied[1]), float(implied[2])
        cur.execute(
            """
            INSERT INTO Match (
                id, country_id, league_id, season,
                home_team_goal, away_team_goal,
                B365H, B365D, B365A
            ) VALUES (?, 1, 1, 2015, ?, ?, ?, ?, ?)
            """,
            (i, h, a, b365h, b365d, b365a),
        )
    con.commit()
    con.close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--source",
        choices=("auto", "download", "minimal"),
        default="auto",
        help="auto: intenta descargar y cae a minimal; download/minimal forzados",
    )
    p.add_argument("--output", type=Path, default=DEFAULT_DB, help="Ruta del SQLite")
    p.add_argument(
        "--force",
        action="store_true",
        help="Sobrescribe aunque ya exista un archivo grande",
    )
    args = p.parse_args(argv)
    dest: Path = args.output

    if dest.is_file() and not args.force:
        size = dest.stat().st_size
        if size > MIN_BYTES_SKIP_REGEN and has_expected_sqlite_schema(dest):
            print(f"Ya existe {dest} ({size // 1024} KiB). Usa --force para regenerar.")
            return 0
        print(f"{dest} existe, pero no pasa validación de esquema; se regenerará.")

    if args.source == "minimal":
        print("Generando SQLite mínima sintética…")
        create_minimal_database(dest)
        print(f"Listo: {dest}")
        return 0

    if args.source == "download":
        print("Descargando desde Hugging Face…")
        download_file(HF_SQLITE_URL, dest)
        print(f"Listo: {dest}")
        return 0

    # auto
    try:
        print(f"Intentando descarga: {HF_SQLITE_URL}")
        download_file(HF_SQLITE_URL, dest)
        print(f"Descarga OK: {dest}")
        return 0
    except Exception as e:
        print(
            f"Descarga no disponible ({e}). Generando SQLite mínima…", file=sys.stderr
        )
        create_minimal_database(dest)
        print(f"Listo (minimal): {dest}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
