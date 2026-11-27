from __future__ import annotations
import pandas as pd
from .filters import classify

DISCLAIMER = "geneResist supports exploratory research and candidate prioritization. Differential-expression results and computational annotations do not establish causality or experimental validation. Prioritized genes should be independently investigated and validated."

def csv_bytes(frame: pd.DataFrame) -> bytes:
    """Serialize a table for a UTF-8 CSV download, including a BOM for spreadsheet compatibility."""
    return frame.to_csv(index=False).encode("utf-8-sig")

def research_summary(frame: pd.DataFrame, metadata: dict, padj_threshold=.05, lfc_threshold=1.0) -> str:
    d = classify(frame, padj_threshold, lfc_threshold)
    sig = d[d.significant]
    lines = ["geneResist research summary", "=" * 28, "", f"Dataset: {metadata.get('dataset_title', 'Not supplied')}",
      f"Organism: {metadata.get('organism', 'Not supplied')}", f"Stress: {metadata.get('stress_type', 'Not supplied')}",
      f"Tissue: {metadata.get('tissue', 'Not supplied')}", f"Treatment: {metadata.get('treatment', 'Not supplied')}",
      f"Control: {metadata.get('control_condition', 'Not supplied')}", f"Samples: {metadata.get('number_of_samples', 'Not supplied')}",
      f"Accession: {metadata.get('accession', 'Not supplied')}", f"Source: {metadata.get('source_url', 'Not supplied')}",
      f"Publication: {metadata.get('publication', 'No publication metadata supplied')}", "", f"Genes analyzed: {len(d)}",
      f"Significantly upregulated: {int((sig.direction == 'Upregulated').sum())}",
      f"Significantly downregulated: {int((sig.direction == 'Downregulated').sum())}",
      f"Thresholds: adjusted p-value < {padj_threshold:g}; |log2FC| ≥ {lfc_threshold:g}", "", "Top candidates by adjusted p-value:"]
    top = sig.sort_values("padj").head(10)
    lines.extend([f"- {r.gene_id}: log2FC={r.log2FoldChange:.3g}, padj={r.padj:.3g}" for r in top.itertuples()])
    if top.empty: lines.append("- No genes meet the selected thresholds.")
    lines.extend(["", "Limitations: Results depend on the supplied precomputed analysis. Annotation and pathway fields are not validation; computational association does not establish causality.", "", DISCLAIMER])
    return "\n".join(lines)
