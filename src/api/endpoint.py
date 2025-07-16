"""
API route definitions for health check and prediction.
"""

import db.constant as c
import os
import yaml
from .db_helpers import load_dimension_mapping
from .model import PatientFeatures
from db.connection import create_db_connection
from fastapi import APIRouter
from ml.model import ReadmissionModel
from pathlib import Path

# Globals
GENDER_MAP = {}
RACE_MAP = {}
ETHNICITY_MAP = {}

# Constants
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(MODULE_DIR, "..", "..", "data", "duckdb_config.yaml")

FEATURES = [
    "age",
    "gender_key",
    "race_key",
    "ethnicity_key",
    "has_diabetes",
    "has_hypertension",
    "has_copd",
    "has_asthma",
    "has_heart_failure",
    "has_arthritis",
    "has_depression",
    "has_kidney_disease",
    "has_cancer",
    "has_alzheimers",
    "chronic_dx_count",
    "num_meds",
    "has_anticoagulant",
    "has_antibiotic",
    "has_steroid",
    "num_procedures",
    "had_surgery",
    "had_biopsy",
]

DEFAULTS = {
    "age": 60,
    "gender_key": 0,
    "race_key": 0,
    "ethnicity_key": 0,
    "has_diabetes": False,
    "has_hypertension": False,
    "has_copd": False,
    "has_asthma": False,
    "has_heart_failure": False,
    "has_arthritis": False,
    "has_depression": False,
    "has_kidney_disease": False,
    "has_cancer": False,
    "has_alzheimers": False,
    "chronic_dx_count": 0,
    "num_meds": 0,
    "has_anticoagulant": False,
    "has_antibiotic": False,
    "has_steroid": False,
    "num_procedures": 0,
    "had_surgery": False,
    "had_biopsy": False,
}


def load_all_mappings():
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    conn = create_db_connection(config)

    global GENDER_MAP, RACE_MAP, ETHNICITY_MAP
    GENDER_MAP = load_dimension_mapping(conn, c.Table.GENDER_DIM, c.Column.GENDER_KEY)
    RACE_MAP = load_dimension_mapping(conn, c.Table.RACE_DIM, c.Column.RACE_KEY)
    ETHNICITY_MAP = load_dimension_mapping(
        conn, c.Table.ETHINICITY_DIM, c.Column.ETHNICITY_KEY
    )


router = APIRouter()
model = ReadmissionModel()


@router.get("/healthz")
def health_check():
    """
    Simple health check endpoint.

    Returns:
        dict: A status message indicating service is running.
    """
    return {"status": "ok"}


@router.get("/metadata")
def get_metadata():
    return {
        "genders": list(GENDER_MAP.keys()),
        "races": list(RACE_MAP.keys()),
        "ethnicities": list(ETHNICITY_MAP.keys()),
    }


@router.post("/predict")
def predict(features: PatientFeatures):
    input_vector = _build_feature_vector(features)
    prediction = model.predict(input_vector)
    return {"readmission_probability": prediction}


def _build_feature_vector(data: PatientFeatures) -> list:
    feature_vector = []

    for feat in FEATURES:
        if feat == "gender_key":
            val = GENDER_MAP.get(data.gender.lower()) if data.gender else None
        elif feat == "race_key":
            val = RACE_MAP.get(data.race.lower()) if data.race else None
        elif feat == "ethnicity_key":
            val = ETHNICITY_MAP.get(data.ethnicity.lower()) if data.ethnicity else None
        else:
            val = getattr(data, feat, None)

        if val is None:
            val = DEFAULTS[feat]

        if isinstance(val, bool):
            val = int(val)

        feature_vector.append(val)

    return feature_vector
