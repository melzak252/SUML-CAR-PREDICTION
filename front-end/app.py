import datetime
import json
from pathlib import Path

import requests
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "brands.json", encoding="utf-8") as f:
    brands = json.load(f)
with open(DATA_DIR / "models_by_brand.json", encoding="utf-8") as f:
    models_by_brand = json.load(f)
with open(DATA_DIR / "types_by_model.json", encoding="utf-8") as f:
    types_by_model = json.load(f)
with open(DATA_DIR / "drives_by_model.json", encoding="utf-8") as f:
    drives_by_model = json.load(f)
with open(DATA_DIR / "colours.json", encoding="utf-8") as f:
    colours = json.load(f)

API_URL = "http://127.0.0.1:8000/predict"
FUEL_TYPES = ["Diesel", "Gasoline", "Gasoline + LPG"]
TRANSMISSIONS = ["Manual", "Automatic"]
YEARS = list(range(1990, 2027))
PH = "---"


def reset_downstream(from_key):
    cascade = ["manufacturer", "model", "type", "drive"]
    found = False
    for k in cascade:
        if found:
            st.session_state.pop(k, None)
        if k == from_key:
            found = True


def make_selectbox(label, options, key, disabled=False):
    if disabled:
        st.selectbox(label, [PH], disabled=True, key=key)
        return PH
    if len(options) == 1:
        return st.selectbox(label, options, key=key)
    display = [PH] + options
    if key not in st.session_state or st.session_state[key] not in display:
        st.session_state[key] = PH
    return st.selectbox(label, display, key=key)


st.set_page_config(page_title="RevRate", page_icon="🚗")
st.title("OTOCENAZATOMOTO")

r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    used = st.checkbox("Used", value=True)


r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    manufacturer = make_selectbox("Manufacturer", brands, "manufacturer")
    if (
        st.session_state.get("_prev_man") is not None
        and manufacturer != st.session_state["_prev_man"]
    ):
        reset_downstream("manufacturer")
        st.session_state["_prev_man"] = manufacturer
        st.rerun()
    st.session_state["_prev_man"] = manufacturer

man_selected = manufacturer != PH
models_list = models_by_brand.get(manufacturer, []) if man_selected else []

with r1c2:
    model = make_selectbox("Model", models_list, "model", disabled=not man_selected)
    if (
        man_selected
        and st.session_state.get("_prev_mod") is not None
        and model != st.session_state["_prev_mod"]
    ):
        reset_downstream("model")
        st.session_state["_prev_mod"] = model
        st.rerun()
    st.session_state["_prev_mod"] = model

mod_selected = model != PH
types_list = types_by_model.get(model, []) if mod_selected else []
drives_list = drives_by_model.get(model, []) if mod_selected else []

with r1c3:
    type_val = make_selectbox("Type", types_list, "type", disabled=not mod_selected)

r2c1, r2c2, r2c3 = st.columns(3)

with r2c1:
    drive = make_selectbox("Drive", drives_list, "drive", disabled=not mod_selected)

with r2c2:
    production_year = make_selectbox("Production year", YEARS, "year")

with r2c3:
    mileage = st.number_input(
        "Mileage (in kkm)",
        min_value=None,
        step=1,
        format="%d",
        placeholder="Enter mileage",
    )

r3c1, r3c2, r3c3 = st.columns(3)

with r3c1:
    power = st.number_input(
        "Power (in hp)",
        min_value=1,
        max_value=2000,
        value=150,
        step=1,
        format="%d",
    )

with r3c2:
    displacement = st.number_input(
        "Displacement (in cm³)",
        min_value=1,
        max_value=9999,
        value=2000,
        step=1,
        format="%d",
    )

with r3c3:
    fuel_type = make_selectbox("Fuel type", FUEL_TYPES, "fuel")

r4c1, r4c2, r4c3 = st.columns(3)

with r4c1:
    transmission = make_selectbox("Transmission", TRANSMISSIONS, "transmission")

with r4c2:
    doors_number = st.number_input(
        "Doors number",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
        format="%d",
    )

with r4c3:
    colour = make_selectbox("Colour", colours, "colour")

all_filled = all(
    [
        manufacturer != PH,
        model != PH,
        type_val != PH,
        drive != PH,
        production_year != PH,
        mileage not in (None, 0),
        power not in (None, 0),
        displacement not in (None, 0),
        fuel_type != PH,
        transmission != PH,
        doors_number not in (None, 0),
        colour != PH,
    ]
)

payload = {
    "Condition": "Used" if used else "New",
    "Vehicle_brand": manufacturer,
    "Vehicle_model": model,
    "Mileage_km": mileage * 1000,
    "Power_HP": power,
    "Displacement_cm3": displacement,
    "Fuel_type": fuel_type,
    "Drive": drive,
    "Transmission": transmission,
    "Type": type_val,
    "Doors_number": doors_number,
    "Colour": colour,
    "car_age": (
        datetime.datetime.now().year - production_year if production_year != PH else PH
    ),
    "mileage_per_year": (
        (mileage * 1000) / (datetime.datetime.now().year - production_year)
        if production_year != PH
        else PH
    ),
    "power_to_displacement": power / displacement if displacement != 0 else 0,
    "age_x_mileage": (
        (datetime.datetime.now().year - production_year) * mileage
        if production_year != PH
        else PH
    ),
}

btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 1])
with btn_col3:
    if st.button("Calculate price", disabled=not all_filled, type="primary"):
        try:
            resp = requests.post(API_URL, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            st.success(f"Predicted price: **{result['predicted_price']:,.2f} PLN**")
        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to API. Make sure the backend is running on http://127.0.0.1:8000"
            )
        except Exception as e:
            st.error(f"Error: {e}")

with st.expander("Aktualne dane auta"):
    st.json(payload)
