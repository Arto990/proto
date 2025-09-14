from PIL import Image
from pdf2image import convert_from_path
import easyocr
import numpy as np

reader = easyocr.Reader(["en", "fr"])


def pdf_to_images(pdf_path: str):
    """Convert a PDF file to a list of images."""
    images = convert_from_path(pdf_path)
    return images


def ocr_from_file(file_path: str) -> list[str]:
    """Perform OCR on a file (image or PDF) and return the extracted text."""
    if file_path.lower().endswith(".pdf"):
        images = pdf_to_images(file_path)
        if not images:
            raise ValueError("No images found in the PDF file.")
    else:
        images = [Image.open(file_path).convert("RGB")]

    pages = []
    for img in images:
        img = np.array(img)
        results = reader.readtext(img)
        full_text = ""
        for bbox, text, prob in results:
            full_text += f"{text}\n"
        pages.append(full_text.strip())

    return pages