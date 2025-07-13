import pytest
from pydantic import ValidationError
from api.model import PatientFeatures


def test_patient_features_accepts_partial_data():
    # Only some fields provided
    data = {
        "age": 45,
        "gender": "male",
        "has_diabetes": True,
        "num_meds": 3,
    }
    patient = PatientFeatures(**data)
    assert patient.age == 45
    assert patient.gender == "male"
    assert patient.has_diabetes is True
    assert patient.num_meds == 3

    # Fields not provided default to None
    assert patient.race is None
    assert patient.has_hypertension is None


def test_patient_features_accepts_empty_data():
    # No data, all fields None
    patient = PatientFeatures()
    for field in patient.model_fields:
        assert getattr(patient, field) is None


def test_patient_features_invalid_types():
    # Provide wrong types to check validation errors
    with pytest.raises(ValidationError):
        PatientFeatures(age="not_an_int")

    with pytest.raises(ValidationError):
        PatientFeatures(has_diabetes="not_a_bool")

    with pytest.raises(ValidationError):
        PatientFeatures(num_meds="five")
