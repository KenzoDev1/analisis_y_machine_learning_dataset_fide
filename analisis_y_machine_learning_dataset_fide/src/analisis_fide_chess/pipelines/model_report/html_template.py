"""Plantilla HTML para el informe técnico de modelos ML."""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;line-height:1.7;font-size:15px}
.container{max-width:1100px;margin:0 auto;padding:40px 24px}
h1{font-size:2.4rem;font-weight:800;background:linear-gradient(135deg,#06b6d4,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px}
h2{font-size:1.5rem;font-weight:700;color:#06b6d4;margin:40px 0 16px;padding-bottom:8px;border-bottom:2px solid #1e293b}
h3{font-size:1.15rem;font-weight:600;color:#a78bfa;margin:24px 0 12px}
.subtitle{color:#94a3b8;font-size:1rem;margin-bottom:32px}
.card{background:rgba(30,41,59,.65);backdrop-filter:blur(12px);border:1px solid #334155;border-radius:16px;padding:28px;margin-bottom:24px}
table{width:100%;border-collapse:collapse;margin:16px 0}
th{background:#1e293b;color:#06b6d4;font-weight:600;text-align:left;padding:12px 16px;font-size:.85rem;text-transform:uppercase;letter-spacing:.5px}
td{padding:10px 16px;border-bottom:1px solid #1e293b;font-size:.9rem}
tr:hover td{background:rgba(6,182,212,.06)}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:.75rem;font-weight:600}
.badge-best{background:rgba(16,185,129,.2);color:#34d399;border:1px solid #34d399}
.badge-method{background:rgba(139,92,246,.2);color:#a78bfa;border:1px solid #a78bfa}
.metric-bar{height:8px;border-radius:4px;background:#1e293b;margin-top:4px;overflow:hidden}
.metric-fill{height:100%;border-radius:4px;background:linear-gradient(90deg,#06b6d4,#8b5cf6);transition:width .3s}
.metric-val{font-weight:700;font-size:1.1rem;color:#f1f5f9}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.stat-card{background:#1e293b;border-radius:12px;padding:20px;text-align:center}
.stat-card .label{font-size:.8rem;color:#94a3b8;text-transform:uppercase;letter-spacing:1px}
.stat-card .value{font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#06b6d4,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:4px}
.tag{display:inline-block;background:#1e293b;color:#94a3b8;padding:4px 12px;border-radius:8px;font-size:.8rem;margin:2px 4px}
.footer{text-align:center;color:#475569;font-size:.8rem;margin-top:48px;padding-top:24px;border-top:1px solid #1e293b}
ul{padding-left:20px}li{margin-bottom:6px}
.cm-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:4px;max-width:300px;margin:12px 0}
.cm-cell{padding:12px;text-align:center;border-radius:8px;font-weight:700;font-size:1rem}
.cm-tp{background:rgba(16,185,129,.25);color:#34d399}
.cm-tn{background:rgba(6,182,212,.2);color:#67e8f9}
.cm-fp{background:rgba(239,68,68,.2);color:#fca5a5}
.cm-fn{background:rgba(251,191,36,.2);color:#fcd34d}
.elbow-bar{display:flex;align-items:end;gap:4px;height:80px;margin:12px 0}
.elbow-col{flex:1;border-radius:4px 4px 0 0;background:linear-gradient(0deg,#06b6d4,#8b5cf6);position:relative;min-width:20px}
.elbow-col span{position:absolute;top:-18px;left:50%;transform:translateX(-50%);font-size:.65rem;color:#94a3b8}
@media print{body{background:#fff;color:#1e293b}.card{border:1px solid #e2e8f0;background:#fff}th{background:#f1f5f9;color:#0f172a}h1{-webkit-text-fill-color:#0f172a}h2{color:#0f172a}h3{color:#4c1d95}}
@media(max-width:700px){.grid-2{grid-template-columns:1fr}h1{font-size:1.8rem}}
"""


def metric_bar(value, label=""):
    pct = min(max(value * 100, 0), 100)
    return (
        f'<div style="margin-bottom:8px">'
        f'<div style="display:flex;justify-content:space-between">'
        f'<span style="font-size:.85rem;color:#94a3b8">{label}</span>'
        f'<span class="metric-val">{value:.4f}</span></div>'
        f'<div class="metric-bar"><div class="metric-fill" style="width:{pct}%"></div></div>'
        f'</div>'
    )


def build_header(timestamp):
    return (
        f'<div style="text-align:center;margin-bottom:48px">'
        f'<h1>Informe Técnico de Modelos ML</h1>'
        f'<p class="subtitle">Análisis de Dataset FIDE Chess — Evaluación Parcial 2 · SCY1101</p>'
        f'<p style="color:#475569;font-size:.8rem">Generado: {timestamp}</p>'
        f'</div>'
    )


def build_resumen(model_options, split_params):
    features = model_options.get("features", [])
    target = model_options.get("target", "is_expert")
    test_size = split_params.get("test_size", 0.2)
    tags = "".join(f'<span class="tag">{f}</span>' for f in features)
    return (
        f'<h2>1. Resumen Ejecutivo</h2><div class="card">'
        f'<p>Este informe documenta el ciclo completo de machine learning aplicado al dataset de jugadores '
        f'de ajedrez de la FIDE, abarcando <strong>modelos supervisados</strong> (clasificación), '
        f'<strong>optimización de hiperparámetros</strong> y <strong>aprendizaje no supervisado</strong> (clustering).</p>'
        f'<h3>Problema</h3><p>Clasificar jugadores como <em>expertos</em> o <em>no expertos</em> '
        f'a partir de indicadores de rendimiento (variable objetivo: <code>{target}</code>).</p>'
        f'<h3>Features utilizadas</h3><div style="margin:8px 0">{tags}</div>'
        f'<h3>Configuración del Split</h3>'
        f'<p>Test size: <strong>{test_size*100:.0f}%</strong> · Estratificado por target · random_state=42</p>'
        f'</div>'
    )


def build_marco(tuning_params, eval_params, clustering_params):
    cv_eval = eval_params.get("cv", 3)
    cv_tune = tuning_params.get("cv", 3)
    k = clustering_params.get("final_k", 4)
    return (
        f'<h2>2. Marco Metodológico</h2><div class="card">'
        f'<p>Se sigue la metodología <strong>CRISP-DM</strong> implementada en <strong>Kedro</strong>. '
        f'Los pipelines de ML se ejecutan de forma reproducible con semillas fijas (<code>random_state=42</code>).</p>'
        f'<h3>Pipeline Supervisado</h3>'
        f'<p>Cada modelo está envuelto en un <code>sklearn.pipeline.Pipeline</code> con '
        f'<code>StandardScaler</code> → Clasificador. Esto garantiza que el escalado se aplique '
        f'de forma consistente durante entrenamiento e inferencia.</p>'
        f'<ul><li><strong>Modelos:</strong> Logistic Regression, Random Forest, KNN, SVM, Gradient Boosting</li>'
        f'<li><strong>Evaluación:</strong> Validación cruzada con cv={cv_eval}</li>'
        f'<li><strong>Optimización:</strong> GridSearchCV (espacios pequeños) + RandomizedSearchCV (espacios grandes) con cv={cv_tune}</li></ul>'
        f'<h3>Pipeline No Supervisado</h3>'
        f'<ul><li><strong>Clustering:</strong> K-Means con K={k} (seleccionado por método del codo + Silhouette)</li>'
        f'<li><strong>Reducción dimensional:</strong> PCA a 2 componentes</li>'
        f'<li><strong>Métricas:</strong> Silhouette Score, Calinski-Harabasz, Davies-Bouldin</li></ul>'
        f'</div>'
    )


def build_supervised(eval_report):
    comparison = eval_report.get("model_comparison", {})
    best = eval_report.get("best_model", "N/A")
    rows = ""
    for name, m in comparison.items():
        is_best = name == best or best in name
        badge = ' <span class="badge badge-best">★ Mejor</span>' if is_best else ""
        rows += (
            f'<tr><td><strong>{name}</strong>{badge}</td>'
            f'<td>{m.get("cv_accuracy_mean", 0):.4f} ± {m.get("cv_accuracy_std", 0):.4f}</td>'
            f'<td>{m.get("cv_f1_mean", 0):.4f} ± {m.get("cv_f1_std", 0):.4f}</td></tr>'
        )
    test_metrics = eval_report.get("test_metrics", {})
    bars = ""
    for k, v in test_metrics.items():
        bars += metric_bar(v, k.replace("_", " ").title())
    cm = eval_report.get("confusion_matrix", [[0, 0], [0, 0]])
    cm_html = ""
    if len(cm) >= 2 and len(cm[0]) >= 2:
        cm_html = (
            f'<h3>Matriz de Confusión (Modelo Principal)</h3>'
            f'<div class="cm-grid">'
            f'<div class="cm-cell cm-tn" title="True Negative">{cm[0][0]}<br><small>TN</small></div>'
            f'<div class="cm-cell cm-fp" title="False Positive">{cm[0][1]}<br><small>FP</small></div>'
            f'<div class="cm-cell cm-fn" title="False Negative">{cm[1][0]}<br><small>FN</small></div>'
            f'<div class="cm-cell cm-tp" title="True Positive">{cm[1][1]}<br><small>TP</small></div>'
            f'</div>'
        )
    return (
        f'<h2>3. Análisis Experimental — Supervisado</h2><div class="card">'
        f'<h3>Comparación de Modelos (Cross-Validation)</h3>'
        f'<table><thead><tr><th>Modelo</th><th>CV Accuracy</th><th>CV F1</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
        f'<h3>Métricas en Test — Modelo Principal ({best})</h3>{bars}'
        f'{cm_html}</div>'
    )


def build_cv(eval_report):
    cv_data = eval_report.get("cross_validation", {})
    if not cv_data:
        return '<h2>4. Validación Cruzada</h2><div class="card"><p>Sin datos de validación cruzada disponibles.</p></div>'
    rows = ""
    for metric, vals in cv_data.items():
        scores_str = ", ".join(str(s) for s in vals.get("scores", []))
        rows += (
            f'<tr><td><strong>{metric.replace("_"," ").title()}</strong></td>'
            f'<td>{vals.get("mean", 0):.4f}</td>'
            f'<td>{vals.get("std", 0):.4f}</td>'
            f'<td style="font-size:.8rem;color:#94a3b8">[{scores_str}]</td></tr>'
        )
    return (
        f'<h2>4. Validación Cruzada</h2><div class="card">'
        f'<p>Resultados detallados de cross-validation para el modelo principal, '
        f'mostrando la estabilidad del rendimiento a través de los folds.</p>'
        f'<table><thead><tr><th>Métrica</th><th>Media</th><th>Desv. Estándar</th><th>Scores por Fold</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )


def build_optimization(opt_report, tuning_params):
    if not opt_report:
        return '<h2>5. Optimización de Hiperparámetros</h2><div class="card"><p>Sin datos disponibles.</p></div>'
    best_name = opt_report.get("best_model", "N/A")
    best_cv = opt_report.get("best_cv_score", 0)
    all_results = opt_report.get("all_results", {})
    rows = ""
    for name, r in all_results.items():
        is_best = name == best_name
        badge = ' <span class="badge badge-best">★ Mejor</span>' if is_best else ""
        method = r.get("search_method", "grid").upper()
        method_badge = f'<span class="badge badge-method">{method}</span>'
        params_str = ", ".join(f'{k.replace("classifier__","")}: {v}' for k, v in r.get("best_params", {}).items())
        rows += (
            f'<tr><td><strong>{name}</strong>{badge}</td>'
            f'<td>{method_badge}</td>'
            f'<td>{r.get("best_cv_score", 0):.4f}</td>'
            f'<td>{r.get("test_accuracy", 0):.4f}</td>'
            f'<td>{r.get("test_f1", 0):.4f}</td>'
            f'<td style="font-size:.8rem;color:#94a3b8">{params_str}</td></tr>'
        )
    grids_html = ""
    grids = tuning_params.get("grids", {})
    for model_name, grid in grids.items():
        params_list = "".join(
            f'<li><code>{k}</code>: {v}</li>' for k, v in grid.items()
        )
        grids_html += f'<h3>Espacio de Búsqueda — {model_name}</h3><ul>{params_list}</ul>'
    return (
        f'<h2>5. Optimización de Hiperparámetros</h2><div class="card">'
        f'<p>Se utilizó <strong>GridSearchCV</strong> para espacios pequeños (LogisticRegression) '
        f'y <strong>RandomizedSearchCV</strong> para espacios grandes (RandomForest, GradientBoosting), '
        f'cumpliendo con el requerimiento IEE 2.3.1 de la rúbrica.</p>'
        f'<table><thead><tr><th>Modelo</th><th>Método</th><th>Best CV F1</th>'
        f'<th>Test Acc</th><th>Test F1</th><th>Mejores Params</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
        f'<div class="grid-2"><div class="stat-card">'
        f'<div class="label">Mejor Modelo Optimizado</div><div class="value">{best_name}</div></div>'
        f'<div class="stat-card"><div class="label">Mejor F1 Score (CV)</div>'
        f'<div class="value">{best_cv:.4f}</div></div></div>'
        f'{grids_html}</div>'
    )


def build_unsupervised(clust_report):
    if not clust_report:
        return '<h2>6. Aprendizaje No Supervisado</h2><div class="card"><p>Sin datos disponibles.</p></div>'
    k = clust_report.get("final_k", 0)
    best_k = clust_report.get("best_k_by_silhouette", 0)
    sil = clust_report.get("silhouette_score", 0)
    cal = clust_report.get("calinski_harabasz_score", 0)
    dav = clust_report.get("davies_bouldin_score", 0)
    dist = clust_report.get("cluster_distribution", {})
    pca = clust_report.get("pca_variance_explained", {})
    elbow = clust_report.get("elbow_data", {})
    dist_rows = "".join(
        f'<tr><td>{name}</td><td><strong>{count:,}</strong></td></tr>'
        for name, count in dist.items()
    )
    sils = elbow.get("silhouettes", [])
    max_sil = max(sils) if sils else 1
    elbow_bars = ""
    k_vals = elbow.get("k_values", [])
    for i, s in enumerate(sils):
        h = max(int((s / max_sil) * 70), 5) if max_sil > 0 else 5
        kv = k_vals[i] if i < len(k_vals) else "?"
        elbow_bars += f'<div class="elbow-col" style="height:{h}px" title="K={kv}: {s:.4f}"><span>{s:.3f}</span></div>'
    return (
        f'<h2>6. Aprendizaje No Supervisado</h2><div class="card">'
        f'<p>Se aplicó <strong>K-Means clustering</strong> con evaluación exploratoria de múltiples K '
        f'(método del codo) y selección final basada en métricas. Se usó <strong>PCA</strong> para '
        f'reducción dimensional a 2 componentes.</p>'
        f'<div class="grid-2">'
        f'<div class="stat-card"><div class="label">K Seleccionado</div><div class="value">{k}</div></div>'
        f'<div class="stat-card"><div class="label">Mejor K (Silhouette)</div><div class="value">{best_k}</div></div>'
        f'</div>'
        f'<h3>Métricas del Modelo Definitivo</h3>'
        f'{metric_bar(sil, "Silhouette Score")}'
        f'<div style="display:flex;gap:16px;margin:12px 0">'
        f'<div><span style="color:#94a3b8;font-size:.85rem">Calinski-Harabasz</span> '
        f'<span class="metric-val">{cal:.2f}</span></div>'
        f'<div><span style="color:#94a3b8;font-size:.85rem">Davies-Bouldin</span> '
        f'<span class="metric-val">{dav:.4f}</span></div></div>'
        f'<h3>Silhouette por K (Método del Codo)</h3>'
        f'<div style="display:flex;gap:4px;align-items:center;margin-bottom:4px">'
        f'{"".join(f"<span style=&quot;flex:1;text-align:center;font-size:.7rem;color:#64748b&quot;>K={kv}</span>" for kv in k_vals)}'
        f'</div><div class="elbow-bar">{elbow_bars}</div>'
        f'<h3>Distribución de Clusters</h3>'
        f'<table><thead><tr><th>Cluster</th><th>Registros</th></tr></thead>'
        f'<tbody>{dist_rows}</tbody></table>'
        f'<h3>PCA — Varianza Explicada</h3>'
        f'{metric_bar(pca.get("PC1", 0), "PC1")}'
        f'{metric_bar(pca.get("PC2", 0), "PC2")}'
        f'{metric_bar(pca.get("total", 0), "Total")}'
        f'</div>'
    )


def build_conclusiones(eval_report, opt_report, clust_report):
    best_sup = eval_report.get("best_model", "N/A")
    test_m = eval_report.get("test_metrics", {})
    best_opt = opt_report.get("best_model", "N/A") if opt_report else "N/A"
    best_cv = opt_report.get("best_cv_score", 0) if opt_report else 0
    sil = clust_report.get("silhouette_score", 0) if clust_report else 0
    k = clust_report.get("final_k", 0) if clust_report else 0
    return (
        f'<h2>7. Conclusiones</h2><div class="card">'
        f'<h3>Modelos Supervisados</h3>'
        f'<p>El modelo con mejor rendimiento en test fue <strong>{best_sup}</strong> '
        f'con un F1-Score de <strong>{test_m.get("f1_score", 0):.4f}</strong> '
        f'y Accuracy de <strong>{test_m.get("accuracy", 0):.4f}</strong>.</p>'
        f'<h3>Optimización</h3>'
        f'<p>Tras la búsqueda de hiperparámetros, el mejor modelo optimizado fue '
        f'<strong>{best_opt}</strong> con un F1 CV de <strong>{best_cv:.4f}</strong>. '
        f'La combinación de GridSearchCV y RandomizedSearchCV permitió explorar '
        f'eficientemente el espacio de hiperparámetros.</p>'
        f'<h3>Clustering</h3>'
        f'<p>El análisis no supervisado con K-Means (K={k}) reveló '
        f'agrupaciones con un Silhouette Score de <strong>{sil:.4f}</strong>, '
        f'lo que indica una separación {"buena" if sil > 0.5 else "moderada" if sil > 0.25 else "débil"} '
        f'entre los clusters identificados.</p>'
        f'<h3>Limitaciones y Trabajo Futuro</h3>'
        f'<ul><li>El subsampling puede afectar la representatividad de los resultados</li>'
        f'<li>Se podría explorar feature engineering adicional (interacciones, polinomiales)</li>'
        f'<li>Considerar modelos de ensemble más avanzados (Stacking, Blending)</li>'
        f'<li>Implementar explicabilidad con SHAP para interpretar predicciones individuales</li></ul>'
        f'</div>'
    )


def build_referencias():
    refs = [
        ("scikit-learn", "https://scikit-learn.org/stable/"),
        ("Kedro Documentation", "https://docs.kedro.org/en/stable/"),
        ("CRISP-DM Methodology", "https://www.datascience-pm.com/crisp-dm-2/"),
        ("FIDE Ratings", "https://ratings.fide.com/"),
    ]
    items = "".join(f'<li><strong>{n}</strong> — <a href="{u}" style="color:#06b6d4">{u}</a></li>' for n, u in refs)
    return f'<h2>8. Referencias</h2><div class="card"><ul>{items}</ul></div>'


def build_footer():
    return (
        '<div class="footer">'
        '<p>Generado automáticamente por el pipeline <code>model_report</code> de Kedro · '
        'Proyecto FIDE Chess · SCY1101</p></div>'
    )
