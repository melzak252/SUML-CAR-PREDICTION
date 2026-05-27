# SUML Car Price Prediction

Prosty prototyp aplikacji do wyceny samochodu. Użytkownik wybiera parametry auta, a aplikacja automatycznie szacuje cenę w PLN przy użyciu modelu XGBoost.

## Uruchomienie

Utwórz środowisko wirtualne:

```powershell
python -m venv .venv
```

Aktywuj środowisko:

```powershell
.venv\Scripts\Activate.ps1
```

Zainstaluj zależności:

```powershell
python -m pip install -r requirements.txt
```

Skopiuj konfigurację:

```powershell
Copy-Item .env.example .env
```

Uruchom aplikację:

```powershell
.venv\Scripts\streamlit.exe run app\streamlit_app.py
```

## Pipeline modelu

Kod pokazujący skąd bierze się model jest w:

```text
training/train_app_model.py
```

Pipeline czyści dane, trenuje model XGBoost, zapisuje model, schema i lookup marek/modeli.

Żeby odtworzyć model, potrzebny jest plik danych w `data/Car_sale_ads.csv`, a potem można uruchomić:

```powershell
.venv\Scripts\python.exe training\train_app_model.py
```

## Struktura

```text
app/          # kod aplikacji Streamlit
models/       # zapisany model i schema
training/     # pipeline treningowy modelu
requirements.txt
.env.example
```

Model aplikacyjny jest dodany do repozytorium, więc po instalacji zależności aplikacja powinna działać od razu.
