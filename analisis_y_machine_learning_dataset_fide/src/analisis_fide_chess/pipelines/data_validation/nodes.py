"""Nodos del pipeline de validación de datos (AD 1.4).

Verificación de integridad post-transformación, validación de esquema
y comparación del estado inicial versus el final.
"""
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Columnas mínimas esperadas tras la transformación
EXPECTED_COLUMNS = [
    "fide_id",
    "rating_std_avg",
    "is_expert",
    "rating_change",
]


def validate_data(df: pd.DataFrame) -> dict:
    """Valida el dataset integrado y genera un reporte JSON detallado."""
    logger.info("=" * 60)
    logger.info("VALIDACIÓN DE DATOS POST-TRANSFORMACIÓN (AD 1.4)")
    logger.info("=" * 60)

    errors = []
    warnings = []

    # ----- 1. Verificar que no esté vacío -----
    if len(df) == 0:
        errors.append("El dataset final está vacío.")
    else:
        logger.info(f"  ✓ Dataset con {len(df)} filas y {len(df.columns)} columnas.")

    # ----- 2. Validación de esquema: columnas esperadas -----
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Columnas faltantes: {missing_cols}")
    else:
        logger.info(f"  ✓ Todas las columnas esperadas presentes: {EXPECTED_COLUMNS}")

    # ----- 3. Verificar nulos residuales -----
    null_summary = df.isnull().sum()
    null_cols = null_summary[null_summary > 0]
    if len(null_cols) > 0:
        for col, count in null_cols.items():
            pct = count / len(df) * 100
            if pct > 50:
                errors.append(f"Columna '{col}' tiene {pct:.1f}% nulos (crítico).")
            elif pct > 10:
                warnings.append(f"Columna '{col}' tiene {pct:.1f}% nulos.")
        logger.info(f"  ⚠ Columnas con nulos: {null_cols.to_dict()}")
    else:
        logger.info("  ✓ Sin valores nulos residuales.")

    # ----- 4. Verificar duplicados por fide_id -----
    if "fide_id" in df.columns:
        dup_ids = df["fide_id"].duplicated().sum()
        if dup_ids > 0:
            warnings.append(f"{dup_ids} fide_id duplicados encontrados.")
        else:
            logger.info("  ✓ Sin fide_id duplicados.")

    # ----- 5. Verificar rangos de la variable objetivo -----
    if "is_expert" in df.columns:
        value_counts = df["is_expert"].value_counts().to_dict()
        logger.info(f"  Distribución is_expert: {value_counts}")
        if len(value_counts) < 2:
            warnings.append("is_expert tiene una sola clase — problema de desbalanceo severo.")

    # ----- 6. Verificar tipos de datos -----
    dtypes_report = {col: str(dtype) for col, dtype in df.dtypes.items()}

    # ----- 7. Estadísticas descriptivas del dataset final -----
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    stats = {}
    for col in numeric_cols[:10]:  # Limitar a 10 columnas para no inflar el JSON
        stats[col] = {
            "mean": round(float(df[col].mean()), 4) if not df[col].isna().all() else None,
            "std": round(float(df[col].std()), 4) if not df[col].isna().all() else None,
            "min": round(float(df[col].min()), 4) if not df[col].isna().all() else None,
            "max": round(float(df[col].max()), 4) if not df[col].isna().all() else None,
        }

    # ----- Construir reporte -----
    report = {
        "status": "PASS" if not errors else "FAIL",
        "num_rows": len(df),
        "num_columns": len(df.columns),
        "columns": df.columns.tolist(),
        "dtypes": dtypes_report,
        "missing_values": df.isnull().sum().to_dict(),
        "errors": errors,
        "warnings": warnings,
        "descriptive_stats": stats,
    }

    if errors:
        for e in errors:
            logger.error(f"  ✗ {e}")
    if warnings:
        for w in warnings:
            logger.warning(f"  ⚠ {w}")

    logger.info(f"Validación completada — Estado: {report['status']}")
    return report
