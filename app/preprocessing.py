import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


DATASET_YEAR = 2023


def clean_feature_list(text: object) -> list[str]:
    if pd.isna(text):
        return []
    cleaned = str(text).replace("[", "").replace("]", "")
    cleaned = cleaned.replace("'", "").replace('"', "")
    return [item.strip() for item in cleaned.split(",") if item.strip()]


class AppCarPreprocessor(BaseEstimator, TransformerMixin):
    numeric_columns = (
        "Production_year",
        "Mileage_km",
        "Power_HP",
        "Displacement_cm3",
        "car_age",
        "mileage_per_year",
        "power_to_displacement",
        "age_x_mileage",
    )
    categorical_columns = (
        "Condition",
        "Fuel_type",
        "Transmission",
        "Type",
        "Drive",
        "Doors_number",
        "Colour",
    )
    target_encoded_columns = ("Brand_Model", "Vehicle_brand")

    def __init__(
        self,
        equipment_top_n: int = 80,
        categorical_min_count: int = 30,
        target_is_log: bool = False,
    ) -> None:
        self.equipment_top_n = equipment_top_n
        self.categorical_min_count = categorical_min_count
        self.target_is_log = target_is_log

    def fit(self, x_data: pd.DataFrame, y_data: pd.Series | np.ndarray):
        prepared = self._prepare_base_frame(x_data)
        target = np.asarray(y_data, dtype=float)
        if not self.target_is_log:
            target = np.log(np.clip(target, 1.0, None))
        target_series = pd.Series(target, index=prepared.index)

        self.numeric_medians_ = {}
        for column in self.numeric_columns:
            value = pd.to_numeric(prepared[column], errors="coerce").median()
            self.numeric_medians_[column] = 0.0 if pd.isna(value) else float(value)

        self.category_modes_ = {}
        self.category_levels_ = {}
        for column in self.categorical_columns:
            self.category_modes_[column] = self._mode(prepared[column])
            filled = prepared[column].fillna(self.category_modes_[column]).astype(str)
            counts = filled.value_counts()
            levels = counts[counts >= self.categorical_min_count].index.tolist()
            self.category_levels_[column] = sorted(levels + ["__other__"])

        self.global_target_mean_ = float(target_series.mean())
        self.target_maps_ = {}
        for column in self.target_encoded_columns:
            self.target_maps_[column] = target_series.groupby(prepared[column].astype(str)).mean()

        equipment_counts: dict[str, int] = {}
        for labels in prepared["Features"].apply(clean_feature_list):
            for label in labels:
                equipment_counts[label] = equipment_counts.get(label, 0) + 1
        sorted_equipment = sorted(equipment_counts.items(), key=lambda item: item[1], reverse=True)
        self.equipment_labels_ = [label for label, _ in sorted_equipment[: self.equipment_top_n]]
        self.output_columns_ = self._output_columns()
        return self

    def transform(self, x_data: pd.DataFrame) -> pd.DataFrame:
        prepared = self._prepare_base_frame(x_data)
        output: dict[str, pd.Series] = {}

        for column in self.numeric_columns:
            output[column] = pd.to_numeric(prepared[column], errors="coerce").fillna(
                self.numeric_medians_[column]
            )

        for column in self.target_encoded_columns:
            output[f"{column}_TargetEncoded"] = prepared[column].astype(str).map(
                self.target_maps_[column]
            ).fillna(self.global_target_mean_)

        for column in self.categorical_columns:
            filled = prepared[column].fillna(self.category_modes_[column]).astype(str)
            known = set(self.category_levels_[column]) - {"__other__"}
            grouped = filled.where(filled.isin(known), "__other__")
            for level in self.category_levels_[column]:
                output[f"{column}__{level}"] = (grouped == level).astype(int)

        feature_sets = prepared["Features"].apply(lambda value: set(clean_feature_list(value)))
        for label in self.equipment_labels_:
            output[f"Feature__{label}"] = feature_sets.apply(lambda labels: int(label in labels))

        frame = pd.DataFrame(output, index=prepared.index)
        return frame.reindex(columns=self.output_columns_, fill_value=0)

    def _prepare_base_frame(self, x_data: pd.DataFrame) -> pd.DataFrame:
        prepared = x_data.copy()
        text_columns = [
            "Vehicle_brand",
            "Vehicle_model",
            "Condition",
            "Fuel_type",
            "Transmission",
            "Type",
            "Drive",
            "Colour",
            "Features",
        ]
        for column in text_columns:
            if column not in prepared.columns:
                prepared[column] = np.nan

        prepared["Vehicle_brand"] = prepared["Vehicle_brand"].fillna("unknown")
        prepared["Vehicle_model"] = prepared["Vehicle_model"].fillna("")
        prepared["Brand_Model"] = (
            prepared["Vehicle_brand"].astype(str) + " " + prepared["Vehicle_model"].astype(str)
        ).str.strip()

        for column in [
            "Production_year",
            "Mileage_km",
            "Power_HP",
            "Displacement_cm3",
            "Doors_number",
        ]:
            if column not in prepared.columns:
                prepared[column] = np.nan
            prepared[column] = pd.to_numeric(prepared[column], errors="coerce")

        prepared["car_age"] = (DATASET_YEAR - prepared["Production_year"]).clip(lower=0)
        prepared["mileage_per_year"] = prepared["Mileage_km"] / prepared["car_age"].clip(lower=1)
        prepared["power_to_displacement"] = np.where(
            prepared["Displacement_cm3"] > 0,
            prepared["Power_HP"] / prepared["Displacement_cm3"],
            np.nan,
        )
        prepared["age_x_mileage"] = prepared["car_age"] * prepared["Mileage_km"]
        prepared["Doors_number"] = prepared["Doors_number"].round().astype("Int64").astype(str)
        return prepared

    def _output_columns(self) -> list[str]:
        columns = list(self.numeric_columns)
        columns += [f"{column}_TargetEncoded" for column in self.target_encoded_columns]
        for column in self.categorical_columns:
            columns += [f"{column}__{level}" for level in self.category_levels_[column]]
        columns += [f"Feature__{label}" for label in self.equipment_labels_]
        return columns

    @staticmethod
    def _mode(series: pd.Series) -> str:
        mode = series.dropna().astype(str).mode()
        return "unknown" if mode.empty else str(mode.iloc[0])
