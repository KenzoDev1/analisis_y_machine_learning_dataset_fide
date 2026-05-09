"""
Tests for the Kedro project: registro de pipelines y ejecución end-to-end.
"""

import subprocess
import sys
from pathlib import Path

from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project

from analisis_equipos_de_football.pipeline_registry import register_pipelines

# Tamaño mínimo para considerar que ya hay una base usable (no un stub vacío).
_MIN_SQLITE_BYTES = 1_000


class TestPipelineRegistry:
    def test_default_pipeline_has_nodes(self) -> None:
        bootstrap_project(Path.cwd())
        pipelines = register_pipelines()
        assert "__default__" in pipelines
        assert len(pipelines["__default__"].nodes) > 0


def _ensure_minimal_sqlite(project_root: Path) -> None:
    db = project_root / "data" / "raw" / "database.sqlite"
    if db.is_file() and db.stat().st_size > _MIN_SQLITE_BYTES:
        return
    subprocess.run(
        [
            sys.executable,
            str(project_root / "scripts" / "bootstrap_data.py"),
            "--source",
            "minimal",
            "--force",
        ],
        cwd=project_root,
        check=True,
    )


class TestKedroRun:
    def test_kedro_run_end_to_end(self) -> None:
        root = Path.cwd()
        _ensure_minimal_sqlite(root)
        bootstrap_project(root)
        with KedroSession.create(project_path=root) as session:
            session.run()
