import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import BRAND_MODEL_LOOKUP_PATH, MODEL_PATH, SCHEMA_PATH
from app.lookups import load_brand_model_lookup
from app.predictor import CarPricePredictor
from app.schema import load_schema
from app.ui import default_car_input, render_input_form, render_prediction, render_sidebar


@st.cache_resource(show_spinner="Ładowanie modelu...")
def get_predictor() -> CarPricePredictor:
    return CarPricePredictor(MODEL_PATH)


@st.cache_data(show_spinner=False)
def get_schema() -> dict:
    return load_schema(SCHEMA_PATH)


@st.cache_data(show_spinner=False)
def get_brand_model_lookup() -> dict[str, list[str]]:
    return load_brand_model_lookup(BRAND_MODEL_LOOKUP_PATH)


def show_current_result() -> None:
    if "last_prediction" not in st.session_state:
        st.info("Aktualna wycena pojawi się tutaj po uzupełnieniu poprawnych danych.")
        return

    prediction = st.session_state["last_prediction"]
    raw_input = st.session_state["last_input"]
    render_prediction(
        prediction["predicted_price"],
        prediction["lower_bound"],
        prediction["upper_bound"],
    )
    with st.expander("Aktualne dane auta"):
        st.json(raw_input)


def save_prediction(predictor: CarPricePredictor, raw_input: dict) -> None:
    result = predictor.predict(raw_input)
    st.session_state["last_input"] = raw_input
    st.session_state["last_prediction"] = {
        "predicted_price": result.predicted_price,
        "lower_bound": result.lower_bound,
        "upper_bound": result.upper_bound,
    }


def prepare_start_prediction(
    predictor: CarPricePredictor, schema: dict, brand_model_lookup: dict[str, list[str]]
) -> None:
    if "last_prediction" in st.session_state:
        return
    raw_input = default_car_input(schema, brand_model_lookup)
    save_prediction(predictor, raw_input)


def input_has_sense(raw_input: dict, schema: dict) -> bool:
    if raw_input["Vehicle_model"] == "Brak modeli":
        return False

    ranges = schema.get("numeric_ranges", {})
    checks = {
        "Production_year": raw_input["Production_year"],
        "Mileage_km": raw_input["Mileage_km"],
        "Power_HP": raw_input["Power_HP"],
        "Displacement_cm3": raw_input["Displacement_cm3"],
        "Doors_number": raw_input["Doors_number"],
    }

    for field_name, value in checks.items():
        lower, upper = ranges.get(field_name, [None, None])
        if lower is not None and value < lower:
            return False
        if upper is not None and value > upper:
            return False

    return True


def main() -> None:
    st.set_page_config(page_title="Wycena samochodu", page_icon="🚗", layout="wide")
    st.title("🚗 Prototyp wyceny samochodu")
    st.write("Podaj parametry auta, a model oszacuje cenę w PLN.")
    render_sidebar()

    try:
        schema = get_schema()
        brand_model_lookup = get_brand_model_lookup()
        predictor = get_predictor()
    except Exception as error:
        st.error(f"Nie udało się uruchomić aplikacji: {error}")
        st.stop()

    prepare_start_prediction(predictor, schema, brand_model_lookup)

    result_box = st.container()
    with result_box:
        show_current_result()

    st.caption("Wycena aktualizuje się automatycznie po zmianie poprawnych parametrów.")
    st.divider()

    raw_input = render_input_form(schema, brand_model_lookup)

    if not input_has_sense(raw_input, schema):
        st.warning("Popraw parametry auta, żeby model mógł przeliczyć wycenę.")
        return

    if raw_input != st.session_state.get("last_input"):
        save_prediction(predictor, raw_input)
        st.rerun()


if __name__ == "__main__":
    main()
