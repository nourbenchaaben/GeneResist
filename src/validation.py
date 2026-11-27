from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = ["gene_id", "baseMean", "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"]
ALIASES = {
    "gene": "gene_id", "geneid": "gene_id", "gene_id": "gene_id", "id": "gene_id",
    "log2fc": "log2FoldChange", "log2_fold_change": "log2FoldChange",
    "adjusted_pvalue": "padj", "adj_pvalue": "padj", "fdr": "padj", "qvalue": "padj",
    "p_value": "pvalue", "p-value": "pvalue", "base_mean": "baseMean", "lfc_se": "lfcSE",
}


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize common DESeq2 column aliases without silently dropping columns."""
    out = frame.copy()
    normalized = {}
    for col in out.columns:
        key = str(col).strip().lower().replace(" ", "_")
        normalized[col] = ALIASES.get(key, col)
    out = out.rename(columns=normalized)
    if out.columns.duplicated().any():
        dupes = out.columns[out.columns.duplicated()].tolist()
        raise ValueError(f"Column aliases resolve to duplicate columns: {', '.join(map(str, dupes))}.")
    return out


def validate_results(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    if frame.empty:
        raise ValueError("The differential-expression file is empty.")
    out = normalize_columns(frame)
    missing = [c for c in REQUIRED_COLUMNS if c not in out.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    notes: list[str] = []
    out["gene_id"] = out["gene_id"].astype("string").str.strip()
    blank = out["gene_id"].isna() | out["gene_id"].eq("")
    if blank.any():
        notes.append(f"{int(blank.sum())} row(s) have missing gene IDs and were excluded.")
        out = out.loc[~blank].copy()
    duplicate = out["gene_id"].duplicated(keep="first")
    if duplicate.any():
        notes.append(f"{int(duplicate.sum())} duplicate gene ID row(s) were excluded; the first row was retained.")
        out = out.loc[~duplicate].copy()
    if out.empty:
        raise ValueError("No rows with usable gene IDs remain.")
    for col in REQUIRED_COLUMNS[1:]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in ("pvalue", "padj"):
        invalid = out[col].notna() & ~out[col].between(0, 1)
        if invalid.any():
            notes.append(f"{int(invalid.sum())} invalid {col} value(s) outside [0, 1] were set to missing.")
            out.loc[invalid, col] = float("nan")
    return out.reset_index(drop=True), notes


def validate_annotations(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    out = normalize_columns(frame)
    if "gene_id" not in out.columns:
        raise ValueError("Annotation file must contain a gene_id column (or supported alias).")
    out["gene_id"] = out["gene_id"].astype("string").str.strip()
    return out.dropna(subset=["gene_id"]).drop_duplicates("gene_id", keep="first"), []


def validate_expression(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    out = normalize_columns(frame)
    if "gene_id" not in out.columns:
        raise ValueError("Expression file must contain a gene_id column (or supported alias).")
    out["gene_id"] = out["gene_id"].astype("string").str.strip()
    samples = [c for c in out.columns if c != "gene_id"]
    if not samples:
        raise ValueError("Expression file must contain at least one sample column.")
    for col in samples:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out.dropna(subset=["gene_id"]).drop_duplicates("gene_id", keep="first"), []
