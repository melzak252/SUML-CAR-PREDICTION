# RevRate - Predykcja ceny samochodu

Aplikacja do przewidywania cen samochodów na podstawie danych z polskiego rynku.

## Instalacja i uruchomienie

Dwuklik `scripts\windows\setup.bat` — instaluje Python 3.10, zależności, pobiera dataset i uruchamia `run.py`.

Pełna instalacja od zera (pobiera Git i Python, klonuje repo): `scripts\windows\deploy.bat`

`run.py` — uruchamia serwery:
localhost:8501 — Streamlit (frontend)
localhost:8001 — middleware (proxy do API)
localhost:8000 — API predykcji (XGBoost)