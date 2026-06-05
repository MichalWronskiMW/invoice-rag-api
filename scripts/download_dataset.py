from datasets import load_dataset
from pathlib import Path

OUTPUT_DIR = Path("data/sample_invoices")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

dataset = load_dataset(
    "katanaml-org/invoices-donut-data-v1",
    split="train"
)

print(f"Liczba rekordów: {len(dataset)}")

for i in range(10):
    sample = dataset[i]

    image = sample["image"]

    image.save(
        OUTPUT_DIR / f"invoice_{i}.png"
    )

    print(f"Zapisano invoice_{i}.png")