-- Drop and recreate schema
DROP SCHEMA IF EXISTS dimension CASCADE;
CREATE SCHEMA dimension;

-- LOOKUPS
-- Diagnosis lookup
CREATE SEQUENCE dimension.diagnosis_key_seq START 1;
CREATE TABLE dimension.diagnosis_lookup (
    diagnosis_key INTEGER PRIMARY KEY DEFAULT nextval('dimension.diagnosis_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Encounter Class Lookup
CREATE SEQUENCE dimension.encounter_class_key_seq START 1;
CREATE TABLE dimension.encounter_class_lookup (
    encounter_class_key SMALLINT PRIMARY KEY DEFAULT nextval('dimension.encounter_class_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Encounter Code Lookup
CREATE SEQUENCE dimension.encounter_code_key_seq START 1;
CREATE TABLE dimension.encounter_code_lookup (
    encounter_code_key SMALLINT PRIMARY KEY DEFAULT nextval('dimension.encounter_code_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Ethnicity Lookup
CREATE SEQUENCE dimension.ethnicity_key_seq START 1;
CREATE TABLE dimension.ethnicity_lookup (
    ethnicity_key UTINYINT PRIMARY KEY DEFAULT nextval('dimension.ethnicity_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Gender Lookup
CREATE SEQUENCE dimension.gender_key_seq START 1;
CREATE TABLE dimension.gender_lookup (
    gender_key UTINYINT PRIMARY KEY DEFAULT nextval('dimension.gender_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- MEDICATIONS LOOKUP
CREATE SEQUENCE dimension.medication_key_seq START 1;
CREATE TABLE dimension.medication_lookup (
    medication_key INTEGER PRIMARY KEY DEFAULT nextval('dimension.medication_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Organization Lookup
CREATE SEQUENCE dimension.organization_key_seq START 1;
CREATE TABLE dimension.organization_lookup (
    organization_key SMALLINT PRIMARY KEY DEFAULT nextval('dimension.organization_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Payer Lookup
CREATE SEQUENCE dimension.payer_key_seq START 1;
CREATE TABLE dimension.payer_lookup (
    payer_key SMALLINT PRIMARY KEY DEFAULT nextval('dimension.payer_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Procedure lookup
CREATE SEQUENCE dimension.procedure_key_seq START 1;
CREATE TABLE dimension.procedure_lookup (
    procedure_key INTEGER PRIMARY KEY DEFAULT nextval('dimension.procedure_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Provider Lookup
CREATE SEQUENCE dimension.provider_key_seq START 1;
CREATE TABLE dimension.provider_lookup (
    provider_key SMALLINT PRIMARY KEY DEFAULT nextval('dimension.provider_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Race Lookup
CREATE SEQUENCE dimension.race_key_seq START 1;
CREATE TABLE dimension.race_lookup (
    race_key UTINYINT PRIMARY KEY DEFAULT nextval('dimension.race_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Reason Code Lookup
CREATE SEQUENCE dimension.reason_code_key_seq START 1;
CREATE TABLE dimension.reason_code_lookup (
    reason_code_key SMALLINT PRIMARY KEY DEFAULT nextval('dimension.reason_code_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);


-- DIMENSIONS
-- Patient Dimension (first table as it is referenced by encounter_dim)
CREATE SEQUENCE dimension.patient_key_seq START 1;
CREATE TABLE dimension.patient_dim (
    patient_key INTEGER PRIMARY KEY DEFAULT nextval('dimension.patient_key_seq'),
    patient_id TEXT UNIQUE NOT NULL,
    birthdate DATE,
    gender_key UTINYINT REFERENCES dimension.gender_lookup(gender_key),
    race_key UTINYINT REFERENCES dimension.race_lookup(race_key),
    ethnicity_key UTINYINT REFERENCES dimension.ethnicity_lookup(ethnicity_key)
);

-- Encounter Dimension (Fact-like) (second dim table as it is referenced by many tables)
CREATE SEQUENCE dimension.encounter_key_seq START 1;
CREATE TABLE dimension.encounter_dim (
    encounter_key INTEGER PRIMARY KEY DEFAULT nextval('dimension.encounter_key_seq'),
    encounter_id TEXT UNIQUE NOT NULL,
    patient_key INTEGER REFERENCES dimension.patient_dim(patient_key),
    start_date DATE,
    end_date DATE,
    organization_key SMALLINT REFERENCES dimension.organization_lookup(organization_key),
    provider_key SMALLINT REFERENCES dimension.provider_lookup(provider_key),
    payer_key SMALLINT REFERENCES dimension.payer_lookup(payer_key),
    encounter_class_key SMALLINT REFERENCES dimension.encounter_class_lookup(encounter_class_key),
    encounter_code_key SMALLINT REFERENCES dimension.encounter_code_lookup(encounter_code_key),
    reason_code_key SMALLINT REFERENCES dimension.reason_code_lookup(reason_code_key),
    base_encounter_cost FLOAT4,
    total_claim_cost FLOAT4,
    payer_coverage FLOAT4
);

-- Diagnosis Dimension (for encounter-level diagnosis details)
CREATE SEQUENCE dimension.diagnosis_dim_key_seq START 1;
CREATE TABLE dimension.diagnosis_dim (
    diagnosis_dim_key INTEGER PRIMARY KEY DEFAULT nextval('dimension.diagnosis_dim_key_seq'),
    encounter_key INTEGER REFERENCES dimension.encounter_dim(encounter_key),
    diagnosis_key INTEGER REFERENCES dimension.diagnosis_lookup(diagnosis_key),
    diagnosis_start_date DATE,
    diagnosis_end_date DATE
);

-- Medication dimension (for encounter-level medication details)
CREATE SEQUENCE dimension.medication_dim_key_seq START 1;
CREATE TABLE dimension.medication_dim (
    medication_dim_key INTEGER PRIMARY KEY DEFAULT nextval('dimension.medication_dim_key_seq'),
    encounter_key INTEGER REFERENCES dimension.encounter_dim(encounter_key),
    medication_key INTEGER REFERENCES dimension.medication_lookup(medication_key),
    medication_start_date DATE,
    medication_end_date DATE
);

-- Procedure dimension (for encounter-level procedure details)
CREATE SEQUENCE dimension.procedure_dim_key_seq START 1;
CREATE TABLE dimension.procedure_dim (
    procedure_dim_key INTEGER PRIMARY KEY DEFAULT nextval('dimension.procedure_dim_key_seq'),
    encounter_key INTEGER REFERENCES dimension.encounter_dim(encounter_key),
    procedure_key INTEGER REFERENCES dimension.procedure_lookup(procedure_key),
    procedure_start_date DATE,
    procedure_end_date DATE
);
