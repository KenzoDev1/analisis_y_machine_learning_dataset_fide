"""Nodos del pipeline de aprendizaje no supervisado (Ev2).

Implementa K-Means clustering, PCA para reducción de dimensionalidad
y métricas de evaluación (Silhouette Score, Calinski-Harabasz, Davies-Bouldin).

Flujo:
  1. Evaluación exploratoria de múltiples K (método del codo).
  2. Entrenamiento del modelo definitivo con K fijo (parametrizado).
  3. Etiquetado del dataset con la columna ``cluster_label``.
  4. Retorna: reporte de métricas, modelo KMeans exportable, DataFrame etiquetado.
"""
import pandas as pd
import numpy as np
import logging
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

logger = logging.getLogger(__name__)

RANDOM_STATE = 42

# Features numéricas para clustering
CLUSTER_FEATURES = [
    "rating_std_avg",
    "rating_change",
    "total_months_active",
    "age_approx",
]


def run_unsupervised(
    df: pd.DataFrame,
    clustering_params: dict,
) -> tuple:
    """Ejecuta análisis no supervisado completo.

    1. Selecciona features y escala
    2. Prueba diferentes valores de K (método del codo)
    3. Entrena modelo definitivo con K fijo (parametrizado)
    4. Etiqueta el dataset con ``cluster_label``
    5. Aplica PCA para visualización
    6. Calcula métricas de clustering

    Returns:
        Tuple[reporte_dict, modelo_kmeans_definitivo, DataFrame_etiquetado]
    """
    logger.info("=" * 60)
    logger.info("APRENDIZAJE NO SUPERVISADO")
    logger.info("=" * 60)

    # ----- 1. Preparar features -----
    available = [c for c in CLUSTER_FEATURES if c in df.columns]
    X = df[available].dropna()

    training_sample_size = clustering_params.get("training_sample_size", 50000)
    if len(X) > training_sample_size:
        logger.info(f"Subsampling training dataset a {training_sample_size} registros")
        X = X.sample(n=training_sample_size, random_state=RANDOM_STATE)

    logger.info(f"Features para clustering: {available}")
    logger.info(f"Registros (X final): {len(X)}")

    sample_size = clustering_params.get("silhouette_sample_size", 10000)
    final_k = clustering_params.get("final_k", 4)
    logger.info(f"Silhouette Sample Size: {sample_size}")
    logger.info(f"K definitivo seleccionado: {final_k}")

    # Escalar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ----- 2. Método del codo — evaluar múltiples K -----
    k_range = range(2, 9)
    inertias = []
    silhouettes = []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=1, max_iter=100)
        labels = km.fit_predict(X_scaled)
        inertias.append(float(km.inertia_))
        sil = silhouette_score(
            X_scaled, labels, sample_size=sample_size, random_state=RANDOM_STATE
        )
        silhouettes.append(round(float(sil), 4))
        logger.info(f"  K={k} — Inertia: {km.inertia_:.2f}, Silhouette: {sil:.4f}")

    # K con mejor silhouette (informativo)
    best_k_silhouette = list(k_range)[np.argmax(silhouettes)]
    logger.info(f"  Mejor K por Silhouette: {best_k_silhouette}")

    # ----- 3. Modelo definitivo con K fijo (parametrizado) -----
    logger.info(f"\n--- Entrenando modelo definitivo con K={final_k} ---")
    final_km = KMeans(
        n_clusters=final_k, random_state=RANDOM_STATE, n_init=1, max_iter=100
    )
    final_labels = final_km.fit_predict(X_scaled)

    # ----- 4. Etiquetar dataset -----
    X_labeled = X.copy()
    X_labeled["cluster_label"] = final_labels
    logger.info(f"  Dataset etiquetado: {X_labeled.shape}")

    # ----- 5. PCA — Reducción a 2D -----
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    X_pca = pca.fit_transform(X_scaled)

    logger.info(
        f"  PCA — Varianza explicada: "
        f"PC1={pca.explained_variance_ratio_[0]:.4f}, "
        f"PC2={pca.explained_variance_ratio_[1]:.4f}, "
        f"Total={sum(pca.explained_variance_ratio_):.4f}"
    )

    # ----- 6. Métricas finales del modelo definitivo -----
    final_silhouette = silhouette_score(
        X_scaled, final_labels, sample_size=sample_size, random_state=RANDOM_STATE
    )
    final_calinski = calinski_harabasz_score(X_scaled, final_labels)
    final_davies = davies_bouldin_score(X_scaled, final_labels)

    # Distribución de clusters
    cluster_dist = pd.Series(final_labels).value_counts().sort_index().to_dict()
    cluster_dist = {f"cluster_{k}": int(v) for k, v in cluster_dist.items()}

    report = {
        "final_k": int(final_k),
        "best_k_by_silhouette": int(best_k_silhouette),
        "silhouette_score": round(float(final_silhouette), 4),
        "calinski_harabasz_score": round(float(final_calinski), 4),
        "davies_bouldin_score": round(float(final_davies), 4),
        "cluster_distribution": cluster_dist,
        "elbow_data": {
            "k_values": list(k_range),
            "inertias": inertias,
            "silhouettes": silhouettes,
        },
        "pca_variance_explained": {
            "PC1": round(float(pca.explained_variance_ratio_[0]), 4),
            "PC2": round(float(pca.explained_variance_ratio_[1]), 4),
            "total": round(float(sum(pca.explained_variance_ratio_)), 4),
        },
    }

    logger.info(f"\nClustering completado — K={final_k}, Silhouette={final_silhouette:.4f}")
    return report, final_km, X_labeled
