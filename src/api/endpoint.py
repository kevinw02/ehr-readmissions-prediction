"""
API route definitions for health check and prediction.
"""


import yaml
from .db_helpers import load_dimension_mapping
from .model import PatientFeatures
from db import constant as c
from db.connection import create_db_connection
from fastapi import APIRouter
from ml.model import ReadmissionModel
from pathlib import Path

# --- Constants ---
FEATURES = [
    "age", "gender_key", "race_key", "ethnicity_key",
    "has_diabetes", "has_hypertension", "has_copd", "has_asthma",
    "has_heart_failure", "has_arthritis", "has_depression", "has_kidney_disease",
    "has_cancer", "has_alzheimers", "chronic_dx_count", "num_meds",
    "has_anticoagulant", "has_antibiotic", "has_steroid",
    "num_procedures", "had_surgery", "had_biopsy",
]

DEFAULTS = {feat: 0 if "num_" in feat or "count" in feat or feat.endswith("_key") or feat == "age" else False for feat in FEATURES}

# --- Global mappings ---
GENDER_MAP: dict = {}
RACE_MAP: dict = {}
ETHNICITY_MAP: dict = {}

# --- Config ---
CONFIG_PATH = Path(__file__).resolve().parents[2] / "data" / "duckdb_config.yaml"

# --- Router and Model ---
router = APIRouter()
model = ReadmissionModel()


def load_all_mappings():
    """Load dimension mappings from the database."""
    with CONFIG_PATH.open() as f:
        config = yaml.safe_load(f)

    conn = create_db_connection(config)
    global GENDER_MAP, RACE_MAP, ETHNICITY_MAP

    GENDER_MAP = load_dimension_mapping(conn, c.Table.GENDER_DIM, c.Column.GENDER_KEY)
    RACE_MAP = load_dimension_mapping(conn, c.Table.RACE_DIM, c.Column.RACE_KEY)
    ETHNICITY_MAP = load_dimension_mapping(conn, c.Table.ETHINICITY_DIM, c.Column.ETHNICITY_KEY)


@router.get("/healthz")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/metadata")
def get_metadata():
    """Return possible values for gender, race, and ethnicity."""
    return {
        "genders": list(GENDER_MAP.keys()),
        "races": list(RACE_MAP.keys()),
        "ethnicities": list(ETHNICITY_MAP.keys()),
    }


@router.post("/predict")
def predict(features: PatientFeatures):
    """Generate readmission prediction based on patient features."""
    input_vector = _build_feature_vector(features)
    prediction = model.predict(input_vector)
    return {"readmission_probability": prediction}


def _build_feature_vector(data: PatientFeatures) -> list:
    """Convert PatientFeatures into a model-ready feature vector."""
    feature_vector = []
    for feat in FEATURES:
        if feat in {"gender_key", "race_key", "ethnicity_key"}:
            value = _map_categorical_feature(data, feat)
        else:
            raw_value = getattr(data, feat, DEFAULTS.get(feat))
            # If raw_value is None, fallback to default or 0
            if raw_value is None:
                raw_value = DEFAULTS.get(feat, 0)
            try:
                value = int(raw_value)
            except (TypeError, ValueError):
                value = 0  # fallback safe default
        feature_vector.append(value)
    return feature_vector


def _map_categorical_feature(data: PatientFeatures, feature: str):
    """Helper for mapping categorical strings to keys."""
    value = getattr(data, feature.replace("_key", ""), None)
    if value is None:
        return DEFAULTS[feature]
    
    lookup = {
        "gender_key": GENDER_MAP,
        "race_key": RACE_MAP,
        "ethnicity_key": ETHNICITY_MAP,
    }.get(feature, {})

    return lookup.get(value.lower(), DEFAULTS[feature])
