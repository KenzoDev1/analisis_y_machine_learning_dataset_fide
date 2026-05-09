# CRISP-DM y aprendizaje de machine learning con este proyecto

**¿Primera vez con el repo?** Empieza por [../GUIA_ESTUDIANTES.md](../GUIA_ESTUDIANTES.md) (instalación, datos, Jupyter).

Esta guía enlaza la metodología **CRISP-DM** (estándar de la industria para proyectos de minería de datos) con el flujo de trabajo de este repositorio: notebook exploratorio, catálogo Kedro y pipelines reproducibles. Sirve como hilo conductor para clases o talleres.

**Guía complementaria (modelos en detalle + flujo integrado con diagramas):** [modelos_y_flujo_integrado.md](modelos_y_flujo_integrado.md).

**Notebooks por fases (01–06) y opcional todo-en-uno:** ver [../../notebooks/README.md](../../notebooks/README.md).

---

## Las seis fases de CRISP-DM (qué son y dónde las trabajan aquí)

### 1. Comprensión del negocio (Business understanding)

**Objetivo pedagógico:** Formular el problema en términos medibles y acotar expectativas (¿predicción, descripción o causalidad?).

**Con este dataset:**

- **Clasificación:** predecir el **resultado** del partido (victoria visitante / empate / victoria local) usando señales disponibles antes del partido (en el flujo base: cuotas Bet365). Las cuotas ya incorporan información pública y expectativas del mercado; el modelo aprende patrones estadísticos, no “reglas del fútbol”.
- **Regresión:** predecir un número continuo, por ejemplo **goles del equipo local**, con las mismas u otras variables.

**Preguntas para el aula:** ¿Qué decisión se apoyaría en esta predicción? ¿Qué error es más costoso (falsos positivos vs falsos negativos)? ¿El uso es ético y razonable?

**En el repo:** definición implícita en `conf/base/parameters.yml` (columnas objetivo y features) y en el notebook (secciones de clasificación y regresión).

---

### 2. Comprensión de los datos (Data understanding)

**Objetivo pedagógico:** Conocer origen, granularidad, calidad, sesgos y limitaciones.

**Con este dataset:**

- Datos en **SQLite** (`data/raw/database.sqlite`): tablas como `Match`, `Team`, `League`, atributos de jugadores/equipos, etc.
- Revisar **valores faltantes**, **rangos** (goles, cuotas), **distribución temporal** (temporadas) y si hay **duplicados** o filas inconsistentes.

**En el repo:**

- Catálogo Kedro: `conf/base/catalog.yml` (qué tablas se cargan y cómo).
- Notebook: exploración con `catalog.load(...)`, histogramas, conteos, correlaciones (pueden ampliar con `seaborn`).

---

### 3. Preparación de los datos (Data preparation)

**Objetivo pedagógico:** Construir un conjunto analítico limpio: objetivo, predictores, particiones, y documentar decisiones.

**Con este dataset (flujo actual):**

- Se derivan **etiquetas de clasificación** a partir de `home_team_goal` y `away_team_goal`.
- Se usan columnas de cuotas **B365**; las filas sin cuotas se eliminan (`dropna` en esas columnas).
- Los **goles** se mantienen para la tarea de regresión.

**En el repo:**

- Nodo `build_ml_features_table` en `src/.../pipelines/data_processing/`.
- Salida intermedia: `features_for_ml` (Parquet en `data/05_model_input/` tras `kedro run`).

**Debate en clase:** ¿Es adecuado mezclar todas las temporadas en un solo split aleatorio? (Avanzado: validación por tiempo para reducir **fuga temporal**.)

---

### 4. Modelado (Modeling)

**Objetivo pedagógico:** Probar varias técnicas, entender supuestos y límites de cada familia.

**Resumen rápido** (para explicaciones ampliadas, hiperparámetros, analogías y diagramas del flujo Kedro/notebook, ver **[modelos_y_flujo_integrado.md](modelos_y_flujo_integrado.md)**):

| Enfoque | Ejemplos en el código | Idea clave |
|--------|------------------------|------------|
| Lineal (clasificación) | Regresión logística | Fronteras de decisión lineales; con escalado, los coeficientes ayudan a interpretar dirección y magnitud (asociación, no causalidad). |
| Lineal (regresión) | Ridge | Penalización L2; estable si las cuotas están correlacionadas. |
| Márgenes / SVM | `LinearSVC` | Separación lineal con margen máximo. |
| Instancias / no paramétrico | k-NN | Predicción local por vecinos; escala crítica. |
| Ensambles (bagging) | `RandomForest` | Muchos árboles en paralelo; reduce varianza. |
| Ensambles (boosting) | `HistGradientBoosting` | Árboles en serie corrigiendo errores; muy expresivo. |

**En el repo:** pipelines `ml_classification` y `ml_regression`; en el notebook, bucles de comparación de modelos.

---

### 5. Evaluación (Evaluation)

**Objetivo pedagógico:** Medir el rendimiento con métricas alineadas al problema y revisar errores sistemáticos.

**Clasificación (multiclase, como aquí):**

| Métrica | Qué mide | Cuándo importa |
|---------|-----------|----------------|
| **Accuracy** | Proporción de aciertos global | Puede engañar si las clases están desbalanceadas. |
| **F1 macro** | Media simple del F1 por clase | Trata cada clase con igual peso; útil para comparar modelos de forma equilibrada entre clases. |
| **F1 weighted** | F1 ponderado por soporte de cada clase | Más cercano al rendimiento “típico” si hay desbalance. |
| **Informe por clase** (`classification_report`) | Precision, recall, F1 por etiqueta | Para ver si el modelo falla solo en empates, por ejemplo. |
| **Matriz de confusión** | Errores entre clases | Diagnóstico visual de confusiones sistemáticas. |

**Regresión:**

| Métrica | Qué mide |
|---------|-----------|
| **MAE** | Error absoluto medio (misma unidad que el objetivo: goles). |
| **RMSE** | Penaliza más los errores grandes. |
| **R²** | Fracción de varianza explicada por el modelo (comparar modelos en el mismo split; no sustituye el análisis de residuos). |

**Explicabilidad (complemento a la evaluación):**

- **Importancia por permutación:** qué tanto empeora el modelo si una variable se vuelve ruido, manteniendo el resto.
- **SHAP** (opcional): descomposición más fina en modelos de árbol; instalar con `pip install -e ".[explain]"`.

**En el repo:** JSON en `data/08_reporting/` (`classification_metrics.json`, `regression_metrics.json`); CSV de importancias; figuras en el notebook.

---

### 6. Despliegue (Deployment)

**Objetivo pedagógico:** Pasar de experimento a algo reproducible, versionable y documentado.

**En el repo:**

- **Kedro:** `kedro run`, pipelines nombrados, parámetros en YAML, artefactos en rutas estándar.
- **Buenas prácticas para estudiantes:** no commitear la base SQLite ni credenciales; documentar versión de Python y dependencias (`requirements.txt` / `pyproject.toml`).

---

## Cómo usar esto en una asignatura (sugerencia de secuencia)

1. **Sesión 1:** Fases 1–2 (negocio + datos): explorar tablas en SQL o vía `catalog`, definir una pregunta clara.
2. **Sesión 2:** Fase 3: replicar y luego **modificar** features (otras casas de apuestas, agregados por equipo) y discutir calidad.
3. **Sesión 3:** Fase 4–5: entrenar, comparar métricas, matrices de confusión y errores de regresión; introducir permutación (y SHAP si aplica).
4. **Sesión 4:** Fase 6 + ética: reproducibilidad con Kedro, límites del modelo, y posible extensión (validación temporal).

---

## Referencias breves

- CRISP-DM: proceso iterativo; no es lineal: a menudo se vuelve atrás tras evaluación o nueva comprensión de datos.
- Documentación Kedro: [https://docs.kedro.org](https://docs.kedro.org)

Si amplías el proyecto, mantén explícitas en el notebook o en un informe las decisiones de cada fase: eso es lo que evalúa mejor el dominio de la metodología, no solo el accuracy final.
