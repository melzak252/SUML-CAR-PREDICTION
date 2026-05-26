from typing import Any

import streamlit as st

from app.schema import category_options, numeric_range


DEFAULT_FEATURES = {"ABS", "Central locking", "Power steering"}


def render_sidebar() -> None:
    st.sidebar.title("Wycena samochodu")


def render_input_form(
    schema: dict[str, Any], brand_model_lookup: dict[str, list[str]]
) -> dict[str, Any]:
    st.subheader("Parametry samochodu")

    left, right = st.columns(2)

    with left:
        brands = sorted(brand_model_lookup) or ["Volkswagen", "BMW", "Audi"]
        default_brand_index = brands.index("Volkswagen") if "Volkswagen" in brands else 0
        vehicle_brand = st.selectbox(
            "Marka", brands, index=default_brand_index, key="vehicle_brand"
        )

        models_for_brand = brand_model_lookup.get(vehicle_brand, []) or ["Brak modeli"]
        default_model_index = models_for_brand.index("Golf") if "Golf" in models_for_brand else 0
        vehicle_model = st.selectbox(
            f"Model dla marki {vehicle_brand}",
            models_for_brand,
            index=default_model_index,
            key="vehicle_model",
        )

        year_min, year_max = numeric_range(schema, "Production_year")
        production_year = st.number_input(
            "Rok produkcji", year_min, year_max, 2018, key="production_year"
        )

        mileage_min, mileage_max = numeric_range(schema, "Mileage_km")
        mileage_km = st.number_input(
            "Przebieg [km]",
            mileage_min,
            mileage_max,
            120000,
            step=1000,
            key="mileage_km",
        )

        power_min, power_max = numeric_range(schema, "Power_HP")
        power_hp = st.number_input(
            "Moc [KM]", power_min, power_max, 150, step=5, key="power_hp"
        )

        displacement_min, displacement_max = numeric_range(schema, "Displacement_cm3")
        displacement_cm3 = st.number_input(
            "Pojemność [cm³]",
            displacement_min,
            displacement_max,
            1498,
            step=50,
            key="displacement_cm3",
        )

    with right:
        fuel_type = st.selectbox("Paliwo", category_options(schema, "Fuel_type"), key="fuel_type")
        transmission = st.selectbox(
            "Skrzynia", category_options(schema, "Transmission"), key="transmission"
        )
        body_type = st.selectbox("Typ nadwozia", category_options(schema, "Type"), key="body_type")
        condition = st.selectbox(
            "Stan", category_options(schema, "Condition"), index=1, key="condition"
        )
        drive = st.selectbox("Napęd", category_options(schema, "Drive"), key="drive")
        doors = st.selectbox(
            "Liczba drzwi", category_options(schema, "Doors_number"), index=2, key="doors"
        )
        colour = st.selectbox("Kolor", category_options(schema, "Colour"), key="colour")

    equipment_options = schema.get("top_equipment_options", [])
    selected_features = []
    if equipment_options:
        with st.expander("Wyposażenie - kliknij, żeby rozwinąć listę", expanded=False):
            for index, option in enumerate(equipment_options):
                key = f"feature_{index}"
                if key not in st.session_state:
                    st.session_state[key] = option in DEFAULT_FEATURES

            reset_left, reset_right = st.columns(2)
            if reset_left.button("Wyczyść wyposażenie"):
                for index in range(len(equipment_options)):
                    st.session_state[f"feature_{index}"] = False

            if reset_right.button("Przywróć domyślne"):
                for index, option in enumerate(equipment_options):
                    st.session_state[f"feature_{index}"] = option in DEFAULT_FEATURES

            feature_cols = st.columns(3)
            for index, option in enumerate(equipment_options):
                if feature_cols[index % 3].toggle(
                    option,
                    key=f"feature_{index}",
                ):
                    selected_features.append(option)

    return {
        "Vehicle_brand": vehicle_brand.strip(),
        "Vehicle_model": vehicle_model.strip(),
        "Production_year": int(production_year),
        "Mileage_km": int(mileage_km),
        "Fuel_type": fuel_type,
        "Transmission": transmission,
        "Power_HP": int(power_hp),
        "Displacement_cm3": int(displacement_cm3),
        "Type": body_type,
        "Condition": condition,
        "Drive": drive,
        "Doors_number": int(doors),
        "Colour": colour,
        "Features": ", ".join(selected_features),
    }


def default_car_input(
    schema: dict[str, Any], brand_model_lookup: dict[str, list[str]]
) -> dict[str, Any]:
    brands = sorted(brand_model_lookup) or ["Volkswagen"]
    vehicle_brand = "Volkswagen" if "Volkswagen" in brands else brands[0]
    models = brand_model_lookup.get(vehicle_brand, []) or ["Golf"]
    vehicle_model = "Golf" if "Golf" in models else models[0]

    return {
        "Vehicle_brand": vehicle_brand,
        "Vehicle_model": vehicle_model,
        "Production_year": 2018,
        "Mileage_km": 120000,
        "Fuel_type": _default_option(schema, "Fuel_type", "Gasoline"),
        "Transmission": _default_option(schema, "Transmission", "Manual"),
        "Power_HP": 150,
        "Displacement_cm3": 1498,
        "Type": _default_option(schema, "Type", "compact"),
        "Condition": _default_option(schema, "Condition", "Used"),
        "Drive": _default_option(schema, "Drive", "Front wheels"),
        "Doors_number": 5,
        "Colour": _default_option(schema, "Colour", "black"),
        "Features": ", ".join(sorted(DEFAULT_FEATURES)),
    }


def _default_option(schema: dict[str, Any], field_name: str, value: str) -> str:
    options = category_options(schema, field_name)
    return value if value in options else options[0]


def render_prediction(predicted_price: float, lower_bound: float, upper_bound: float) -> None:
    price = f"{predicted_price:,.0f} PLN".replace(",", " ")
    low = f"{lower_bound:,.0f} PLN".replace(",", " ")
    high = f"{upper_bound:,.0f} PLN".replace(",", " ")

    with st.container(border=True):
        st.markdown("### Aktualna wycena")
        main_col, low_col, high_col = st.columns([2, 1, 1])
        main_col.metric("Szacowana cena", price)
        low_col.metric("Dolny zakres", low)
        high_col.metric("Górny zakres", high)
        st.caption(
            "Zakres jest orientacyjny i pokazuje około ±15% od predykcji modelu."
        )
