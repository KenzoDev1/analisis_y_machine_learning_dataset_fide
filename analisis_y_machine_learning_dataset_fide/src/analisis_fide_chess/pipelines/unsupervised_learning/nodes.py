"""Nodos del pipeline de aprendizaje no supervisado (Ev2).

Implementa K-Means clustering, PCA para reducción de dimensionalidad
y métricas de evaluación (Silhouette Score, Calinski-Harabasz, Davies-Bouldin).
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
    3. Aplica K-Means con el K óptimo
    4. Aplica PCA para visualización
    5. Calcula métricas de clustering

    Returns:
        Tuple[modelo_kmeans, reporte_dict]
    """
    logger.info("=" * 60)
    logger.info("APRENDIZAJE NO SUPERVISADO")
    logger.info("=" * 60)

    # ----- 1. Preparar features -----
    available = [c for c in CLUSTER_FEATURES if c in df.columns]
    X = df[available].dropna()
    logger.info(f"Features para clustering: {available}")
    logger.info(f"Registros: {len(X)}")

    sample_size = clustering_params.get("silhouette_sample_size", 10000)
    logger.info(f"Silhouette Sample Size: {sample_size}")

    # Escalar
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ----- 2. Método del codo — encontrar K óptimo -----
    k_range = range(2, 11)
    inertias = []
    silhouettes = []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        labels = km.fit_predict(X_scaled)
        inertias.append(float(km.inertia_))
        sil = silhouette_score(
            X_scaled, labels, sample_size=sample_size, random_state=RANDOM_STATE
        )
        silhouettes.append(round(float(sil), 4))
        logger.info(f"  K={k} — Inertia: {km.inertia_:.2f}, Silhouette: {sil:.4f}")

    # Elegir K con mejor silhouette
    best_k = list(k_range)[np.argmax(silhouettes)]
    logger.info(f"  Mejor K por Silhouette: {best_k}")

    # ----- 3. K-Means final -----
    final_km = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=10)
    final_labels = final_km.fit_predict(X_scaled)

    # ----- 4. PCA — Reducción a 2D -----
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    X_pca = pca.fit_transform(X_scaled)

    logger.info(
        f"  PCA — Varianza explicada: "
        f"PC1={pca.explained_variance_ratio_[0]:.4f}, "
        f"PC2={pca.explained_variance_ratio_[1]:.4f}, "
        f"Total={sum(pca.explained_variance_ratio_):.4f}"
    )

    # ----- 5. Métricas finales -----
    final_silhouette = silhouette_score(
        X_scaled, final_labels, sample_size=sample_size, random_state=RANDOM_STATE
    )
    final_calinski = calinski_harabasz_score(X_scaled, final_labels)
    final_davies = davies_bouldin_score(X_scaled, final_labels)

    # Distribución de clusters
    cluster_dist = pd.Series(final_labels).value_counts().sort_index().to_dict()
    cluster_dist = {f"cluster_{k}": int(v) for k, v in cluster_dist.items()}

    report = {
        "best_k": int(best_k),
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

    logger.info(f"\nClustering completado — K={best_k}, Silhouette={final_silhouette:.4f}")
    return final_km, report
