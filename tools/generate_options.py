import json
import pandas as pd
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cleaned_data.csv"
LABELS_PATH = Path(__file__).resolve().parent.parent / "frontend" / "labels.json"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "frontend" / "car_options.json"


def load_labels():
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def pretty(val, mapping):
    return mapping.get(val, val.replace("_", " ").title() if "_" in val else val.title())


def generate_options():
    labels = load_labels()
    df = pd.read_csv(DATA_PATH)

    hierarchy = {}
    for (brand, model), group in df.groupby(["Vehicle_brand", "Vehicle_model"]):
        types = sorted(pretty(t, labels["type"]) for t in group["Type"].dropna().unique().tolist())
        if brand not in hierarchy:
            hierarchy[brand] = {}
        hierarchy[brand][str(model)] = types

    all_labels = {}
    for mapping in labels.values():
        all_labels.update(mapping)

    options = {
        "hierarchy": hierarchy,
        "transmissions": sorted(df["Transmission"].dropna().unique().tolist()),
        "fuel_types": sorted(pretty(f, labels["fuel"]) for f in df["Fuel_type"].dropna().unique().tolist()),
        "drives": sorted(pretty(d, labels["drive"]) for d in df["Drive"].dropna().unique().tolist()),
        "colours": sorted(pretty(c, labels["colour"]) for c in df["Colour"].dropna().unique().tolist()),
        "doors_numbers": sorted(df["Doors_number"].dropna().astype(int).unique().tolist()),
        "conditions": sorted(pretty(c, labels["condition"]) for c in df["Condition"].dropna().unique().tolist()),
        "labels_to_raw": {v: k for k, v in all_labels.items()},
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