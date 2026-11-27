import streamlit as st
from src.page_utils import shared_controls, gene_table, ensure_state, footer
from src.visualizations import volcano, expression_heatmap
from src.report_generator import csv_bytes

st.set_page_config(page_title="Expression Analysis | geneResist", layout="wide")
ensure_state()
st.title("Differential Expression Analysis")
st.caption("Explore precomputed differential-expression statistics. Thresholds are visible and adjustable.")
if st.session_state.demo: st.warning("SYNTHETIC DEMO — simulated values only; do not use for scientific conclusions.")
frame = st.session_state.dataset
filtered, padj, lfc = shared_controls(frame, "analysis")
st.plotly_chart(volcano(frame, padj, lfc), use_container_width=True, config={"displaylogo":False})
st.caption(f"Threshold guides show padj = {padj:g} and log₂FC = ±{lfc:g}. Missing adjusted p-values are omitted from the y axis.")
st.subheader("Filtered results")
table = gene_table(filtered)
st.dataframe(table, use_container_width=True, hide_index=True, height=360)
st.download_button("Download filtered CSV", csv_bytes(table), "geneResist_filtered_genes.csv", "text/csv")
st.subheader("Expression heatmap")
expr = st.session_state.expression
if expr is None:
    st.info("No normalized expression matrix is loaded. Upload a CSV with gene_id and one column per sample to enable this view.")
else:
    mode = st.radio("Gene selection", ["Top filtered genes", "Significant genes", "Search genes"], horizontal=True)
    if mode == "Top filtered genes":
        n = st.slider("Number of genes", 5, 50, 20)
        genes = filtered.sort_values("padj").gene_id.head(n).tolist()
    elif mode == "Significant genes":
        genes = filtered[filtered.significant].sort_values("padj").gene_id.head(50).tolist()
    else:
        options = expr.gene_id.astype(str).tolist()
        selected = st.multiselect("Select gene IDs", options, default=options[:5])
        genes = selected[:50]
    fig = expression_heatmap(expr, genes)
    if fig: st.plotly_chart(fig, use_container_width=True, config={"displaylogo":False})
    else: st.info("No expression rows matched the selected genes.")
footer()
