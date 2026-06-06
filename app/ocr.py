from pathlib import Path

import pytesseract
from PIL import Image


def extract_text(image_path: str | Path) -> str:
    """
    Extract text from an image using Tesseract OCR.

    Args:
        image_path: Path to the image file.

    Returns:
        Extracted text as a string.
    """
    image_path = Path(image_path)

    with Image.open(image_path) as image:
        image = image.convert("RGB")

        text = pytesseract.image_to_string(
            image,
            lang="eng",
        )

    return text.strip()