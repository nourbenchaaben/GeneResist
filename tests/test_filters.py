import pandas as pd
from src.filters import classify, filter_genes, evidence_class
from src.report_generator import research_summary, csv_bytes

def sample():
    return pd.DataFrame({"gene_id":["up","down","weak","missing"],"baseMean":[5]*4,"log2FoldChange":[2,-2,.5,3],"lfcSE":[.2]*4,"stat":[1]*4,"pvalue":[.001,.01,.3,None],"padj":[.01,.04,.3,None]})

def test_significance_and_direction():
    out = classify(sample())
    assert list(out.direction) == ["Upregulated","Downregulated","Upregulated","Upregulated"]
    assert list(out.significant) == [True,True,False,False]

def test_threshold_filtering():
    out = filter_genes(sample(), padj_threshold=.05, lfc_threshold=1)
    assert set(out.gene_id) == {"up","down"}

def test_zero_padj_is_finite():
    frame = sample(); frame.loc[0,"padj"] = 0
    values = classify(frame).minus_log10_padj.dropna()
    assert values.map(lambda value: value != float("inf")).all()

def test_evidence_classification_uses_available_fields():
    assert evidence_class({"description":None,"pathway":None}) == "Statistical evidence only"
    assert evidence_class({"description":"Evidence","pathway":None}) == "Statistical + functional annotation"
    assert evidence_class({"description":"Evidence","pathway":"Pathway"}) == "Statistical + annotation + pathway evidence"

def test_summary_does_not_invent_publication():
    summary = research_summary(sample(), {"dataset_title":"Example"})
    assert "No publication metadata supplied" in summary
    assert "causality" in summary

def test_csv_export_round_trips_with_unicode_header():
    original = sample()[["gene_id", "log2FoldChange"]]
    restored = pd.read_csv(__import__("io").BytesIO(csv_bytes(original)))
    pd.testing.assert_frame_equal(original, restored)
