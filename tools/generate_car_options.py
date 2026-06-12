import json
from pathlib import Path

import pandas as pd


def generate_options(data_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_dir / "cleaned_data.csv")

    brands = sorted(df["Vehicle_brand"].dropna().unique().tolist())
    with open(output_dir / "brands.json", "w", encoding="utf-8") as f:
        json.dump(brands, f, ensure_ascii=False, indent=2)

    models_by_brand = {
        brand: sorted(
            df[df["Vehicle_brand"] == brand]["Vehicle_model"].dropna().unique().tolist()
        )
        for brand in brands
    }
    with open(output_dir / "models_by_brand.json", "w", encoding="utf-8") as f:
        json.dump(models_by_brand, f, ensure_ascii=False, indent=2)

    types_by_model = {
        model: sorted(
            df[df["Vehicle_model"] == model]["Type"].dropna().unique().tolist()
        )
        for model in df["Vehicle_model"].dropna().unique()
    }
    with open(output_dir / "types_by_model.json", "w", encoding="utf-8") as f:
        json.dump(types_by_model, f, ensure_ascii=False, indent=2)

    drives_by_model = {
        model: sorted(
            df[df["Vehicle_model"] == model]["Drive"].dropna().unique().tolist()
        )
        for model in df["Vehicle_model"].dropna().unique()
    }
    with open(output_dir / "drives_by_model.json", "w", encoding="utf-8") as f:
        json.dump(drives_by_model, f, ensure_ascii=False, indent=2)

    colours = sorted(df["Colour"].dropna().unique().tolist())
    with open(output_dir / "colours.json", "w", encoding="utf-8") as f:
        json.dump(colours, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    DATA_DIR = Path(__file__).parent.parent / "data"
    OUTPUT_DIR = Path(__file__).parent.parent / "frontend/data"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    generate_options(DATA_DIR / "car_data.csv", OUTPUT_DIR)
