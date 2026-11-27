import streamlit as st
import pandas as pd
from .filters import classify, filter_genes
from .report_generator import DISCLAIMER
from .data_loader import load_demo

def ensure_state():
    """Initialize shared data when a user opens a multipage URL directly."""
    if "dataset" not in st.session_state:
        result, annotations, expression, metadata, notes = load_demo()
        st.session_state.update(dataset=result, annotations=annotations, expression=expression,
                                metadata=metadata, notes=notes, demo=True)

def shared_controls(df, key="filter"):
    a,b,c = st.columns([1.4,1,1])
    query = a.text_input("Search gene ID or annotation", key=f"{key}_query")
    padj = b.number_input("Adjusted p-value threshold", min_value=0.0, max_value=1.0, value=.05, step=.01, format="%.3f", key=f"{key}_padj")
    lfc = c.number_input("Minimum |log₂FC|", min_value=0.0, max_value=20.0, value=1.0, step=.25, key=f"{key}_lfc")
    direction = st.selectbox("Direction", ["All", "Upregulated", "Downregulated", "No change"], key=f"{key}_direction")
    result = filter_genes(df, query, padj, lfc, direction)
    return result, padj, lfc

def gene_table(df):
    view = classify(df)
    cols = [c for c in ("gene_id", "gene_name", "log2FoldChange", "pvalue", "padj", "direction", "significant", "description", "pathway") if c in view]
    return view[cols]

def disclaimer():
    st.caption(DISCLAIMER)

def footer():
    metadata = st.session_state.metadata
    st.divider()
    st.caption(f"geneResist MVP v0.1 · Source: {metadata.get('source_url', 'not supplied')} · {DISCLAIMER}")
