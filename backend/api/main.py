import joblib
import pandas as pd
import warnings
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

warnings.filterwarnings("ignore", category=UserWarning, module="xgboost")

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"

model = None
categorical_cols = None
feature_order = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, categorical_cols, feature_order
    model = joblib.load(MODELS_DIR / "custom_model.pkl")
    booster = model.get_booster()
    feature_order = booster.feature_names
    categorical_cols = [
        name for name, ftype in zip(booster.feature_names, booster.feature_types)
        if ftype == "c"
    ]
    yield


app = FastAPI(title="Car Price Prediction API", lifespan=lifespan)


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
    age_x_mileage: Optional[float] = None


class PredictionResponse(BaseModel):
    predicted_price: float
    currency: str = "PLN"


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    row = {}
    for field in request.model_fields:
        val = getattr(request, field)
        if val is None:
            raise HTTPException(status_code=400, detail=f"Missing feature: {field}")
        row[field] = val

    df = pd.DataFrame([row], columns=feature_order)

    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype("category")

    y_pred = model.predict(df)
    return PredictionResponse(
        predicted_price=float(y_pred[0]),
        currency="PLN",
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "feature_order": feature_order,
        "categorical_cols": categorical_cols,
    }