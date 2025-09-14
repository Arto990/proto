import argparse
from neuro_core.neuropacks.health.protocheck.ingesters.lab_ocr import extract_lab_sheet_texts


def main():
    parser = argparse.ArgumentParser(description="Run OCR on a lab sheet file (image or PDF).")
    parser.add_argument("--file", required=True, help="Path to the lab sheet image or PDF.")
    args = parser.parse_args()

    texts = extract_lab_sheet_texts(args.file)
    print("----- OCR OUTPUT -----")
    for idx, page in enumerate(texts, 1):
        print(f"\n--- Page {idx} ---\n{page}")


if __name__ == "__main__":
    main()

