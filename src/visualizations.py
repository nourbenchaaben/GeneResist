import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

GREEN = "#1f5b45"

def volcano(frame, padj_threshold=.05, lfc_threshold=1.0):
    d = frame.copy()
    d["minus_log10_padj"] = -np.log10(d.padj.clip(lower=np.finfo(float).tiny))
    d.loc[d.padj.isna(), "minus_log10_padj"] = np.nan
    d["group"] = np.where(d.padj < padj_threshold, np.where(d.log2FoldChange >= lfc_threshold, "Upregulated", np.where(d.log2FoldChange <= -lfc_threshold, "Downregulated", "Significant, below fold-change threshold")), "Not significant / unavailable")
    hover = [c for c in ("gene_id", "gene_name", "log2FoldChange", "pvalue", "padj", "description") if c in d]
    fig = px.scatter(d, x="log2FoldChange", y="minus_log10_padj", color="group", hover_data=hover,
        color_discrete_map={"Upregulated":"#cf765e", "Downregulated":"#416f94", "Significant, below fold-change threshold":"#b8a36a", "Not significant / unavailable":"#aeb8b2"},
        labels={"log2FoldChange":"log₂ fold change", "minus_log10_padj":"−log₁₀(adjusted p-value)", "group":"Result"})
    fig.update_layout(template="plotly_white", height=450, margin=dict(l=10,r=10,t=24,b=10), legend_title_text="")
    fig.add_hline(y=-np.log10(padj_threshold), line_dash="dash", line_color="#829087")
    fig.add_vline(x=lfc_threshold, line_dash="dash", line_color="#829087"); fig.add_vline(x=-lfc_threshold, line_dash="dash", line_color="#829087")
    return fig

def expression_heatmap(expr: pd.DataFrame, genes: list[str]):
    d = expr[expr.gene_id.isin(genes)].set_index("gene_id")
    if d.empty: return None
    vals = d.astype(float)
    z = (vals - vals.mean(axis=1).values[:, None]) / vals.std(axis=1).replace(0, 1).values[:, None]
    fig = go.Figure(go.Heatmap(z=z, x=list(vals.columns), y=list(vals.index), colorscale="RdBu_r", zmid=0, colorbar_title="Row z-score", hoverongaps=False))
    fig.update_layout(template="plotly_white", height=max(300, min(850, len(genes)*24)), margin=dict(l=10,r=10,t=20,b=10), xaxis_title="Sample", yaxis_title="Gene ID")
    return fig
