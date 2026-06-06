from pathlib import Path

from PIL import Image
import pytesseract


def extract_text(image_path: str | Path) -> str:
    image_path = Path(image_path)

    image = Image.open(image_path).convert("RGB")

    text = pytesseract.image_to_string(
        image,
        lang="eng",
    )

    return text.strip()