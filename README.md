# geneResist MVP v0.1

geneResist is a research dashboard for exploring precomputed differential-expression results and candidate-gene evidence for wheat drought-response studies. It keeps statistical results, annotations, provenance, and exploratory prioritization distinct. It does not run RNA-seq processing or claim that a candidate gene causes drought tolerance.

## MVP scope

- Overview and dataset design/provenance summary
- CSV loading for precomputed DESeq2 results, optional gene annotations, and optional normalized expression
- Volcano plot, sortable gene tables, filters, and an interactive expression heatmap
- Candidate profiles with explicit evidence categories
- CSV exports and a downloadable research summary
- Reproducible synthetic demo data, visibly labeled in the application
- Planned AI Research Assistant section only; no chatbot is implemented

## Technology

Python, Streamlit, pandas, NumPy, Plotly, and pytest.

## Install and run

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

## Project structure

```text
app.py                         Overview and dataset upload
pages/                         Dataset, analysis, candidate, and report pages
src/                           Validation, loading, filtering, charts, reports
data/demo/                     Explicitly synthetic example data
data/raw/                      Place local source files here (ignored by git)
data/processed/                Local derived files (ignored by git)
tests/                         Unit tests for core behavior
assets/                        Reserved for future brand assets
```

## Demo mode

The application starts with 600 reproducible, simulated rows using `DEMO_GENE_###` identifiers. Demo annotations are explicitly illustrative. They do not represent real genes, pathways, publications, accessions, or results and must not be used for scientific conclusions. Use **Reset to synthetic demo** in the sidebar to restore the demo after loading another dataset.

## Loading real data

From the Overview page, upload a DESeq2 results CSV with these required columns:

`gene_id, baseMean, log2FoldChange, lfcSE, stat, pvalue, padj`

Common aliases such as `GeneID`, `gene`, `log2FC`, `FDR`, and `adj_pvalue` are normalized. Invalid p-values are set to missing with a visible validation message; blank or duplicate gene IDs are excluded with a visible message. Optional annotation CSV should include `gene_id` and may include `gene_name`, `description`, `organism`, `chromosome`, `GO_terms`, `pathway`, `annotation_source`, and `reference_url`. Optional expression CSV should include `gene_id` plus one column per sample; the sample column names are read dynamically. Optional metadata JSON can supply dataset title, organism, stress, tissue, treatment/control, sample/replicate counts, accession, source URL, publication, experiment description, and analysis notes.

No files are uploaded to a server by this MVP. Data exists in the current Streamlit session. Review the displayed source and analysis notes before interpreting output.

## Researcher workflow

1. **Choose a starting point.** Explore the synthetic demo first, or upload a precomputed DESeq2 results CSV from the Overview page.
2. **Check the study context.** Open Dataset Explorer and confirm the organism, tissue, treatment/control, sample details, source, and validation messages. Supply metadata JSON when available.
3. **Explore differential expression.** In Expression Analysis, adjust the adjusted p-value and absolute log2 fold-change thresholds, review the volcano plot, and inspect the heatmap when normalized expression was supplied.
4. **Review candidate genes.** Search and filter in Candidate Genes. Read statistical evidence separately from gene annotation, GO terms, and pathway fields. Missing fields are shown as unavailable.
5. **Export and follow up.** Download filtered or complete tables and the research summary from Reports. Investigate prioritized candidates with external evidence and experimental validation before drawing biological conclusions.

For the synthetic demo, do not treat its simulated results or illustrative annotations as scientific findings.

## Scientific limitations

This application presents supplied precomputed differential-expression statistics; it does not run DESeq2. Threshold filters are exploratory. Annotation availability does not establish function, and pathway membership does not establish mechanism. Computational association does not prove causality or experimental validation. Prioritized genes require independent investigation and validation. Missing publication metadata is reported as missing rather than inferred.

## Roadmap

Potential next steps include richer metadata editing, validated public dataset ingestion, downloadable methods/provenance manifests, and an evidence-grounded assistant that cites only supplied results and verifiable literature. These are not implemented in this MVP.

## Tests

```bash
pytest
```
