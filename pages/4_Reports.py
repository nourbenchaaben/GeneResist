import streamlit as st
from src.page_utils import shared_controls, gene_table, ensure_state, footer
from src.report_generator import research_summary
from src.report_generator import csv_bytes

st.set_page_config(page_title="Reports | geneResist", layout="wide")
ensure_state()
st.title("Research Reports")
st.caption("Export transparent summaries and tables for downstream analysis.")
if st.session_state.demo: st.warning("SYNTHETIC DEMO — exports contain simulated data and are not scientific findings.")
filtered, padj, lfc = shared_controls(st.session_state.dataset, "report")
table = gene_table(filtered)
st.metric("Genes in filtered export", f"{len(table):,}")
st.download_button("Download filtered gene table", csv_bytes(table), "geneResist_filtered_genes.csv", "text/csv")
full = gene_table(st.session_state.dataset)
st.download_button("Download complete differential-expression table", csv_bytes(full), "geneResist_all_results.csv", "text/csv")
if st.session_state.annotations is not None:
    annotated = st.session_state.dataset
    st.download_button("Download annotated gene table", csv_bytes(annotated), "geneResist_annotated_results.csv", "text/csv")
summary = research_summary(st.session_state.dataset, st.session_state.metadata, padj, lfc)
st.subheader("Research summary")
st.code(summary, language=None)
st.download_button("Download research summary", summary, "geneResist_research_summary.txt", "text/plain", type="primary")
footer()
