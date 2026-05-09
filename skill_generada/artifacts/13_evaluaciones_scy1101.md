# Evaluación SCY1101 — Guía de Evaluaciones Estudiantiles
> Fuente: EV_PARCIAL_1_INSTRUCCIONES_ESTUDIANTE.docx, EV_PARCIAL_1_RUBRICA.docx, EV PARCIAL 2 SCY1101_ESTUDIANTE.pdf, GUIA_KEDRO_ESTUDIANTE.docx

Esta guía documenta los requisitos de las evaluaciones parciales de la asignatura de Programación para la Ciencia de Datos (SCY1101), orientadas a evaluar competencias en Kedro, análisis de datos y modelado.

---

## 1. Evaluación Parcial 1: Transformación y Calidad de Datos

**Objetivo:** Desarrollar un proyecto completo de transformación de datos usando Kedro. Abarca desde la carga hasta el dataset final limpio.

### 1.1 Tareas requeridas (Alineadas con EA1)
El proyecto se divide en 4 pipelines principales que los estudiantes deben construir en su proyecto `ev_parcial1_apellido`:

1.  **`data_ingestion` (AD 1.1)**
    *   **Acción:** Cargar los 4 archivos CSV asignados desde `data/01_raw/`.
    *   **Exploración:** Obtener forma, tipos, `head()`, `describe()`, `info()`.
    *   **Diagnóstico:** Detectar problemas de calidad.
    *   **Salida:** Reporte de diagnóstico inicial.
2.  **`data_cleaning` (AD 1.2)**
    *   **Acción:** Tratamiento de nulos, eliminación de duplicados, corrección de tipos mixtos, estandarización de fechas y strings. Tratamiento de outliers (Z-score o IQR).
    *   **Salida:** Datasets limpios en `data/02_intermediate/`.
3.  **`data_transform` (AD 1.3)**
    *   **Acción:** Joins/merges de las 4 tablas, uso de `pivot_table`, `groupby`, creación de features derivadas, normalización/estandarización, codificación de categóricas.
    *   **Salida:** Dataset integrado en `data/03_primary/`.
4.  **`data_validation` (AD 1.4)**
    *   **Acción:** Verificación de integridad post-transformación, validación de esquemas y comparación del estado inicial con el final.
    *   **Salida:** Reporte de validación en `data/08_reporting/`.

### 1.2 Entregables (Encargo 10% y Presentación 20%)
*   **Proyecto Kedro Funcional:** `kedro run` debe ejecutar los 4 pipelines sin errores. Catalog y Parameters correctamente configurados (`catalog.yml`, `parameters.yml`).
*   **Notebook Exploratorio:** Análisis exploratorio inicial (EDA).
*   **Informe Técnico (8-12 páginas):** Resumen, EDA, Metodología, Resultados, Conclusiones.
*   **Entorno:** `requirements.txt` y `README.md`.
*   **Presentación (15m + 5m Q&A):** Demostración del código, justificación de decisiones y hallazgos.

---

## 2. Evaluación Parcial 2: Machine Learning

**Objetivo:** Implementación completa del ciclo de machine learning (modelos supervisados y no supervisados), con comparación y optimización rigurosa, orientada a problemas de negocio reales.

### 2.1 Requisitos de Modelado
*   **Múltiples Modelos (Supervisados):** Implementar modelos de clasificación o regresión usando `scikit-learn`.
*   **Modelos No Supervisados:** Aplicar clustering o reducción de dimensionalidad (ej. PCA, K-Means) para exploración o segmentación.
*   **Evaluación:** Validación cruzada, múltiples métricas interpretadas comparativamente.
*   **Optimización:** Búsqueda de hiperparámetros (GridSearchCV, RandomizedSearchCV).
*   **Reproducibilidad:** Código limpio, documentado, con semillas fijas, manejo de excepciones.

### 2.2 Rúbrica de Evaluación (Puntos Clave para el 100%)
1.  **Implementación Supervisada (20%):** Implementa y configura múltiples modelos con pipelines. Justifica cada decisión técnica y demuestra un dominio de `scikit-learn`.
2.  **Validación y Evaluación (20%):** Realiza validación cruzada robusta, calcula todas las métricas, y compara/visualiza resultados con análisis avanzado.
3.  **Optimización de Hiperparámetros (30%):** Implementa optimización exhaustiva, justificando técnica y visualmente el impacto.
4.  **Aprendizaje No Supervisado (30%):** Aplica múltiples técnicas no supervisadas, evaluadas con métricas y visualizaciones avanzadas.

*(El 65% restante del peso de la rúbrica evalúa la defensa oral y presentación: argumentación, interpretación de métricas y explicación de optimización).*

### 2.3 Entregables
*   **Informe Técnico (12-15 páginas):** Resumen, Marco Metodológico, Análisis Experimental, Resultados y Comparación, Optimización, Conclusiones, Referencias.
*   **Código:** Proyecto reproducible.
*   **Presentación:** Defensa de resultados, justificación de selección de modelos, comparación de métricas y lecciones aprendidas.

---

## 3. Rol del Asistente (Antigravity)
Al interactuar en el contexto de SCY1101, el asistente debe:
1.  **Fomentar la justificación técnica:** Cuando se pida un modelo o transformación, recordar explicar el *por qué*.
2.  **Guiar la modularidad:** Ayudar a dividir el código en los pipelines solicitados (Ingestion, Cleaning, Transform, Validation).
3.  **Asegurar la reproducibilidad:** Enseñar a no hardcodear rutas, usar `parameters.yml` y semillas fijas (`random_state=42`).
4.  **Apoyar en la evaluación:** Recordar incluir validación cruzada, GridSearchCV, métricas múltiples y técnicas no supervisadas para alcanzar el máximo nivel en la rúbrica de la EV Parcial 2.
