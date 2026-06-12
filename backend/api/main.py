import joblib
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"

app = FastAPI(title="Car Price Prediction API")

model = None
preprocessor = None
feature_names = None


class PredictionRequest(BaseModel):
    Condition: Optional[str] = None
    Vehicle_brand: Optional[str] = None
    Vehicle_model: Optional[str] = None
    Mileage_km: Optional[float] = None
    Power_HP: Optional[float] = None
    Displacement_cm3: Optional[float] = None
    Fuel_type: Optional[str] = None
    Drive: Optional[str] = None
    Transmission: Optional[str] = None
    Type: Optional[str] = None
    Doors_number: Optional[float] = None
    Colour: Optional[str] = None
    car_age: Optional[float] = None
    mileage_per_year: Optional[float] = None
    power_to_displacement: Optional[float] = None


class PredictionResponse(BaseModel):
    predicted_price: float
    currency: str = "PLN"


@app.on_event("startup")
def load_models():
    global model, preprocessor, feature_names
    model = joblib.load(MODELS_DIR / "custom_model.pkl")
    preprocessor = joblib.load(MODELS_DIR / "custom_preprocessor.pkl")
    feature_names = joblib.load(MODELS_DIR / "custom_top_features.pkl")


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if request.Condition is None:
        raise HTTPException(status_code=400, detail="Condition is required")

    row = {}
    for name in feature_names:
        val = getattr(request, name, None)
        if val is None:
            raise HTTPException(status_code=400, detail=f"Missing feature: {name}")
        row[name] = val

    df = pd.DataFrame([row])

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)

    X = preprocessor.transform(df)
    y_pred = model.predict(X)

    return PredictionResponse(
        predicted_price=float(y_pred[0]),
        currency="PLN",
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "features": feature_names,
    }