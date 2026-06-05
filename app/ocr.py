from pathlib import Path

import easyocr
import numpy as np
from PIL import Image

_reader = None


def get_reader():
    global _reader

    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)

    return _reader


def extract_text(image_path: str | Path) -> str:
    image_path = Path(image_path)

    image = Image.open(image_path).convert("RGB")
    image_array = np.array(image)

    reader = get_reader()
    result = reader.readtext(image_array, detail=0)

    return "\n".join(result)