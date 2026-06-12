# Frontend Streamlit - RevRate

## Files to create/modify

### 1. `requirements.txt` (edit)
Add `streamlit` to the list.

### 2. `front-end/generate_data.py` (new)
Python script that reads `data/cleaned_data.csv` and generates 5 JSON files:
- `front-end/data/brands.json` - sorted list of unique Vehicle_brand
- `front-end/data/models_by_brand.json` - dict brand -> [models]
- `front-end/data/types_by_model.json` - dict model -> [types]
- `front-end/data/drives_by_model.json` - dict model -> [drive types]
- `front-end/data/colours.json` - sorted list of unique Colour

### 3. `front-end/app.py` (new)
Main Streamlit application with:
- Title "RevRate - Car Price Prediction"
- 11 input fields:
  - **Manufacturer** (selectbox from brands.json, cascading to Model)
  - **Model** (selectbox from models_by_brand.json[manufacturer], disabled before Manufacturer selected)
  - **Type** (selectbox from types_by_model.json[model], disabled before Model selected)
  - **Drive** (selectbox from drives_by_model.json[model], disabled before Model selected)
  - **Production year** (selectbox, 1990-2026)
  - **Mileage** (number_input, min=1; displayed as "tys. km"; value * 1000 sent to API)
  - **Power** (number_input, min=1, max=2000)
  - **Displacement** (number_input, min=1, max=9999)
  - **Fuel type** (selectbox: Diesel, Gasoline, Gasoline + LPG)
  - **Transmission** (selectbox: Manual, Automatic)
  - **Doors number** (number_input, min=1, max=10)
  - **Colour** (selectbox from colours.json)
- Hidden/constant values: Condition="Used", voivodeship="unknown", CO2_emissions=None
- "Calculate price" button disabled until all 11 fields are filled
- On submit: POST to `http://localhost:8000/predict` with JSON payload
- Display predicted price in PLN

### 4. `front-end/data/` (created by generate_data.py)
Generated JSON files.

## Payload mapping to API

```python
{
    "Condition": "Used",
    "Vehicle_brand": manufacturer,
    "Vehicle_model": model,
    "Production_year": production_year,
    "Mileage_km": mileage * 1000,        # user enters in thousands
    "Power_HP": power,
    "Displacement_cm3": displacement,
    "Fuel_type": fuel_type,
    "CO2_emissions": None,
    "Drive": drive,
    "Transmission": transmission,
    "Type": type_,
    "Doors_number": doors_number,
    "Colour": colour,
    "voivodeship": "unknown",
}
```

## Usage

```bash
# Terminal 1: start API backend
.venv\Scripts\python src\revrate\api\app.py

# Terminal 2: generate data then run streamlit
.venv\Scripts\python front-end/generate_data.py
.venv\Scripts\python -m streamlit run front-end/app.py
```
