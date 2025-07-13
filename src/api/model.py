"""
Pydantic schemas for API request and response models.
"""

from pydantic import BaseModel
from typing import Optional


class PatientFeatures(BaseModel):
    """
    Data model for patient features used in readmission prediction.

    All fields are optional; missing fields will be filled with default values.
    """

    age: Optional[int] = None
    """Age of the patient at the time of encounter (in years)."""

    gender: Optional[str] = None
    """Encoded gender of the patient (e.g., 0 = Female, 1 = Male)."""

    race: Optional[str] = None
    """Encoded race of the patient."""

    ethnicity: Optional[str] = None
    """Encoded ethnicity of the patient."""

    has_diabetes: Optional[bool] = None
    """Whether the patient has a diagnosis of diabetes."""

    has_hypertension: Optional[bool] = None
    """Whether the patient has hypertension."""

    has_copd: Optional[bool] = None
    """Whether the patient has chronic obstructive pulmonary disease (COPD)."""

    has_asthma: Optional[bool] = None
    """Whether the patient has asthma."""

    has_heart_failure: Optional[bool] = None
    """Whether the patient has heart failure."""

    has_arthritis: Optional[bool] = None
    """Whether the patient has arthritis."""

    has_depression: Optional[bool] = None
    """Whether the patient has depression."""

    has_kidney_disease: Optional[bool] = None
    """Whether the patient has kidney disease."""

    has_cancer: Optional[bool] = None
    """Whether the patient has cancer."""

    has_alzheimers: Optional[bool] = None
    """Whether the patient has Alzheimer’s disease."""

    chronic_dx_count: Optional[int] = None
    """Count of chronic diagnoses for the patient."""

    num_meds: Optional[int] = None
    """Number of medications the patient is currently taking."""

    has_anticoagulant: Optional[bool] = None
    """Whether the patient is on anticoagulant medication."""

    has_antibiotic: Optional[bool] = None
    """Whether the patient is on antibiotic medication."""

    has_steroid: Optional[bool] = None
    """Whether the patient is on steroid medication."""

    num_procedures: Optional[int] = None
    """Number of medical procedures the patient has undergone."""

    had_surgery: Optional[bool] = None
    """Whether the patient had surgery during the encounter."""

    had_biopsy: Optional[bool] = None
    """Whether the patient had a biopsy during the encounter."""
