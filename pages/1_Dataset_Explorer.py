import streamlit as st
import pandas as pd
from src.page_utils import ensure_state, footer

st.set_page_config(page_title="Dataset Explorer | geneResist", layout="wide")
ensure_state()
st.title("Dataset Explorer")
st.caption("Review study design, provenance and available files before exploring results.")
meta = st.session_state.metadata
if st.session_state.demo: st.warning("SYNTHETIC DEMO — simulated values and illustrative annotations only.")
st.subheader(meta.get("dataset_title", "Dataset"))
st.dataframe(pd.DataFrame([(key, str(value)) for key, value in meta.items()], columns=["Metadata field", "Value"]), hide_index=True, use_container_width=True)
st.subheader("Loaded data")
a,b,c = st.columns(3)
a.metric("DE results", f"{len(st.session_state.dataset):,} genes")
b.metric("Annotation rows", "Available" if st.session_state.annotations is not None else "Not loaded")
c.metric("Expression matrix", "Available" if st.session_state.expression is not None else "Not loaded")
for note in st.session_state.notes: st.info(note)
footer()
