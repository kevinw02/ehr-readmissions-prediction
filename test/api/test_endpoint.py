from fastapi import FastAPI
from fastapi.testclient import TestClient
from api.endpoint import router
from unittest.mock import patch


app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("api.endpoint.GENDER_MAP", {"m": 1, "f": 2})
@patch("api.endpoint.RACE_MAP", {"white": 1, "black": 2})
@patch("api.endpoint.ETHNICITY_MAP", {"hispanic": 1, "non-hispanic": 2})
def test_metadata():
    response = client.get("/metadata")
    assert response.status_code == 200
    json_data = response.json()
    assert set(json_data["genders"]) == {"m", "f"}
    assert set(json_data["races"]) == {"white", "black"}
    assert set(json_data["ethnicities"]) == {"hispanic", "non-hispanic"}


@patch("api.endpoint.model")
def test_predict(mock_model):
    # Setup mock predict return value
    mock_model.predict.return_value = 0.75

    # Sample input matching PatientFeatures (adjust fields as necessary)
    payload = {
        "age": 50,
        "gender": "m",
        "race": "White",
        "ethnicity": "Hispanic",
        "has_diabetes": True,
        "has_hypertension": False,
        # add other fields with defaults or sample values
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    json_data = response.json()
    assert "readmission_probability" in json_data
    assert json_data["readmission_probability"] == 0.75

    # Assert that model.predict was called once
    mock_model.predict.assert_called_once()


def test_build_feature_vector_defaults():
    from api.endpoint import (
        _build_feature_vector,
        PatientFeatures,
        DEFAULTS,
        GENDER_MAP,
        RACE_MAP,
        ETHNICITY_MAP,
    )

    # Clear global maps to force defaults
    GENDER_MAP.clear()
    RACE_MAP.clear()
    ETHNICITY_MAP.clear()

    data = PatientFeatures(
        age=None,
        gender=None,
        race=None,
        ethnicity=None,
        has_diabetes=False,
        has_hypertension=False,
        has_copd=False,
        has_asthma=False,
        has_heart_failure=False,
        has_arthritis=False,
        has_depression=False,
        has_kidney_disease=False,
        has_cancer=False,
        has_alzheimers=False,
        chronic_dx_count=0,
        num_meds=0,
        has_anticoagulant=False,
        has_antibiotic=False,
        has_steroid=False,
        num_procedures=0,
        had_surgery=False,
        had_biopsy=False,
    )

    vector = _build_feature_vector(data)

    assert isinstance(vector, list)
    assert len(vector) == len(DEFAULTS)
    # Check defaults applied for keys
    assert vector[0] == DEFAULTS["age"]
    assert vector[1] == DEFAULTS["gender_key"]  # Because GENDER_MAP is empty
