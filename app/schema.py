import json
from pathlib import Path
from typing import Any


def load_schema(schema_path: Path) -> dict[str, Any]:
    if not schema_path.exists():
        raise FileNotFoundError(f"Brak pliku schema: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def category_options(schema: dict[str, Any], field_name: str) -> list[str]:
    options = schema.get("known_categories", {}).get(field_name, [])
    return [option for option in options if option != "__other__"]


def numeric_range(schema: dict[str, Any], field_name: str) -> tuple[int, int]:
    lower, upper = schema.get("numeric_ranges", {}).get(field_name, [0, 1])
    return int(lower), int(upper)
