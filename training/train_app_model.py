import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

from app.preprocessing import AppCarPreprocessor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "Car_sale_ads.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "models" / "car_price_xgboost_price_target"
DEFAULT_LOOKUP_PATH = PROJECT_ROOT / "app" / "lookups" / "brand_model_lookup.csv"

APP_COLUMNS = [
    "Vehicle_brand",
    "Vehicle_model",
    "Production_year",
    "Mileage_km",
    "Fuel_type",
    "Transmission",
    "Power_HP",
    "Displacement_cm3",
    "Type",
    "Condition",
    "Drive",
    "Doors_number",
    "Colour",
    "Features",
]


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data = data[data["Currency"] == "PLN"]
    data = data[data["Price"] > 0]
    data["Log_Price"] = np.log(data["Price"])

    q1 = data["Log_Price"].quantile(0.25)
    q3 = data["Log_Price"].quantile(0.75)
    iqr = q3 - q1
    data = data[
        (data["Log_Price"] >= q1 - 1.5 * iqr)
        & (data["Log_Price"] <= q3 + 1.5 * iqr)
    ]

    data = data[data["Production_year"].between(1990, 2024)]
    data = data[data["Mileage_km"] > 0]
    data["Mileage_km"] = data["Mileage_km"].clip(upper=500000)
    data = data[data["Power_HP"].between(30, 700)]
    data.loc[~data["Displacement_cm3"].between(400, 8000), "Displacement_cm3"] = np.nan
    data = data[data["Doors_number"].between(2, 7)]

    return data


def build_model() -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocess", AppCarPreprocessor(target_is_log=False)),
            (
                "model",
                XGBRegressor(
                    objective="reg:squarederror",
                    eval_metric="rmse",
                    tree_method="hist",
                    n_estimators=800,
                    max_depth=6,
                    learning_rate=0.05,
                    reg_lambda=1.0,
                    subsample=0.85,
                    colsample_bytree=0.85,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def evaluate(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    return {
        "rmse": float(rmse),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def make_input_schema(data: pd.DataFrame, preprocessor: AppCarPreprocessor) -> dict:
    return {
        "currency": "PLN only",
        "required_fields": [
            "Vehicle_brand",
            "Vehicle_model",
            "Production_year",
            "Mileage_km",
            "Fuel_type",
            "Transmission",
            "Power_HP",
            "Displacement_cm3",
            "Type",
            "Condition",
            "Drive",
            "Doors_number",
        ],
        "optional_fields": ["Colour", "Features"],
        "numeric_ranges": {
            "Production_year": [1990, 2024],
            "Mileage_km": [1, 500000],
            "Power_HP": [30, 700],
            "Displacement_cm3": [400, 8000],
            "Doors_number": [2, 7],
        },
        "known_categories": {
            column: sorted(data[column].dropna().astype(str).unique().tolist() + ["__other__"])
            for column in preprocessor.categorical_columns
        },
        "top_equipment_options": preprocessor.equipment_labels_,
    }


def save_brand_model_lookup(data: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lookup = data[["Vehicle_brand", "Vehicle_model"]].dropna().copy()
    lookup["Vehicle_brand"] = lookup["Vehicle_brand"].astype(str).str.strip()
    lookup["Vehicle_model"] = lookup["Vehicle_model"].astype(str).str.strip()
    lookup = lookup[(lookup["Vehicle_brand"] != "") & (lookup["Vehicle_model"] != "")]
    lookup = lookup.groupby(["Vehicle_brand", "Vehicle_model"]).size().reset_index(name="count")
    lookup = lookup[lookup["count"] >= 5]
    lookup = lookup.sort_values(["Vehicle_brand", "count", "Vehicle_model"], ascending=[True, False, True])
    lookup.to_csv(output_path, index=False)


def train(data_path: Path, output_dir: Path, lookup_path: Path) -> None:
    raw_data = pd.read_csv(data_path)
    data = clean_data(raw_data)

    x_data = data[APP_COLUMNS]
    y_data = data["Price"]

    bins = pd.qcut(y_data, q=10, duplicates="drop")
    x_train, x_test, y_train, y_test = train_test_split(
        x_data,
        y_data,
        test_size=0.2,
        random_state=42,
        stratify=bins,
    )

    model = build_model()
    model.fit(x_train, y_train)

    train_metrics = evaluate(y_train, model.predict(x_train))
    test_metrics = evaluate(y_test, model.predict(x_test))

    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_dir / "model_pipeline_app.pkl")

    schema = make_input_schema(data, model.named_steps["preprocess"])
    (output_dir / "input_schema.json").write_text(
        json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    metrics = {
        "rows_after_cleaning": int(len(data)),
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "train": train_metrics,
        "test": test_metrics,
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    feature_columns = model.named_steps["preprocess"].output_columns_
    pd.DataFrame({"feature": feature_columns}).to_csv(
        output_dir / "feature_columns.csv", index=False
    )

    save_brand_model_lookup(data, lookup_path)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the Streamlit app car price model.")
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--lookup-path", type=Path, default=DEFAULT_LOOKUP_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train(args.data_path, args.output_dir, args.lookup_path)


if __name__ == "__main__":
    main()
