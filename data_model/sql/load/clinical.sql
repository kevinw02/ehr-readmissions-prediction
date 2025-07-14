/*
DIMENSION DATA LOAD
*/

-- Prepopulate with 'Unknown' (surrogate key = 0)
INSERT INTO clinical.gender_dim (gender_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.race_dim (race_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.ethnicity_dim (ethnicity_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.encounter_class_dim (encounter_class_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.encounter_code_dim (encounter_code_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.reason_code_dim (reason_code_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.procedure_dim (procedure_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.medication_dim (medication_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.diagnosis_dim (diagnosis_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.organization_dim (organization_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.provider_dim (provider_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO clinical.payer_dim (payer_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;



-- Load Diagnosis Dimension
INSERT INTO clinical.diagnosis_dim (code, description)
SELECT DISTINCT code, description
FROM staging.conditions s
WHERE code IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM clinical.diagnosis_dim d WHERE d.code = s.code::TEXT
);

-- Load Encounter Class Dimension
INSERT INTO clinical.encounter_class_dim (description)
SELECT DISTINCT s.encounterclass
FROM staging.encounters s
WHERE encounterclass IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM clinical.encounter_class_dim d WHERE d.description = s.encounterclass
);

-- Load Encounter Code Dimension
INSERT INTO clinical.encounter_code_dim (code, description)
SELECT DISTINCT s.code, s.description
FROM staging.encounters s
WHERE encounterclass IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM clinical.encounter_code_dim d WHERE d.code = s.code::TEXT
);

-- Load Ethnicity Dimension
INSERT INTO clinical.ethnicity_dim (description)
SELECT DISTINCT ethnicity
FROM staging.patients s
WHERE ethnicity IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM clinical.ethnicity_dim d WHERE d.description = s.ethnicity
);

-- Load Gender Dimension
INSERT INTO clinical.gender_dim (description)
SELECT DISTINCT gender
FROM staging.patients s
WHERE gender IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM clinical.gender_dim d WHERE d.description = s.gender
);

-- Load Medication Dimension
INSERT INTO clinical.medication_dim (code, description)
SELECT code, MIN(description) -- Some codes have multiple descriptions, lets just grab the first.
FROM staging.medications s
WHERE code IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM clinical.medication_dim d WHERE d.code = s.code::TEXT
)
GROUP BY code;

-- Load Procedure Dimension
INSERT INTO clinical.procedure_dim (code, description)
SELECT DISTINCT code, description
FROM staging.procedures s
WHERE code IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM clinical.procedure_dim d WHERE d.code = s.code::TEXT
);

-- Load Race Dimension
INSERT INTO clinical.race_dim (description)
SELECT DISTINCT race
FROM staging.patients s
WHERE race IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM clinical.race_dim d WHERE d.description = s.race
);

-- Load Reason Code Dimension
INSERT INTO clinical.reason_code_dim (code, description)
SELECT DISTINCT reasoncode::TEXT, reasondescription
FROM staging.encounters s
WHERE reasoncode IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM clinical.reason_code_dim d WHERE d.code = s.reasoncode::TEXT
);


-- Load Patient Dimension
INSERT INTO clinical.patient_dim (
  patient_id, 
  birthdate, 
  gender_key, 
  race_key, 
  ethnicity_key
)
SELECT DISTINCT
  s.id,
  s.birthdate,
  COALESCE(g.gender_key, 0),
  COALESCE(r.race_key, 0),
  COALESCE(e.ethnicity_key, 0)
FROM staging.patients s
LEFT JOIN clinical.gender_dim g ON s.gender = g.description
LEFT JOIN clinical.race_dim r ON s.race = r.description
LEFT JOIN clinical.ethnicity_dim e ON s.ethnicity = e.description
WHERE NOT EXISTS (
  SELECT 1 FROM clinical.patient_dim p WHERE p.patient_id = s.id
);

-- Load Encounter Dimension
INSERT INTO clinical.encounter_dim (
  encounter_id, 
  patient_key, 
  start_date, 
  end_date,
  organization_key,
  provider_key,
  payer_key,
  encounter_class_key,
  encounter_code_key,
  reason_code_key,
  base_encounter_cost,
  total_claim_cost,
  payer_coverage
)
SELECT DISTINCT
  s.id,
  p.patient_key,
  s.start,
  s.stop,
  COALESCE(o.organization_key, 0),
  COALESCE(pr.provider_key, 0),
  COALESCE(pay.payer_key, 0),
  COALESCE(ec.encounter_class_key, 0),
  COALESCE(eco.encounter_code_key, 0),
  COALESCE(rc.reason_code_key, 0),
  s.base_encounter_cost,
  s.total_claim_cost,
  s.payer_coverage
FROM staging.encounters s
JOIN clinical.patient_dim p ON s.patient = p.patient_id
LEFT JOIN clinical.organization_dim o ON s.organization = o.description
LEFT JOIN clinical.provider_dim pr ON s.provider = pr.description
LEFT JOIN clinical.payer_dim pay ON s.payer = pay.description
LEFT JOIN clinical.encounter_class_dim ec ON s.encounterclass = ec.description
LEFT JOIN clinical.encounter_code_dim eco ON s.code::TEXT = eco.code
LEFT JOIN clinical.reason_code_dim rc ON s.reasoncode::TEXT = rc.code
WHERE NOT EXISTS (
  SELECT 1 FROM clinical.encounter_dim e WHERE e.encounter_id = s.id
);

-- Load Procedure Fact (encounter-level)
INSERT INTO clinical.procedure_fact (
  encounter_key,
  patient_key,
  procedure_key, 
  procedure_start_date,
  procedure_end_date
)
SELECT DISTINCT
  ed.encounter_key,
  pd.patient_key,
  pl.procedure_key,
  s.start,
  s.stop
FROM staging.procedures s
JOIN clinical.patient_dim pd on s.patient = pd.patient_id
JOIN clinical.encounter_dim ed ON s.encounter = ed.encounter_id
JOIN clinical.procedure_dim pl ON s.code::TEXT = pl.code
WHERE NOT EXISTS (
  SELECT 1 FROM clinical.procedure_fact pd 
  WHERE pd.encounter_key = ed.encounter_key 
    AND pd.procedure_key = pl.procedure_key
);

-- Load Medication Fact (encounter-level)
INSERT INTO clinical.medication_fact (
  encounter_key,
  patient_key,
  medication_key, 
  medication_start_date, 
  medication_end_date
)
SELECT DISTINCT
  ed.encounter_key,
  pd.patient_key,
  ml.medication_key,
  s.start,
  s.stop
FROM staging.medications s
JOIN clinical.patient_dim pd on s.patient = pd.patient_id
JOIN clinical.encounter_dim ed ON s.encounter = ed.encounter_id
JOIN clinical.medication_dim ml ON s.code::TEXT = ml.code
WHERE NOT EXISTS (
  SELECT 1 FROM clinical.medication_fact md
  WHERE md.encounter_key = ed.encounter_key
    AND md.medication_key = ml.medication_key
);

-- Load Diagnosis Fact (encounter-level)
INSERT INTO clinical.diagnosis_fact (
  encounter_key,
  patient_key,
  diagnosis_key, 
  diagnosis_start_date, 
  diagnosis_end_date
)
SELECT DISTINCT
  ed.encounter_key,
  pd.patient_key,
  dl.diagnosis_key,
  s.start,
  s.stop
FROM staging.conditions s
JOIN clinical.patient_dim pd on s.patient = pd.patient_id
JOIN clinical.encounter_dim ed ON s.encounter = ed.encounter_id
JOIN clinical.diagnosis_dim dl ON s.code::TEXT = dl.code
WHERE NOT EXISTS (
  SELECT 1 FROM clinical.diagnosis_fact dd
  WHERE dd.encounter_key = ed.encounter_key
    AND dd.diagnosis_key = dl.diagnosis_key
);
