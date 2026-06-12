import json
import pandas as pd
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cleaned_data.csv"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "frontend" / "car_options.json"


def generate_options():
    df = pd.read_csv(DATA_PATH)

    hierarchy = {}
    for (brand, model), group in df.groupby(["Vehicle_brand", "Vehicle_model"]):
        types = sorted(group["Type"].dropna().unique().tolist())
        if brand not in hierarchy:
            hierarchy[brand] = {}
        hierarchy[brand][str(model)] = types

    options = {
        "hierarchy": hierarchy,
        "transmissions": sorted(df["Transmission"].dropna().unique().tolist()),
        "fuel_types": sorted(df["Fuel_type"].dropna().unique().tolist()),
        "drives": sorted(df["Drive"].dropna().unique().tolist()),
        "colours": sorted(df["Colour"].dropna().unique().tolist()),
        "doors_numbers": sorted(df["Doors_number"].dropna().astype(int).unique().tolist()),
        "conditions": sorted(df["Condition"].dropna().unique().tolist()),
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(options, f, ensure_ascii=False, indent=2)

    print(f"Zapisano opcje do {OUTPUT_PATH}")
    print(f"  Marek: {len(hierarchy)}")
    total_models = sum(len(models) for models in hierarchy.values())
    print(f"  Modeli: {total_models}")
    print(f"  Typow paliwa: {len(options['fuel_types'])}")
    print(f"  Skrzyn biegow: {len(options['transmissions'])}")
    print(f"  Napedow: {len(options['drives'])}")
    print(f"  Kolorow: {len(options['colours'])}")


if __name__ == "__main__":
    generate_options()