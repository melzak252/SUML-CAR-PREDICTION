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
with open(DATA_DIR / "types_pl.json", encoding="utf-8") as f:
    types_pl = json.load(f)
    types_pl_rev = {v: k for k, v in types_pl.items()}
with open(DATA_DIR / "drives_pl.json", encoding="utf-8") as f:
    drives_pl = json.load(f)
    drives_pl_rev = {v: k for k, v in drives_pl.items()}
with open(DATA_DIR / "colours_pl.json", encoding="utf-8") as f:
    kolory_pl = json.load(f)
    kolory_pl_rev = {v: k for k, v in kolory_pl.items()}

API_URL = "http://127.0.0.1:8000/predict"
FUEL_TYPES = ["Diesel", "Gasoline", "Gasoline + LPG"]
FUEL_TYPES_PL = {
    "Diesel": "Diesel",
    "Benzyna": "Gasoline",
    "Benzyna + LPG": "Gasoline + LPG",
}
TRANSMISSIONS = ["Manual", "Automatic"]
TRANSMISSIONS_PL = {"Manualna": "Manual", "Automatyczna": "Automatic"}
YEARS = list(range(1990, 2027))
PH = "---"

slownik = {}


def reset_downstream(from_key):
    cascade = ["manufacturer", "model", "type", "drive"]
    found = False
    for k in cascade:
        if found:
            st.session_state.pop(k, None)
        if k == from_key:
            found = True


def make_selectbox(label, options, key, disabled=False):
    options = list(options)
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
st.title("RevRate")
st.subheader("Inteligentna wycena samochodów")

r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    used = st.checkbox("Used", value=True)


r1c1, r1c2, r1c3 = st.columns(3)

with r1c1:
    manufacturer = make_selectbox("Marka", brands, "manufacturer")
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


def render_prediction(
    predicted_price: float, lower_bound: float, upper_bound: float
) -> None:
    price = f"{predicted_price:,.0f} PLN".replace(",", " ")
    low = f"{lower_bound:,.0f} PLN".replace(",", " ")
    high = f"{upper_bound:,.0f} PLN".replace(",", " ")

    with st.container(border=True):
        st.markdown("### Aktualna wycena")
        main_col, low_col, high_col = st.columns([1, 1, 1])
        main_col.metric("Szacowana cena", price)
        low_col.metric("Dolny zakres", low)
        high_col.metric("Górny zakres", high)
        st.caption(
            "Zakres jest orientacyjny i pokazuje około ±15% od predykcji modelu."
        )


mod_selected = model != PH
types_list = types_by_model.get(model, []) if mod_selected else []
types_list_pl = [types_pl_rev[t] for t in types_list] if mod_selected else []
drives_list = drives_by_model.get(model, []) if mod_selected else []
drives_list_pl = [drives_pl_rev[d] for d in drives_list] if mod_selected else []
with r1c3:
    type_pl_val = make_selectbox(
        "Typ nadwozia", types_list_pl, "type", disabled=not mod_selected
    )
    type_val = types_pl.get(type_pl_val, PH) if type_pl_val != PH else PH


r2c1, r2c2, r2c3 = st.columns(3)

with r2c1:
    drive_pl = make_selectbox(
        "Napęd", drives_list_pl, "drive", disabled=not mod_selected
    )
    drive = drives_pl.get(drive_pl, PH) if drive_pl != PH else PH

with r2c2:
    production_year = make_selectbox("Rok produkcji", YEARS, "year")

with r2c3:
    mileage = st.number_input(
        "Przebieg (w tys. km)",
        min_value=None,
        step=1,
        format="%d",
        placeholder="Wprowadź przebieg w tysiącach km (np. 150)",
    )

r3c1, r3c2, r3c3 = st.columns(3)

with r3c1:
    power = st.number_input(
        "Moc (w KM)",
        min_value=1,
        max_value=2000,
        value=150,
        step=1,
        format="%d",
    )

with r3c2:
    displacement = st.number_input(
        "Pojemność (w cm³)",
        min_value=1,
        max_value=9999,
        value=2000,
        step=1,
        format="%d",
    )

with r3c3:
    fuel_type_pl = make_selectbox("Typ paliwa", FUEL_TYPES_PL.keys(), "fuel")
    fuel_type = FUEL_TYPES_PL.get(fuel_type_pl, PH) if fuel_type_pl != PH else PH

r4c1, r4c2, r4c3 = st.columns(3)

with r4c1:
    transmission_pl = make_selectbox(
        "Transmission", TRANSMISSIONS_PL.keys(), "transmission"
    )
    transmission = (
        TRANSMISSIONS_PL.get(transmission_pl, PH) if transmission_pl != PH else PH
    )

with r4c2:
    doors_number = st.number_input(
        "Liczba drzwi",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
        format="%d",
    )

colours = kolory_pl.keys() if model != PH else colours
with r4c3:
    colour_pl = make_selectbox("Kolor", colours, "colour")
    colour = kolory_pl.get(colour_pl, PH) if colour_pl != PH else PH

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
price = st.session_state.get("predicted_price")
with btn_col3:
    if st.button("Oblicz cenę", disabled=not all_filled, type="primary"):
        try:
            resp = requests.post(API_URL, json=payload, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            price = result["predicted_price"]

            st.session_state["predicted_price"] = price
        except requests.exceptions.ConnectionError:
            st.error(
                "Nie można połączyć się z API. Upewnij się, że backend działa na http://127.0.0.1:8000"
            )
        except Exception as e:
            st.error(f"Error: {e}")

if price is not None:
    lower = price * 0.85
    upper = price * 1.15
    render_prediction(
        predicted_price=price,
        lower_bound=lower,
        upper_bound=upper,
    )
