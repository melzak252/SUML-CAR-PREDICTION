"""Unpack the zipped Car Sale dataset into data/."""

import zipfile
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
ZIP_PATH = DATA_DIR / "Car_sale_ads.zip"
CSV_PATH = DATA_DIR / "Car_sale_ads.csv"


def main():
    """Extract Car_sale_ads.zip if the CSV does not exist."""
    if CSV_PATH.exists():
        print(f"Dataset juz istnieje: {CSV_PATH}")
        return

    if not ZIP_PATH.exists():
        print(f"Blad: Nie znaleziono {ZIP_PATH}")
        print("Upewnij sie, ze plik Car_sale_ads.zip jest w katalogu data/")
        raise SystemExit(1)

    print("Wypakowywanie datasetu...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(DATA_DIR)
    print(f"Wypakowano do {DATA_DIR}")


if __name__ == "__main__":
    main()
