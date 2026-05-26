from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import pandas as pd


@dataclass(frozen=True)
class PredictionResult:
    predicted_price: float
    lower_bound: float
    upper_bound: float


class CarPricePredictor:
    def __init__(self, model_path: Path) -> None:
        if not model_path.exists():
            raise FileNotFoundError(f"Brak modelu: {model_path}")

        self.model = joblib.load(model_path)

    def predict(self, raw_input: dict[str, Any]) -> PredictionResult:
        data = pd.DataFrame([raw_input])
        price = float(self.model.predict(data)[0])
        price = max(price, 0.0)

        return PredictionResult(
            predicted_price=price,
            lower_bound=price * 0.85,
            upper_bound=price * 1.15,
        )
