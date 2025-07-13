/*
DIMENSION DATA LOAD
*/

-- Prepopulate with 'Unknown' (surrogate key = 0)
INSERT INTO dimension.gender_lookup (gender_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.race_lookup (race_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.ethnicity_lookup (ethnicity_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.encounter_class_lookup (encounter_class_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.encounter_code_lookup (encounter_code_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.reason_code_lookup (reason_code_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.procedure_lookup (procedure_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.medication_lookup (medication_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.diagnosis_lookup (diagnosis_key, code, description) VALUES (0, 'Unknown', 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.organization_lookup (organization_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.provider_lookup (provider_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;
INSERT INTO dimension.payer_lookup (payer_key, description) VALUES (0, 'Unknown') ON CONFLICT DO NOTHING;



-- Load Diagnosis Lookup
INSERT INTO dimension.diagnosis_lookup (code, description)
SELECT DISTINCT code, description
FROM staging.conditions s
WHERE code IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM dimension.diagnosis_lookup d WHERE d.code = s.code::TEXT
);

-- Load Encounter Class Lookup
INSERT INTO dimension.encounter_class_lookup (description)
SELECT DISTINCT s.encounterclass
FROM staging.encounters s
WHERE encounterclass IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM dimension.encounter_class_lookup d WHERE d.description = s.encounterclass
);

-- Load Encounter Code Lookup
INSERT INTO dimension.encounter_code_lookup (code, description)
SELECT DISTINCT s.code, s.description
FROM staging.encounters s
WHERE encounterclass IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM dimension.encounter_code_lookup d WHERE d.code = s.code::TEXT
);

-- Load Ethnicity Lookup
INSERT INTO dimension.ethnicity_lookup (description)
SELECT DISTINCT ethnicity
FROM staging.patients s
WHERE ethnicity IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM dimension.ethnicity_lookup d WHERE d.description = s.ethnicity
);

-- Load Gender Lookup
INSERT INTO dimension.gender_lookup (description)
SELECT DISTINCT gender
FROM staging.patients s
WHERE gender IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM dimension.gender_lookup d WHERE d.description = s.gender
);

-- Load Medication Lookup
INSERT INTO dimension.medication_lookup (code, description)
SELECT code, MIN(description) -- Some codes have multiple descriptions, lets just grab the first.
FROM staging.medications s
WHERE code IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM dimension.medication_lookup d WHERE d.code = s.code::TEXT
)
GROUP BY code;

-- Load Procedure Lookup
INSERT INTO dimension.procedure_lookup (code, description)
SELECT DISTINCT code, description
FROM staging.procedures s
WHERE code IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM dimension.procedure_lookup d WHERE d.code = s.code::TEXT
);

-- Load Race Lookup
INSERT INTO dimension.race_lookup (description)
SELECT DISTINCT race
FROM staging.patients s
WHERE race IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM dimension.race_lookup d WHERE d.description = s.race
);

-- Load Reason Code Lookup
INSERT INTO dimension.reason_code_lookup (code, description)
SELECT DISTINCT reasoncode::TEXT, reasondescription
FROM staging.encounters s
WHERE reasoncode IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM dimension.reason_code_lookup d WHERE d.code = s.reasoncode::TEXT
);


-- Load Patient Dimension
INSERT INTO dimension.patient_dim (
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
LEFT JOIN dimension.gender_lookup g ON s.gender = g.description
LEFT JOIN dimension.race_lookup r ON s.race = r.description
LEFT JOIN dimension.ethnicity_lookup e ON s.ethnicity = e.description
WHERE NOT EXISTS (
  SELECT 1 FROM dimension.patient_dim p WHERE p.patient_id = s.id
);

-- Load Encounter Dimension
INSERT INTO dimension.encounter_dim (
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
JOIN dimension.patient_dim p ON s.patient = p.patient_id
LEFT JOIN dimension.organization_lookup o ON s.organization = o.description
LEFT JOIN dimension.provider_lookup pr ON s.provider = pr.description
LEFT JOIN dimension.payer_lookup pay ON s.payer = pay.description
LEFT JOIN dimension.encounter_class_lookup ec ON s.encounterclass = ec.description
LEFT JOIN dimension.encounter_code_lookup eco ON s.code::TEXT = eco.code
LEFT JOIN dimension.reason_code_lookup rc ON s.reasoncode::TEXT = rc.code
WHERE NOT EXISTS (
  SELECT 1 FROM dimension.encounter_dim e WHERE e.encounter_id = s.id
);

-- Load Procedure Dimension (encounter-level)
INSERT INTO dimension.procedure_dim (
  encounter_key, 
  procedure_key, 
  procedure_start_date,
  procedure_end_date
)
SELECT DISTINCT
  ed.encounter_key,
  pl.procedure_key,
  s.start,
  s.stop
FROM staging.procedures s
JOIN dimension.encounter_dim ed ON s.encounter = ed.encounter_id
JOIN dimension.procedure_lookup pl ON s.code::TEXT = pl.code
WHERE NOT EXISTS (
  SELECT 1 FROM dimension.procedure_dim pd 
  WHERE pd.encounter_key = ed.encounter_key 
    AND pd.procedure_key = pl.procedure_key
);

-- Load Medication Dimension (encounter-level)
INSERT INTO dimension.medication_dim (
  encounter_key, 
  medication_key, 
  medication_start_date, 
  medication_end_date
)
SELECT DISTINCT
  ed.encounter_key,
  ml.medication_key,
  s.start,
  s.stop
FROM staging.medications s
JOIN dimension.encounter_dim ed ON s.encounter = ed.encounter_id
JOIN dimension.medication_lookup ml ON s.code::TEXT = ml.code
WHERE NOT EXISTS (
  SELECT 1 FROM dimension.medication_dim md
  WHERE md.encounter_key = ed.encounter_key
    AND md.medication_key = ml.medication_key
);

-- Load Diagnosis Dimension (encounter-level)
INSERT INTO dimension.diagnosis_dim (
  encounter_key, 
  diagnosis_key, 
  diagnosis_start_date, 
  diagnosis_end_date
)
SELECT DISTINCT
  ed.encounter_key,
  dl.diagnosis_key,
  s.start,
  s.stop
FROM staging.conditions s
JOIN dimension.encounter_dim ed ON s.encounter = ed.encounter_id
JOIN dimension.diagnosis_lookup dl ON s.code::TEXT = dl.code
WHERE NOT EXISTS (
  SELECT 1 FROM dimension.diagnosis_dim dd
  WHERE dd.encounter_key = ed.encounter_key
    AND dd.diagnosis_key = dl.diagnosis_key
);
