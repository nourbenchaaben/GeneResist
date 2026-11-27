from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .validation import validate_annotations, validate_expression, validate_results

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "data" / "demo"


def read_csv(source) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        return source.copy()
    return pd.read_csv(source)


def load_dataset(results, annotations=None, expression=None):
    result, notes = validate_results(read_csv(results))
    annotation = None
    expr = None
    if annotations is not None:
        annotation, extra = validate_annotations(read_csv(annotations)); notes.extend(extra)
        missing = len(set(result.gene_id) - set(annotation.gene_id))
        if missing:
            notes.append(f"{missing} result gene(s) have no matching annotation; annotation fields will remain blank.")
        result = result.merge(annotation, on="gene_id", how="left", suffixes=("", "_annotation"))
    if expression is not None:
        expr, extra = validate_expression(read_csv(expression)); notes.extend(extra)
        missing = len(set(result.gene_id) - set(expr.gene_id))
        if missing:
            notes.append(f"{missing} result gene(s) have no matching expression row.")
    return result, annotation, expr, notes


def load_demo():
    results, annotations, expression, notes = load_dataset(
        DEMO / "deseq2_results.csv", DEMO / "gene_annotations.csv", DEMO / "normalized_expression.csv"
    )
    metadata = json.loads((DEMO / "dataset_metadata.json").read_text(encoding="utf-8"))
    return results, annotations, expression, metadata, notes


def generate_demo(seed: int = 17, n: int = 600):
    """Create reproducible, explicitly synthetic data for local demo mode."""
    rng = np.random.default_rng(seed)
    ids = [f"DEMO_GENE_{i:03d}" for i in range(1, n + 1)]
    lfc = np.clip(rng.normal(0, 1.15, n), -4, 4)
    p = np.clip(10 ** rng.uniform(-6, 0, n), 1e-8, 1)
    p[rng.choice(n, size=n // 5, replace=False)] = rng.uniform(.2, 1, n // 5)
    # Benjamini-Hochberg adjusted values, kept within [0,1].
    order = np.argsort(p); ranked = p[order] * n / np.arange(1, n + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    padj = np.empty(n); padj[order] = np.clip(ranked, 0, 1)
    results = pd.DataFrame({"gene_id": ids, "baseMean": rng.lognormal(5, 1, n), "log2FoldChange": lfc,
        "lfcSE": rng.uniform(.1, .8, n), "stat": lfc / rng.uniform(.1, .8, n), "pvalue": p, "padj": padj})
    annotations = pd.DataFrame({"gene_id": ids[:45], "gene_name": [f"Illustrative locus {i:02d}" for i in range(1, 46)],
        "description": ["Illustrative synthetic annotation; not a real gene." for _ in range(45)],
        "organism": "Synthetic wheat-like demo", "chromosome": "Illustrative", "GO_terms": "Illustrative only",
        "pathway": "Illustrative pathway", "annotation_source": "Synthetic demo annotation", "reference_url": ""})
    samples = ["Control_1", "Control_2", "Control_3", "Stress_1", "Stress_2", "Stress_3"]
    expr = pd.DataFrame({"gene_id": ids, **{s: rng.lognormal(5 + (lfc if s.startswith("Stress") else 0) * np.log(2), .35, n) for s in samples}})
    metadata = {"dataset_title": "Synthetic drought response demo", "organism": "Wheat (synthetic demo)",
      "scientific_name": "Triticum aestivum (label context only)", "stress_type": "Drought (simulated)", "tissue": "Not specified",
      "treatment": "Synthetic drought-like condition", "control_condition": "Synthetic control", "number_of_samples": 6,
      "biological_replicates": 3, "accession": "Not supplied", "source_url": "Not supplied",
      "publication": "No publication metadata supplied", "experiment_description": "All values and annotations are simulated for interface demonstration.",
      "analysis_notes": "Synthetic values; not suitable for scientific conclusions.", "data_status": "SYNTHETIC DEMO"}
    return results, annotations, expr, metadata, []
