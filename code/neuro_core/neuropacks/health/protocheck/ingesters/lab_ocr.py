from pathlib import Path
from neuro_core.neuro_ai.ocr.main import ocr_from_file
from neuro_core.neuropacks.health.protocheck.core.logger import get_logger

logger = get_logger(__name__)


def extract_lab_sheet_texts(file_path: str) -> list[str]:
    """
    Use OCR to extract text from a lab sheet image or PDF.
    Returns a list of strings, one per page.
    """
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    logger.info("Running OCR on file: %s", file_path)
    try:
        texts = ocr_from_file(file_path)
        logger.info("OCR completed. %d pages extracted.", len(texts))
        return texts
    except Exception as e:
        logger.error("OCR failed: %s", str(e))
        raise

