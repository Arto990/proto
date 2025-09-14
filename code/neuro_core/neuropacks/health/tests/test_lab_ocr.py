import os
import pytest
from neuro_core.neuropacks.health.protocheck.ingesters.lab_ocr import extract_lab_sheet_texts

# Dummy test file – replace with a real one for accurate testing
TEST_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "lab_sample1.png")

@pytest.mark.skipif(not os.path.exists(TEST_FILE_PATH), reason="Test input file not found.")
def test_extract_lab_sheet_texts_returns_text():
    result = extract_lab_sheet_texts(TEST_FILE_PATH)

    assert result is not None, "Result should not be None"
    assert isinstance(result, (list, str, dict)), "Unexpected return type"
    if isinstance(result, list):
        assert all(isinstance(item, str) for item in result), "All list items should be strings"
    elif isinstance(result, dict):
        assert all(isinstance(v, str) for v in result.values()), "All dict values should be strings"
    elif isinstance(result, str):
        assert len(result) > 0, "Returned string should not be empty"
