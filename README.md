# RevRate - Predykcja ceny samochodu

Aplikacja do przewidywania cen samochodow na podstawie danych z polskiego rynku. Wykorzystuje model XGBoost wytrenowany na danych ogloszeniowych, serwowany przez FastAPI z interfejsem Streamlit.

## Architektura

```
data/                   # Dane wejsciowe (Car_sale_ads.zip)
notebooks/              # Notebooki Jupyter: EDA, czyszczenie, trening
models/                 # Wytrenowany model (custom_model.pkl)
backend/
  api/main.py           # API predykcji XGBoost (port 8000)
  middleware/main.py     # Proxy API + dane pochodne (port 8001)
  tools/                # Generowanie opcji, rozpakowanie datasetu
frontend/
  web_app.py            # Interfejs Streamlit (port 8501)
  car_options.json      # Listy marek, modeli, typow
  labels.json           # Mapowania etykiet surowych na ladne
scripts/
  windows/              # Skrypty instalacyjne dla Windows
  linux/                # Skrypty instalacyjne dla Linux
run.py                  # Punkt wejscia - uruchamia wszystkie serwery
```

Przeplyw danych: **Streamlit** → (POST /predict) → **Middleware** → (POST /predict) → **API (XGBoost)**

## Wymagania systemowe

Instalatory (`deploy.bat` / `deploy.sh`) pobieraja wszystko automatycznie — nie potrzebujesz Pythona ani Gita na komputerze.

- **Windows**: PowerShell 5.1+ (wbudowany)
- **Linux**: `bash`, `curl`, `tar` (dostepne domyslnie na kazdej dystrybucji)
- 2 GB RAM (model XGBoost)
- 300 MB miejsca na dysku

## Pelna instalacja od zera

Oba skrypty dzialaja tak samo: pobieraja portable Python + repo, tworza .venv, instaluja zaleznosci, czyszcza pliki tymczasowe, uruchamiaja aplikacje.

### Windows
```batch
scripts\windows\deploy.bat
```

### Linux (klon repo)
```bash
chmod +x scripts/linux/deploy.sh && bash scripts/linux/deploy.sh
```

### Linux (bez Gita — jedna komenda)
```bash
curl -fSL -o deploy.sh https://raw.githubusercontent.com/melzak252/SUML-CAR-PREDICTION/deployment/scripts/linux/deploy.sh && chmod +x deploy.sh && bash deploy.sh
```

## Szybkie uruchomienie (gdy .venv juz istnieje)

### Windows
```batch
scripts\windows\setup.bat
```

### Linux
```bash
bash scripts/linux/setup.sh
```

## Porty

| Port    | Serwis     | Opis                    |
|---------|------------|-------------------------|
| `:8501` | Streamlit  | Interfejs uzytkownika   |
| `:8001` | Middleware | Proxy + cechy pochodne  |
| `:8000` | API        | Predykcja XGBoost       |

## Dane wejsciowe

Formularz Streamlit przyjmuje:
- **Marka, Model, Typ nadwozia** — wybierane kaskadowo
- **Rok produkcji** — 1990-2026
- **Moc (KM)** — liczba calkowita > 0
- **Przebieg (km)** — liczba calkowita >= 0
- **Pojemnosc (cm3)** — liczba calkowita > 0
- **Naped, Paliwo, Skrzynia, Kolor, Stan, Liczba drzwi** — listy wyboru

Wynik: szacowana cena w PLN z orientacyjnym zakresem ±15%.

## Tresowanie modelu

Notebooki w `notebooks/` (uruchamiac w kolejnosci):
1. `eda.ipynb` — analiza eksploracyjna danych
2. `dataset_cleaning.ipynb` — czyszczenie i przygotowanie danych
3. `model_training.ipynb` — trenowanie modelu XGBoost

## Wymagania Python

Zobacz `requirements.txt` — glowny plik zaleznosci.

## Licencja

MIT — zobacz plik `LICENSE`.
