"""
Pydantic schema for API request model.
"""

from pydantic import BaseModel
from typing import Optional


class PatientFeatures(BaseModel):
    """
    Patient feature schema for readmission prediction.

    All fields are optional; defaults will be applied if missing.
    """

    # Demographics
    age: Optional[int] = None
    gender: Optional[str] = None  # e.g., "m", "f"
    race: Optional[str] = None
    ethnicity: Optional[str] = None

    # Chronic conditions
    has_diabetes: Optional[bool] = None
    has_hypertension: Optional[bool] = None
    has_copd: Optional[bool] = None
    has_asthma: Optional[bool] = None
    has_heart_failure: Optional[bool] = None
    has_arthritis: Optional[bool] = None
    has_depression: Optional[bool] = None
    has_kidney_disease: Optional[bool] = None
    has_cancer: Optional[bool] = None
    has_alzheimers: Optional[bool] = None
    chronic_dx_count: Optional[int] = None  # Total chronic diagnoses

    # Medications
    num_meds: Optional[int] = None
    has_anticoagulant: Optional[bool] = None
    has_antibiotic: Optional[bool] = None
    has_steroid: Optional[bool] = None

    # Procedures
    num_procedures: Optional[int] = None
    had_surgery: Optional[bool] = None
    had_biopsy: Optional[bool] = None
