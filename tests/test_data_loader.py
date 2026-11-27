import pandas as pd
import pytest
from src.validation import validate_results, normalize_columns
from src.data_loader import load_dataset, generate_demo

def valid():
    return pd.DataFrame({"gene_id":["g1","g2"],"baseMean":[1,2],"log2FoldChange":[2,-2],"lfcSE":[.1,.2],"stat":[20,-10],"pvalue":[.001,.02],"padj":[.01,.04]})

def test_alias_normalization():
    result, _ = validate_results(valid().rename(columns={"gene_id":"GeneID", "log2FoldChange":"log2FC", "padj":"FDR"}))
    assert list(result.gene_id) == ["g1","g2"]

def test_missing_required_column_errors():
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_results(valid().drop(columns="padj"))

def test_invalid_pvalues_become_missing_with_note():
    frame = valid(); frame.loc[0,"padj"] = 2
    result, notes = validate_results(frame)
    assert pd.isna(result.loc[0,"padj"])
    assert any("invalid padj" in n for n in notes)

def test_duplicate_and_missing_ids_are_reported():
    frame = pd.concat([valid(), valid().iloc[[0]]], ignore_index=True)
    frame.loc[2,"gene_id"] = None
    result, notes = validate_results(frame)
    assert len(result) == 2
    assert any("missing gene IDs" in n for n in notes)

def test_loader_optional_data():
    result, ann, expr, notes = load_dataset(valid())
    assert ann is None and expr is None and result.shape[0] == 2

def test_demo_is_reproducible_and_large_enough():
    first = generate_demo(); second = generate_demo()
    assert len(first[0]) >= 500
    pd.testing.assert_frame_equal(first[0], second[0])
