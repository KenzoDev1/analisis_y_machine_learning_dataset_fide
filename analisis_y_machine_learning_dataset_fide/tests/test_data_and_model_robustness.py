import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from analisis_fide_chess.pipelines.data_processing.nodes import (
    build_ml_features_table,
)
from analisis_fide_chess.pipelines.ml_classification.nodes import (
    train_classification_bundle,
)
from analisis_fide_chess.pipelines.ml_regression.nodes import (
    train_regression_bundle,
)
from scripts.bootstrap_data import create_minimal_database, has_expected_sqlite_schema

EXPECTED_COMPLETE_ROWS = 2


def _minimal_match_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "home_team_goal": [1.0, np.nan, 0.0, 2.0],
            "away_team_goal": [0.0, 1.0, np.nan, 2.0],
            "B365H": [1.8, 2.0, 2.5, 3.0],
            "B365D": [3.2, 3.1, 3.0, 2.9],
            "B365A": [4.1, 3.8, 3.5, 3.2],
        }
    )


def test_build_ml_features_table_drops_rows_with_missing_goals() -> None:
    result = build_ml_features_table(_minimal_match_frame())

    assert len(result) == EXPECTED_COMPLETE_ROWS
    assert result["home_team_goal"].isna().sum() == 0
    assert result["away_team_goal"].isna().sum() == 0
    assert result["outcome"].tolist() == [2, 1]


def test_classification_handles_small_training_split_and_missing_classes() -> None:
    features = pd.DataFrame(
        {
            "B365H": np.linspace(1.2, 3.0, 12),
            "B365D": np.linspace(2.5, 4.0, 12),
            "B365A": np.linspace(1.4, 4.5, 12),
            "outcome": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1],
        }
    )

    metrics, model, importance = train_classification_bundle(
        features,
        split={"test_size": 0.25, "random_state": 7},
        classification={
            "feature_columns": ["B365H", "B365D", "B365A"],
            "target": "outcome",
        },
    )

    assert metrics["task"] == "classification"
    assert metrics["best_model"]
    assert model is not None
    assert set(importance["feature"]) == {"B365H", "B365D", "B365A"}
    assert metrics["classification_report"]["home_win"]["support"] == 0.0


def test_regression_bundle_runs_on_small_synthetic_table() -> None:
    features = pd.DataFrame(
        {
            "B365H": np.linspace(1.2, 3.0, 12),
            "B365D": np.linspace(2.5, 4.0, 12),
            "B365A": np.linspace(1.4, 4.5, 12),
            "home_team_goal": [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3],
        }
    )

    metrics, model, importance = train_regression_bundle(
        features,
        split={"test_size": 0.25, "random_state": 7},
        regression={
            "feature_columns": ["B365H", "B365D", "B365A"],
            "target": "home_team_goal",
        },
    )

    assert metrics["task"] == "regression"
    assert metrics["best_model"]
    assert model is not None
    assert set(importance["feature"]) == {"B365H", "B365D", "B365A"}
    assert len(metrics["leaderboard"]) >= 1
    assert "best_on_test" in metrics


def test_has_expected_sqlite_schema_detects_valid_and_invalid_databases(
    tmp_path: Path,
) -> None:
    valid_db = tmp_path / "valid.sqlite"
    invalid_db = tmp_path / "invalid.sqlite"

    create_minimal_database(valid_db, n_matches=20)
    with sqlite3.connect(invalid_db) as con:
        con.execute("CREATE TABLE Match (id INTEGER PRIMARY KEY)")

    assert has_expected_sqlite_schema(valid_db)
    assert not has_expected_sqlite_schema(invalid_db)
    assert not has_expected_sqlite_schema(tmp_path / "missing.sqlite")
