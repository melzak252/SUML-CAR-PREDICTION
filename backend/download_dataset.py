import os
import sys

os.environ.setdefault('KAGGLE_API_TOKEN', 'KGAT_bb7b3e08aa50d95c285f5ab611ba50ab')

try:
    import kaggle.api

    os.makedirs('data', exist_ok=True)

    print("Pobieranie datasetu...")
    kaggle.api.dataset_download_files('bartoszpieniak/poland-cars-for-sale-dataset', path='data', unzip=True)
    print("Pobrano do data/")

    print("\nPliki w data/:")
    for file in os.listdir('data'):
        print(f"  - {file}")

except ImportError:
    print("Brak pakietu kaggle. Zainstaluj: pip install kaggle")
    sys.exit(1)
except Exception as e:
    print(f"Blad: {e}")
    print("Upewnij sie ze masz:")
    print("  1. pip install kaggle")
    print("  2. KAGGLE_API_TOKEN ustawiony w srodowisku")
    sys.exit(1)