-- SCHEMA
DROP SCHEMA IF EXISTS readmission CASCADE;
CREATE SCHEMA readmission;

-- NOTE: Can't use foreign keys to dimension schema as DuckDB does not support cross schema keys.
-- WIDE FEATURE FACT TABLE
CREATE TABLE readmission.encounter_fact (
    encounter_key INTEGER PRIMARY KEY,
    patient_key INTEGER,
    encounter_start DATE,
    encounter_end DATE,
    age_at_encounter INTEGER,
    gender_key UTINYINT,
    race_key UTINYINT,
    ethnicity_key UTINYINT,
    
    -- Chronic
    has_diabetes BOOL,
    has_hypertension BOOL,
    has_copd BOOL,
    has_asthma BOOL,
    has_heart_failure BOOL,
    has_arthritis BOOL,
    has_depression BOOL,
    has_kidney_disease BOOL,
    has_cancer BOOL,
    has_alzheimers BOOL,
    chronic_dx_count USMALLINT,

    -- Medications
    num_meds USMALLINT,
    has_anticoagulant BOOL,
    has_antibiotic BOOL,
    has_steroid BOOL,

    -- Procedures
    num_procedures USMALLINT,
    had_surgery BOOL,
    had_biopsy BOOL,

    -- Label
    readmitted BOOL
);
