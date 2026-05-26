import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

MODEL_DIR = Path(
    os.getenv(
        "MODEL_DIR",
        PROJECT_ROOT / "models" / "car_price_xgboost_price_target",
    )
)
MODEL_FILE = os.getenv("MODEL_FILE", "model_pipeline_app.pkl")
MODEL_PATH = MODEL_DIR / MODEL_FILE
SCHEMA_PATH = MODEL_DIR / "input_schema.json"
BRAND_MODEL_LOOKUP_PATH = PROJECT_ROOT / "app" / "lookups" / "brand_model_lookup.csv"
