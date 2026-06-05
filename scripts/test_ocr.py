import easyocr
import numpy as np
from PIL import Image
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
image_path = PROJECT_ROOT / "data" / "sample_invoices" / "invoice_0.png"

print("PROJECT_ROOT:", PROJECT_ROOT)
print("IMAGE_PATH:", image_path)
print("FILE EXISTS:", image_path.exists())

if not image_path.exists():
    raise FileNotFoundError(f"File not found: {image_path}")

image = Image.open(image_path).convert("RGB")
image_array = np.array(image)

reader = easyocr.Reader(["en"], gpu=False)
result = reader.readtext(image_array, detail=0)

print("\n--- OCR RESULT ---\n")
print("\n".join(result))