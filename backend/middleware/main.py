import json
import httpx
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, validator

API_URL = "http://localhost:8000/predict"
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
OPTIONS_PATH = FRONTEND_DIR / "car_options.json"

app = FastAPI(title="Car Price Prediction - Middleware")


class FormData(BaseModel):
    Production_year: int
    Power_HP: float
    Mileage_km: float
    Displacement_cm3: float
    Doors_number: int
    Transmission: str
    Vehicle_model: str
    Vehicle_brand: str
    Type: str
    Drive: str
    Colour: str
    Fuel_type: str
    Condition: str

    @validator("Condition")
    def validate_condition(cls, v):
        if v not in ("New", "Used"):
            raise ValueError("Condition must be New or Used")
        return v

    @validator("Production_year")
    def validate_production_year(cls, v):
        if v < 1990 or v > 2026:
            raise ValueError("Production_year must be between 1990 and 2026")
        return v

    @validator("Power_HP", "Mileage_km", "Displacement_cm3")
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("Value must be non-negative")
        return v

    @validator("Doors_number")
    def validate_doors(cls, v):
        if v not in (2, 3, 4, 5):
            raise ValueError("Doors_number must be 2, 3, 4, or 5")
        return v

    class Config:
        extra = "forbid"


class PriceResponse(BaseModel):
    price_pln: int
    price_formatted: str


def compute_derived_features(data: FormData) -> dict:
    current_year = datetime.now().year
    car_age = max(current_year - data.Production_year, 0)
    mileage_per_year = data.Mileage_km / max(car_age, 1)
    power_to_displacement = (
        data.Power_HP / data.Displacement_cm3
        if data.Displacement_cm3 > 0
        else 0.0
    )
    age_x_mileage = car_age * data.Mileage_km

    return {
        "Condition": data.Condition,
        "Vehicle_brand": data.Vehicle_brand,
        "Vehicle_model": str(data.Vehicle_model),
        "Mileage_km": data.Mileage_km,
        "Power_HP": data.Power_HP,
        "Displacement_cm3": data.Displacement_cm3,
        "Fuel_type": data.Fuel_type,
        "Drive": data.Drive,
        "Transmission": data.Transmission,
        "Type": data.Type,
        "Doors_number": float(data.Doors_number),
        "Colour": data.Colour,
        "car_age": float(car_age),
        "mileage_per_year": mileage_per_year,
        "power_to_displacement": power_to_displacement,
        "age_x_mileage": age_x_mileage,
    }


@app.get("/car-options")
def get_car_options():
    with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/predict", response_model=PriceResponse)
async def predict(data: FormData):
    features = compute_derived_features(data)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(API_URL, json=features)
            response.raise_for_status()
        except httpx.ConnectError:
            raise HTTPException(
                status_code=502,
                detail="Nie mozna polaczyc z API modelu. Upewnij sie, ze api dziala na porcie 8000.",
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Blad API: {e.response.text}",
            )

    result = response.json()
    price = result["predicted_price"]

    return PriceResponse(
        price_pln=int(round(price)),
        price_formatted=f"{int(round(price)):,} PLN".replace(",", " "),
    )


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = FRONTEND_DIR / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))