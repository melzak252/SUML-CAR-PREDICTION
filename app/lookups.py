from pathlib import Path

import pandas as pd


def load_brand_model_lookup(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}

    lookup = pd.read_csv(path)
    result = {}
    for brand, group in lookup.groupby("Vehicle_brand"):
        result[str(brand)] = group["Vehicle_model"].astype(str).tolist()
    return result
