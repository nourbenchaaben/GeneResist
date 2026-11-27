from __future__ import annotations

import json
import streamlit as st
import pandas as pd

from src.data_loader import load_dataset, load_demo, generate_demo
from src.filters import classify
from src.report_generator import DISCLAIMER

st.set_page_config(page_title="geneResist | Research workspace", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
:root { --forest:#174D39; --sage:#E7EFE9; --ink:#172D25; --muted:#455B50; --paper:#F5F7F4; --line:#C9D6CD; --accent:#176B4D; }
.stApp { background:var(--paper); color:var(--ink); }
.stApp, .stApp p, .stApp li, .stApp label, .stApp [data-testid="stMarkdownContainer"] { color:var(--ink); }
[data-testid="stSidebar"] { background:#E7EFE9; border-right:1px solid var(--line); }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color:#213D31; }
[data-testid="stSidebarNav"] { display:none; }
[data-testid="stSidebar"] h1 { color:var(--forest); font-size:1.45rem; letter-spacing:-.04em; }
.eyebrow { color:var(--forest); font-size:.75rem; text-transform:uppercase; letter-spacing:.13em; font-weight:700; }
.hero { padding:1.4rem 0 .8rem; }
.hero h1 { font-size:2.15rem; letter-spacing:-.04em; margin:.25rem 0; color:#123B2B; }
.muted, [data-testid="stCaptionContainer"] { color:var(--muted) !important; }
.panel { border:1px solid var(--line); background:#FFFFFF; padding:1rem 1.1rem; border-radius:12px; color:var(--ink); }
[data-testid="stMetric"] { background:#FFFFFF; border:1px solid var(--line); border-radius:12px; padding:.8rem 1rem; }
[data-testid="stMetricLabel"] p { color:#455B50 !important; font-weight:600; }
[data-testid="stMetricValue"] { color:#123B2B !important; font-weight:700; }
.stButton button, .stDownloadButton button { border-radius:8px; border:1px solid #176B4D; color:#174D39; background:#FFFFFF; font-weight:650; }
.stButton button:hover, .stDownloadButton button:hover { border-color:#0C4E37; color:#0C4E37; background:#E7EFE9; }
.stButton button[kind="primary"], .stFormSubmitButton button { background:#176B4D !important; color:#FFFFFF !important; border:1px solid #176B4D !important; }
.stButton button[kind="primary"] p, .stFormSubmitButton button p { color:#FFFFFF !important; }
input, textarea, [data-baseweb="select"] > div { background:#FFFFFF !important; color:#172D25 !important; border-color:#9FB3A5 !important; }
div[data-testid="stAlert"] { border-radius:10px; color:#172D25 !important; }
div[data-testid="stAlert"] p { color:#172D25 !important; }
.workflow { border:1px solid #C9D6CD; border-top:4px solid #176B4D; border-radius:10px; padding:.85rem .9rem; background:#FFFFFF; min-height:126px; }
.workflow .step-number { color:#176B4D; font-weight:800; font-size:.78rem; letter-spacing:.1em; }
.workflow .step-title { color:#123B2B; font-weight:750; margin:.3rem 0; }
.workflow .step-copy { color:#455B50; font-size:.88rem; line-height:1.4; }
@media(max-width:700px){ .hero h1{font-size:1.65rem;} }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DISCLAIMER_SHORT = "geneResist supports exploratory research and candidate prioritization. Differential-expression results and computational annotations do not establish causality or experimental validation. Prioritized genes should be independently investigated and validated."

if "dataset" not in st.session_state:
    result, annotations, expr, metadata, notes = load_demo()
    st.session_state.update(dataset=result, annotations=annotations, expression=expr, metadata=metadata, notes=notes, demo=True)

with st.sidebar:
    st.markdown("# geneResist")
    st.caption("AI-Powered Bioinformatics for Climate-Resilient Agriculture")
    st.divider()
    st.markdown("**Workspace**")
    st.page_link("app.py", label="Overview")
    st.page_link("pages/1_Dataset_Explorer.py", label="Dataset Explorer")
    st.page_link("pages/2_Expression_Analysis.py", label="Expression Analysis")
    st.page_link("pages/3_Candidate_Genes.py", label="Candidate Genes")
    st.page_link("pages/4_Reports.py", label="Reports")
    st.divider()
    st.caption("CURRENT DATASET")
    st.write(st.session_state.metadata.get("dataset_title", "Uploaded dataset"))
    st.caption("ACTIVE STRESS")
    st.write(st.session_state.metadata.get("stress_type", "Not specified"))
    if st.button("Reset to synthetic demo", use_container_width=True):
        result, annotations, expr, metadata, notes = load_demo()
        st.session_state.update(dataset=result, annotations=annotations, expression=expr, metadata=metadata, notes=notes, demo=True)
        st.rerun()

df = classify(st.session_state.dataset)
meta = st.session_state.metadata
st.markdown('<div class="hero"><div class="eyebrow">Research workspace · Wheat · Drought</div><h1>Explore expression evidence</h1><div class="muted">Turn precomputed differential-expression results into a transparent, visual research workflow.</div></div>', unsafe_allow_html=True)
if st.session_state.demo:
    st.warning("SYNTHETIC DEMO MODE — all displayed data and annotations are simulated for interface demonstration. Do not use for scientific conclusions.", icon="⚠️")
else:
    st.info("User-provided dataset. Verify source and analysis methods before interpreting results.")

st.subheader("Researcher workflow")
st.caption("A practical path from data upload to a reviewable research export.")
steps = [
    ("01", "Choose data", "Start with the synthetic demo or upload precomputed DESeq2 results."),
    ("02", "Check the study", "Review conditions, provenance, sample details, and validation notes."),
    ("03", "Explore results", "Set adjusted p-value and fold-change thresholds; inspect the volcano plot and optional heatmap."),
    ("04", "Review candidates", "Search genes and distinguish statistical evidence from functional annotation."),
    ("05", "Export and validate", "Download tables and a summary, then investigate candidates with independent evidence."),
]
workflow_cols = st.columns(5)
for col, (number, title, copy) in zip(workflow_cols, steps):
    with col:
        st.markdown(f'<div class="workflow"><div class="step-number">STEP {number}</div><div class="step-title">{title}</div><div class="step-copy">{copy}</div></div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
sig = df[df.significant]
col1.metric("Genes analyzed", f"{len(df):,}")
col2.metric("Significant · up", f"{int((sig.direction == 'Upregulated').sum()):,}")
col3.metric("Significant · down", f"{int((sig.direction == 'Downregulated').sum()):,}")
col4.metric("Annotations available", f"{int(df.get('description', pd.Series(dtype=object)).notna().sum()):,}")

left, right = st.columns([1.3, 1])
with left:
    st.subheader("Dataset overview")
    st.write(meta.get("experiment_description", "No experiment description supplied."))
    details = {"Organism":meta.get("organism", "Not supplied"), "Tissue":meta.get("tissue", "Not supplied"), "Treatment":meta.get("treatment", "Not supplied"), "Control":meta.get("control_condition", "Not supplied"), "Samples":meta.get("number_of_samples", "Not supplied"), "Biological replicates":meta.get("biological_replicates", "Not supplied"), "Accession":meta.get("accession", "Not supplied"), "Publication":meta.get("publication", "No publication metadata supplied")}
    st.dataframe(pd.DataFrame([(key, str(value)) for key, value in details.items()], columns=["Study field", "Value"]), hide_index=True, use_container_width=True)
with right:
    st.subheader("Analysis snapshot")
    st.caption("Default exploratory thresholds · padj < 0.05 · |log₂FC| ≥ 1")
    st.write(f"{len(sig):,} genes meet both selected thresholds.")
    st.write("Prioritization classifies available evidence. It does not predict drought tolerance.")
    st.markdown('<div class="panel"><b>AI Research Assistant — Planned Feature</b><br><span class="muted">Future responses will be grounded in differential-expression results, annotations and verified literature.</span></div>', unsafe_allow_html=True)

st.subheader("Load your own dataset")
st.caption("Upload precomputed DESeq2 results. Annotation and normalized expression files are optional. Required results columns: gene_id, baseMean, log2FoldChange, lfcSE, stat, pvalue, padj.")
with st.form("upload_dataset"):
    results_file = st.file_uploader("Differential-expression results CSV", type="csv", key="results_upload")
    annotation_file = st.file_uploader("Gene annotations CSV (optional)", type="csv", key="annotation_upload")
    expression_file = st.file_uploader("Normalized expression CSV (optional)", type="csv", key="expression_upload")
    metadata_file = st.file_uploader("Dataset metadata JSON (optional)", type="json", key="metadata_upload")
    submitted = st.form_submit_button("Load dataset", type="primary")
if submitted:
    if not results_file:
        st.error("Choose a differential-expression results CSV first.")
    else:
        try:
            results, ann, expr, notes = load_dataset(results_file, annotation_file, expression_file)
            newmeta = {"dataset_title":"Uploaded dataset", "organism":"Not supplied", "stress_type":"Not specified", "tissue":"Not supplied", "treatment":"Not supplied", "control_condition":"Not supplied", "number_of_samples":"Not supplied", "biological_replicates":"Not supplied", "accession":"Not supplied", "source_url":"Not supplied", "publication":"No publication metadata supplied", "experiment_description":"User-provided precomputed differential-expression data.", "data_status":"USER PROVIDED"}
            if metadata_file:
                supplied = json.load(metadata_file)
                if not isinstance(supplied, dict): raise ValueError("Metadata JSON must contain an object.")
                newmeta.update(supplied)
            st.session_state.update(dataset=results, annotations=ann, expression=expr, metadata=newmeta, notes=notes, demo=False)
            st.success(f"Loaded {len(results):,} genes.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not load dataset: {exc}")
for note in st.session_state.notes:
    st.warning(note)

st.divider()
st.caption(f"geneResist MVP v0.1 · Source: {meta.get('source_url', 'not supplied')} · {DISCLAIMER_SHORT}")
