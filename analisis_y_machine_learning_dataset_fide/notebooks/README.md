# Laboratorios Jupyter (orden recomendado)

## Antes de abrir cualquier notebook

1. **Raíz del proyecto** en la terminal (donde está `pyproject.toml`).
2. **Entorno virtual activado** (`.venv`).
3. **Dependencias instaladas:** `pip install -r requirements.txt` y `pip install -e .`
4. **Base de datos creada:** `python scripts/bootstrap_data.py`  
   Guía detallada: [docs/GUIA_ESTUDIANTES.md](../docs/GUIA_ESTUDIANTES.md)

## Cómo abrir Jupyter con Kedro

```bash
kedro jupyter lab
```

o `kedro jupyter notebook`. Así tendrás `catalog`, `context` y rutas correctas.

En la primera celda de cada notebook:

```python
%load_ext kedro.ipython
```

---

## Secuencia de notebooks

| Orden | Notebook | Fase CRISP-DM | Contenido principal | Tiempo orientativo* |
|-------|----------|---------------|----------------------|----------------------|
| 01 | `01_comprension_negocio_y_datos.ipynb` | 1–2 | Problema, `catalog`, `match`, calidad, histogramas | ~30–45 min |
| 02 | `02_preparacion_datos.ipynb` | 3 | Tabla `df_ml`; comparación con Parquet de Kedro | ~20–30 min |
| 03 | `03_clasificacion_resultado.ipynb` | 4–5 | Varios clasificadores, barras de métricas, matriz de confusión | ~45–60 min |
| 04 | `04_regresion_goles.ipynb` | 4–5 | Ridge, bosques, boosting; MAE, RMSE, R²; residuos | ~30–45 min |
| 05 | `05_explicabilidad_evaluacion.ipynb` | 5 | Permutación, coeficientes logísticos, SHAP opcional | ~30 min |
| 06 | `06_pipeline_Kedro.ipynb` | 6 | Parámetros YAML, `session.run()`, leer salidas | ~20–30 min |
| 07 | `07_validacion_cruzada_hiperparametros.ipynb` | 4–5 | KFold/StratifiedKFold, `cross_validate`, `GridSearchCV`, `RandomizedSearchCV` (complementa el un solo split de `kedro run`; ver guía **4.1** en `docs/guias/modelos_y_flujo_integrado.md`) | ~45–60 min |
| 08 | `08_no_supervisado_clustering.ipynb` | 2–4 | PCA, K-Means, silhouette e interpretación de clusters | ~30–45 min |

\*Depende del hardware y de si usáis la base completa o la sintética.

**Opcional (todo en uno):** `Exploracion_de_datos.ipynb` — repaso rápido de clasificación, regresión y explicabilidad en un solo flujo.

---

## Después de los notebooks

- Ejecutar el pipeline completo: `python -m kedro run`
- Verificar el proyecto: `make verify` (desde la raíz, con `pip install -e ".[dev]"`)
- Verificar que los notebooks corren: `make verify-notebooks`

Salidas generadas por Kedro:

- `data/05_model_input/features_for_ml.parquet`
- `data/08_reporting/classification_metrics.json`, `regression_metrics.json`
- `data/06_models/*.pkl`
- CSV de importancias en `data/08_reporting/`

---

## Material de apoyo

- Estudiantes: [docs/GUIA_ESTUDIANTES.md](../docs/GUIA_ESTUDIANTES.md)
- CRISP-DM y métricas: [docs/guias/crispdm_y_machine_learning.md](../docs/guias/crispdm_y_machine_learning.md)
- Modelos y flujo integrado: [docs/guias/modelos_y_flujo_integrado.md](../docs/guias/modelos_y_flujo_integrado.md)

---

## Nota sobre la base sintética

Si usáis `bootstrap_data.py` sin descarga completa, la base **mínima** tiene la tabla `Match` poblada pero otras tablas (`Player`, `Team`, …) pueden estar **vacías**. Los laboratorios 01–06 están pensados para no depender de esas tablas, salvo exploraciones opcionales en el notebook 01.
