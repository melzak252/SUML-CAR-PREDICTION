import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "frontend/data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_DIR / "cleaned_data.csv")

brands = sorted(df["Vehicle_brand"].dropna().unique().tolist())
with open(OUTPUT_DIR / "brands.json", "w", encoding="utf-8") as f:
    json.dump(brands, f, ensure_ascii=False, indent=2)

models_by_brand = {
    brand: sorted(
        df[df["Vehicle_brand"] == brand]["Vehicle_model"].dropna().unique().tolist()
    )
    for brand in brands
}
with open(OUTPUT_DIR / "models_by_brand.json", "w", encoding="utf-8") as f:
    json.dump(models_by_brand, f, ensure_ascii=False, indent=2)

types_by_model = {
    model: sorted(
        df[df["Vehicle_model"] == model]["Type"].dropna().unique().tolist()
    )
    for model in df["Vehicle_model"].dropna().unique()
}
with open(OUTPUT_DIR / "types_by_model.json", "w", encoding="utf-8") as f:
    json.dump(types_by_model, f, ensure_ascii=False, indent=2)

drives_by_model = {
    model: sorted(
        df[df["Vehicle_model"] == model]["Drive"].dropna().unique().tolist()
    )
    for model in df["Vehicle_model"].dropna().unique()
}
with open(OUTPUT_DIR / "drives_by_model.json", "w", encoding="utf-8") as f:
    json.dump(drives_by_model, f, ensure_ascii=False, indent=2)

colours = sorted(df["Colour"].dropna().unique().tolist())
with open(OUTPUT_DIR / "colours.json", "w", encoding="utf-8") as f:
    json.dump(colours, f, ensure_ascii=False, indent=2)
