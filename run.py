import sys
import webbrowser
import time
from pathlib import Path
from multiprocessing import Process
from tools.generate_car_options import generate_options as generate_car_options

ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"


def run_api():
    import uvicorn

    uvicorn.run("backend.api.main:app", host="0.0.0.0", port=8000)


def run_middleware():
    import uvicorn

    uvicorn.run("backend.middleware.main:app", host="0.0.0.0", port=8001)


def generate_options():
    options_path = FRONTEND_DIR / "car_options.json"
    print(f"Sprawdzanie {options_path}...")
    if not options_path.exists():
        print("Generowanie car_options.json...")
        generate_car_options(
            data_dir=ROOT / "data",
            output_dir=FRONTEND_DIR / "data",
        )
    else:
        print("car_options.json juz istnieje, pomijam generowanie.")


def check_models():
    models_dir = ROOT / "models"
    required = ["custom_model.pkl"]
    missing = [f for f in required if not (models_dir / f).exists()]
    if missing:
        print(f"Blad: Brak plikow modelu w {models_dir}:")
        for f in missing:
            print(f"  - {f}")
        print("Przeprowadz trening w notebooku przed uruchomieniem.")
        sys.exit(1)


if __name__ == "__main__":
    check_models()
    generate_options()

    print("\nUruchamianie API (port 8000) i Middleware (port 8001)...")
    print("Frontend: http://localhost:8001\n")

    api_proc = Process(target=run_api, daemon=True)
    mid_proc = Process(target=run_middleware, daemon=True)

    api_proc.start()
    mid_proc.start()

    time.sleep(2)
    webbrowser.open("http://localhost:8001")

    try:
        api_proc.join()
        mid_proc.join()
    except KeyboardInterrupt:
        print("\nZamykanie serwerow...")
        api_proc.terminate()
        mid_proc.terminate()
        api_proc.join()
        mid_proc.join()
        print("Zamknieto.")
