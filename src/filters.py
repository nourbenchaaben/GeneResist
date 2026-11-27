from __future__ import annotations
import numpy as np
import pandas as pd

def classify(frame: pd.DataFrame, padj_threshold=.05, lfc_threshold=1.0) -> pd.DataFrame:
    out = frame.copy()
    out["direction"] = np.select([out.log2FoldChange > 0, out.log2FoldChange < 0], ["Upregulated", "Downregulated"], default="No change")
    out["significant"] = out.padj.notna() & (out.padj < padj_threshold) & (out.log2FoldChange.abs() >= lfc_threshold)
    out["minus_log10_padj"] = -np.log10(out.padj.clip(lower=np.finfo(float).tiny))
    out.loc[out.padj.isna(), "minus_log10_padj"] = np.nan
    return out

def filter_genes(frame, query="", padj_threshold=.05, lfc_threshold=1.0, direction="All", annotation="All"):
    out = classify(frame, padj_threshold, lfc_threshold)
    out = out[out.significant]
    if query:
        searchable = [c for c in ("gene_id", "gene_name", "description", "annotation", "pathway", "GO_terms") if c in out]
        mask = pd.Series(False, index=out.index)
        for col in searchable: mask |= out[col].fillna("").astype(str).str.contains(query, case=False, regex=False)
        out = out.loc[mask]
    if direction != "All": out = out[out.direction == direction]
    if annotation == "Annotated": out = out[out.get("description", pd.Series(index=out.index, dtype=object)).notna()]
    if annotation == "Unannotated": out = out[out.get("description", pd.Series(index=out.index, dtype=object)).isna()]
    return out.sort_values("padj", na_position="last")

def evidence_class(row):
    annotated = pd.notna(row.get("description")) and bool(str(row.get("description")).strip())
    pathway = pd.notna(row.get("pathway")) and bool(str(row.get("pathway")).strip())
    if annotated and pathway: return "Statistical + annotation + pathway evidence"
    if pathway: return "Statistical + pathway evidence"
    if annotated: return "Statistical + functional annotation"
    return "Statistical evidence only"
