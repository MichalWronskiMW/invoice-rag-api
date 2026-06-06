"""
Simple OCR test script.

Loads a sample invoice image and verifies that Tesseract OCR
returns readable text.
"""

from pathlib import Path

from app.ocr import extract_text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_PATH = PROJECT_ROOT / "data" / "sample_invoices" / "invoice_0.png"


def main() -> None:
    """Run OCR on a sample invoice and print the result."""
    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("IMAGE_PATH:", IMAGE_PATH)
    print("FILE EXISTS:", IMAGE_PATH.exists())

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"File not found: {IMAGE_PATH}")

    text = extract_text(IMAGE_PATH)

    print("\n--- OCR RESULT ---\n")
    print(text)


if __name__ == "__main__":
    main()