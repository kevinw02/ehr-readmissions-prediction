-- Drop and recreate schema
DROP SCHEMA IF EXISTS clinical CASCADE;
CREATE SCHEMA clinical;

-- DIMENSIONS
-- Diagnosis Dimension
CREATE SEQUENCE clinical.diagnosis_key_seq START 1;
CREATE TABLE clinical.diagnosis_dim (
    diagnosis_key INTEGER PRIMARY KEY DEFAULT nextval('clinical.diagnosis_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Encounter Class Dimension
CREATE SEQUENCE clinical.encounter_class_key_seq START 1;
CREATE TABLE clinical.encounter_class_dim (
    encounter_class_key SMALLINT PRIMARY KEY DEFAULT nextval('clinical.encounter_class_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Encounter Code Dimension
CREATE SEQUENCE clinical.encounter_code_key_seq START 1;
CREATE TABLE clinical.encounter_code_dim (
    encounter_code_key SMALLINT PRIMARY KEY DEFAULT nextval('clinical.encounter_code_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Ethnicity Dimension
CREATE SEQUENCE clinical.ethnicity_key_seq START 1;
CREATE TABLE clinical.ethnicity_dim (
    ethnicity_key UTINYINT PRIMARY KEY DEFAULT nextval('clinical.ethnicity_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Gender Dimension
CREATE SEQUENCE clinical.gender_key_seq START 1;
CREATE TABLE clinical.gender_dim (
    gender_key UTINYINT PRIMARY KEY DEFAULT nextval('clinical.gender_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Medications Dimension
CREATE SEQUENCE clinical.medication_key_seq START 1;
CREATE TABLE clinical.medication_dim (
    medication_key INTEGER PRIMARY KEY DEFAULT nextval('clinical.medication_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Organization Dimension
CREATE SEQUENCE clinical.organization_key_seq START 1;
CREATE TABLE clinical.organization_dim (
    organization_key SMALLINT PRIMARY KEY DEFAULT nextval('clinical.organization_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Payer Dimension
CREATE SEQUENCE clinical.payer_key_seq START 1;
CREATE TABLE clinical.payer_dim (
    payer_key SMALLINT PRIMARY KEY DEFAULT nextval('clinical.payer_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Procedure Dimension
CREATE SEQUENCE clinical.procedure_key_seq START 1;
CREATE TABLE clinical.procedure_dim (
    procedure_key INTEGER PRIMARY KEY DEFAULT nextval('clinical.procedure_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Provider Dimension
CREATE SEQUENCE clinical.provider_key_seq START 1;
CREATE TABLE clinical.provider_dim (
    provider_key SMALLINT PRIMARY KEY DEFAULT nextval('clinical.provider_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Race Dimension
CREATE SEQUENCE clinical.race_key_seq START 1;
CREATE TABLE clinical.race_dim (
    race_key UTINYINT PRIMARY KEY DEFAULT nextval('clinical.race_key_seq'),
    description TEXT UNIQUE NOT NULL
);

-- Reason Code Dimension
CREATE SEQUENCE clinical.reason_code_key_seq START 1;
CREATE TABLE clinical.reason_code_dim (
    reason_code_key SMALLINT PRIMARY KEY DEFAULT nextval('clinical.reason_code_key_seq'),
    code TEXT UNIQUE NOT NULL,
    description TEXT
);

-- Patient dimension
CREATE SEQUENCE clinical.patient_key_seq START 1;
CREATE TABLE clinical.patient_dim (
    patient_key INTEGER PRIMARY KEY DEFAULT nextval('clinical.patient_key_seq'),
    patient_id TEXT UNIQUE NOT NULL,
    birthdate DATE,
    gender_key UTINYINT REFERENCES clinical.gender_dim(gender_key),
    race_key UTINYINT REFERENCES clinical.race_dim(race_key),
    ethnicity_key UTINYINT REFERENCES clinical.ethnicity_dim(ethnicity_key)
);

-- Encounter dimension (Fact-like)
-- This is serving as a conformed dimension across the fact tables, but I think it 
-- would be perfectly reasonable to use this as a fact table and perhaps rename it.
-- Frankly, it likely just depends on downstream use cases.
CREATE SEQUENCE clinical.encounter_key_seq START 1;
CREATE TABLE clinical.encounter_dim (
    encounter_key INTEGER PRIMARY KEY DEFAULT nextval('clinical.encounter_key_seq'),
    encounter_id TEXT UNIQUE NOT NULL,
    patient_key INTEGER REFERENCES clinical.patient_dim(patient_key),
    start_date DATE,
    end_date DATE,
    organization_key SMALLINT REFERENCES clinical.organization_dim(organization_key),
    provider_key SMALLINT REFERENCES clinical.provider_dim(provider_key),
    payer_key SMALLINT REFERENCES clinical.payer_dim(payer_key),
    encounter_class_key SMALLINT REFERENCES clinical.encounter_class_dim(encounter_class_key),
    encounter_code_key SMALLINT REFERENCES clinical.encounter_code_dim(encounter_code_key),
    reason_code_key SMALLINT REFERENCES clinical.reason_code_dim(reason_code_key),
    base_encounter_cost FLOAT4,
    total_claim_cost FLOAT4,
    payer_coverage FLOAT4
);

-- FACTS
-- Diagnosis (for encounter-level diagnosis details)
CREATE SEQUENCE clinical.diagnosis_fact_key_seq START 1;
CREATE TABLE clinical.diagnosis_fact (
    diagnosis_fact_key INTEGER PRIMARY KEY DEFAULT nextval('clinical.diagnosis_fact_key_seq'),
    patient_key INTEGER REFERENCES clinical.patient_dim(patient_key),
    encounter_key INTEGER REFERENCES clinical.encounter_dim(encounter_key),
    diagnosis_key INTEGER REFERENCES clinical.diagnosis_dim(diagnosis_key),
    diagnosis_start_date DATE,
    diagnosis_end_date DATE
);

-- Medication (for encounter-level medication details)
CREATE SEQUENCE clinical.medication_fact_key_seq START 1;
CREATE TABLE clinical.medication_fact (
    medication_fact_key INTEGER PRIMARY KEY DEFAULT nextval('clinical.medication_fact_key_seq'),
    patient_key INTEGER REFERENCES clinical.patient_dim(patient_key),
    encounter_key INTEGER REFERENCES clinical.encounter_dim(encounter_key),
    medication_key INTEGER REFERENCES clinical.medication_dim(medication_key),
    medication_start_date DATE,
    medication_end_date DATE
);

-- Procedure dimension (for encounter-level procedure details)
CREATE SEQUENCE clinical.procedure_fact_key_seq START 1;
CREATE TABLE clinical.procedure_fact (
    procedure_fact_key INTEGER PRIMARY KEY DEFAULT nextval('clinical.procedure_fact_key_seq'),
    patient_key INTEGER REFERENCES clinical.patient_dim(patient_key),
    encounter_key INTEGER REFERENCES clinical.encounter_dim(encounter_key),
    procedure_key INTEGER REFERENCES clinical.procedure_dim(procedure_key),
    procedure_start_date DATE,
    procedure_end_date DATE
);
