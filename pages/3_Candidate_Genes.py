import streamlit as st
import pandas as pd
from src.page_utils import shared_controls, gene_table, ensure_state, footer
from src.filters import classify, evidence_class
from src.visualizations import expression_heatmap
from src.report_generator import csv_bytes

st.set_page_config(page_title="Candidate Genes | geneResist", layout="wide")
ensure_state()
st.title("Candidate Gene Explorer")
st.caption("Transparent evidence review. Candidate prioritization does not indicate causal or validated drought tolerance.")
if st.session_state.demo: st.warning("SYNTHETIC DEMO — simulated data and illustrative annotations only.")
frame = st.session_state.dataset
filtered, padj, lfc = shared_controls(frame, "candidate")
ann_filter = st.selectbox("Annotation availability", ["All", "Annotated", "Unannotated"])
if ann_filter != "All":
    description = filtered.get("description", pd.Series(index=filtered.index, dtype=object))
    filtered = filtered[description.notna() if ann_filter == "Annotated" else description.isna()]
st.write(f"{len(filtered):,} genes match these filters.")
view = classify(filtered, padj, lfc)
if not view.empty:
    view["evidence_class"] = view.apply(evidence_class, axis=1)
    cols = [c for c in ["gene_id", "gene_name", "log2FoldChange", "pvalue", "padj", "direction", "significant", "evidence_class"] if c in view]
    st.dataframe(view[cols], use_container_width=True, hide_index=True, height=340)
    st.download_button("Download filtered candidate table", csv_bytes(view[cols]), "geneResist_candidates.csv", "text/csv")
    gene = st.selectbox("Inspect a gene", view.gene_id.tolist())
    row = view[view.gene_id == gene].iloc[0]
    st.subheader(f"Gene profile · {gene}")
    stat_cols = st.columns(4)
    stat_cols[0].metric("log₂ fold change", f"{row.log2FoldChange:.3g}")
    stat_cols[1].metric("Adjusted p-value", "Missing" if pd.isna(row.padj) else f"{row.padj:.3g}")
    stat_cols[2].metric("Base mean", "Missing" if pd.isna(row.baseMean) else f"{row.baseMean:.3g}")
    stat_cols[3].metric("Direction", row.direction)
    st.markdown("**Statistical evidence**")
    st.write(f"p-value: {row.pvalue if pd.notna(row.pvalue) else 'Missing'} · adjusted p-value: {row.padj if pd.notna(row.padj) else 'Missing'} · Meets thresholds: {'Yes' if row.significant else 'No'}")
    st.markdown("**Functional annotation**")
    for key,label in [("gene_name","Gene name"),("description","Description"),("GO_terms","GO terms"),("pathway","Pathway"),("annotation_source","Annotation source"),("reference_url","External reference")]:
        value = row.get(key)
        if pd.isna(value) or str(value).strip() == "": value = "Annotation unavailable"
        if key == "reference_url" and value != "Annotation unavailable": st.markdown(f"[{value}]({value})")
        else: st.write(f"**{label}:** {value}")
    expr = st.session_state.expression
    if expr is not None:
        fig = expression_heatmap(expr, [gene])
        if fig: st.plotly_chart(fig, use_container_width=True)
else: st.info("No genes match the selected filters.")
st.caption("Evidence classes report which types of loaded evidence exist; no points are awarded and no tolerance prediction is made.")
footer()
