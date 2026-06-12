import json
import pandas as pd
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cleaned_data.csv"
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "frontend" / "car_options.json"

TYPE_LABELS = {
    "city_cars": "City Cars",
    "small_cars": "Small Cars",
    "station_wagon": "Station Wagon",
    "compact": "Compact",
    "sedan": "Sedan",
    "SUV": "SUV",
    "coupe": "Coupe",
    "convertible": "Convertible",
    "minivan": "Minivan",
}

DRIVE_LABELS = {
    "Front wheels": "Front-Wheel Drive",
    "Rear wheels": "Rear-Wheel Drive",
    "4x4 (permanent)": "4x4 Permanent",
    "4x4 (attached automatically)": "4x4 Auto",
    "4x4 (attached manually)": "4x4 Manual",
}

FUEL_LABELS = {
    "Gasoline": "Benzyna",
    "Diesel": "Diesel",
    "Gasoline + LPG": "Benzyna + LPG",
}

CONDITION_LABELS = {
    "New": "Nowy",
    "Used": "Uzywany",
}

COLOUR_LABELS = {
    "beige": "Bezowy",
    "black": "Czarny",
    "blue": "Niebieski",
    "brown": "Brazowy",
    "burgundy": "Bordowy",
    "golden": "Zloty",
    "gray": "Szary",
    "green": "Zielony",
    "other": "Inny",
    "red": "Czerwony",
    "silver": "Srebrny",
    "violet": "Fioletowy",
    "white": "Bialy",
    "yellow": "Zolty",
}


def pretty(val, mapping):
    return mapping.get(val, val.title() if "_" not in val else val.replace("_", " ").title())


ALL_LABELS = {**TYPE_LABELS, **DRIVE_LABELS, **FUEL_LABELS, **CONDITION_LABELS, **COLOUR_LABELS}


def generate_options():
    df = pd.read_csv(DATA_PATH)

    hierarchy = {}
    for (brand, model), group in df.groupby(["Vehicle_brand", "Vehicle_model"]):
        types = sorted(pretty(t, TYPE_LABELS) for t in group["Type"].dropna().unique().tolist())
        if brand not in hierarchy:
            hierarchy[brand] = {}
        hierarchy[brand][str(model)] = types

    options = {
        "hierarchy": hierarchy,
        "transmissions": sorted(df["Transmission"].dropna().unique().tolist()),
        "fuel_types": sorted(pretty(f, FUEL_LABELS) for f in df["Fuel_type"].dropna().unique().tolist()),
        "drives": sorted(pretty(d, DRIVE_LABELS) for d in df["Drive"].dropna().unique().tolist()),
        "colours": sorted(pretty(c, COLOUR_LABELS) for c in df["Colour"].dropna().unique().tolist()),
        "doors_numbers": sorted(df["Doors_number"].dropna().astype(int).unique().tolist()),
        "conditions": sorted(pretty(c, CONDITION_LABELS) for c in df["Condition"].dropna().unique().tolist()),
        "labels_to_raw": {v: k for k, v in ALL_LABELS.items()},
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