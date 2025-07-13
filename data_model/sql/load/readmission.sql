/*
========================================
Readmission Schema Data Load Script
========================================
*/

-- Load the Wide Encounter Fact Table
INSERT INTO readmission.encounter_fact (
    encounter_key,
    patient_key,
    encounter_start,
    encounter_end,
    age_at_encounter,
    gender_key,
    race_key,
    ethnicity_key,

    has_diabetes,
    has_hypertension,
    has_copd,
    has_asthma,
    has_heart_failure,
    has_arthritis,
    has_depression,
    has_kidney_disease,
    has_cancer,
    has_alzheimers,
    chronic_dx_count,

    num_meds,
    has_anticoagulant,
    has_antibiotic,
    has_steroid,

    num_procedures,
    had_surgery,
    had_biopsy,

    readmitted
)
WITH readmitted_flag AS (
  SELECT
    e1.encounter_key,
    CASE
      WHEN COUNT(*) > 0 THEN TRUE
      ELSE FALSE
    END AS readmitted
  FROM dimension.encounter_dim e1
  JOIN dimension.encounter_dim e2
    ON e1.patient_key = e2.patient_key
   AND e2.start_date > e1.end_date
   AND e2.start_date <= e1.end_date + INTERVAL '30 days'
   AND e1.encounter_key <> e2.encounter_key
  GROUP BY e1.encounter_key
),
procedure_dim AS (
    SELECT
        ed.encounter_key,
        COUNT(DISTINCT pl.procedure_key) AS num_procedures,
        BOOL_OR(pl.description ILIKE '%surgery%') AS had_surgery,
        BOOL_OR(pl.description ILIKE '%biopsy%') AS had_biopsy
    FROM dimension.encounter_dim ed
    JOIN dimension.procedure_dim pd ON ed.encounter_key = pd.encounter_key
    JOIN dimension.procedure_lookup pl ON pd.procedure_key = pl.procedure_key
    GROUP BY ed.encounter_key
),
medication_dim AS (
    SELECT
        ed.encounter_key,
        COUNT(DISTINCT ml.medication_key) AS num_meds,
        BOOL_OR(ml.description ILIKE '%anticoagulant%') AS has_anticoagulant,
        BOOL_OR(ml.description ILIKE '%antibiotic%') AS has_antibiotic,
        BOOL_OR(ml.description ILIKE '%steroid%') AS has_steroid
    FROM dimension.encounter_dim ed
    JOIN dimension.medication_dim md ON ed.encounter_key = md.encounter_key
    JOIN dimension.medication_lookup ml ON md.medication_key = ml.medication_key
    GROUP BY ed.encounter_key
),
chronic_dx_dim AS (
    SELECT
        ed.encounter_key,
        MAX(CASE WHEN dc.code = 'E11' THEN TRUE ELSE FALSE END) AS has_diabetes,
        MAX(CASE WHEN dc.code = 'I10' THEN TRUE ELSE FALSE END) AS has_hypertension,
        MAX(CASE WHEN dc.code LIKE 'J44%' THEN TRUE ELSE FALSE END) AS has_copd,
        MAX(CASE WHEN dc.code LIKE 'J45%' THEN TRUE ELSE FALSE END) AS has_asthma,
        MAX(CASE WHEN dc.code LIKE 'I50%' THEN TRUE ELSE FALSE END) AS has_heart_failure,
        MAX(CASE WHEN dc.code LIKE 'M19%' THEN TRUE ELSE FALSE END) AS has_arthritis,
        MAX(CASE WHEN dc.code LIKE 'F32%' THEN TRUE ELSE FALSE END) AS has_depression,
        MAX(CASE WHEN dc.code LIKE 'N18%' THEN TRUE ELSE FALSE END) AS has_kidney_disease,
        MAX(CASE WHEN dc.code LIKE 'C%' THEN TRUE ELSE FALSE END) AS has_cancer,
        MAX(CASE WHEN dc.code LIKE 'G30%' THEN TRUE ELSE FALSE END) AS has_alzheimers,
        COUNT(DISTINCT dc.diagnosis_key) AS chronic_dx_count
    FROM dimension.encounter_dim ed
    JOIN dimension.diagnosis_dim dd ON ed.encounter_key = dd.encounter_key
    JOIN dimension.diagnosis_lookup dc ON dd.diagnosis_key = dc.diagnosis_key
    WHERE dc.code IS NOT NULL
    GROUP BY ed.encounter_key
)
SELECT
    ed.encounter_key,
    ed.patient_key,
    ed.start_date,
    ed.end_date,
    DATE_PART('year', ed.start_date) - DATE_PART('year', pd.birthdate)::INT AS age_at_encounter,
    pd.gender_key,
    pd.race_key,
    pd.ethnicity_key,

    COALESCE(c.has_diabetes, FALSE),
    COALESCE(c.has_hypertension, FALSE),
    COALESCE(c.has_copd, FALSE),
    COALESCE(c.has_asthma, FALSE),
    COALESCE(c.has_heart_failure, FALSE),
    COALESCE(c.has_arthritis, FALSE),
    COALESCE(c.has_depression, FALSE),
    COALESCE(c.has_kidney_disease, FALSE),
    COALESCE(c.has_cancer, FALSE),
    COALESCE(c.has_alzheimers, FALSE),
    COALESCE(c.chronic_dx_count, 0),

    COALESCE(m.num_meds, 0),
    COALESCE(m.has_anticoagulant, FALSE),
    COALESCE(m.has_antibiotic, FALSE),
    COALESCE(m.has_steroid, FALSE),

    COALESCE(p.num_procedures, 0),
    COALESCE(p.had_surgery, FALSE),
    COALESCE(p.had_biopsy, FALSE),

    COALESCE(rf.readmitted, FALSE)
FROM dimension.encounter_dim ed
JOIN dimension.patient_dim pd ON ed.patient_key = pd.patient_key
LEFT JOIN readmitted_flag rf ON ed.encounter_key = rf.encounter_key
LEFT JOIN chronic_dx_dim c ON ed.encounter_key = c.encounter_key
LEFT JOIN medication_dim m ON ed.encounter_key = m.encounter_key
LEFT JOIN procedure_dim p ON ed.encounter_key = p.encounter_key
ON CONFLICT (encounter_key) DO UPDATE SET
    patient_key = EXCLUDED.patient_key,
    encounter_start = EXCLUDED.encounter_start,
    encounter_end = EXCLUDED.encounter_end,
    age_at_encounter = EXCLUDED.age_at_encounter,
    gender_key = EXCLUDED.gender_key,
    race_key = EXCLUDED.race_key,
    ethnicity_key = EXCLUDED.ethnicity_key,

    has_diabetes = EXCLUDED.has_diabetes,
    has_hypertension = EXCLUDED.has_hypertension,
    has_copd = EXCLUDED.has_copd,
    has_asthma = EXCLUDED.has_asthma,
    has_heart_failure = EXCLUDED.has_heart_failure,
    has_arthritis = EXCLUDED.has_arthritis,
    has_depression = EXCLUDED.has_depression,
    has_kidney_disease = EXCLUDED.has_kidney_disease,
    has_cancer = EXCLUDED.has_cancer,
    has_alzheimers = EXCLUDED.has_alzheimers,
    chronic_dx_count = EXCLUDED.chronic_dx_count,

    num_meds = EXCLUDED.num_meds,
    has_anticoagulant = EXCLUDED.has_anticoagulant,
    has_antibiotic = EXCLUDED.has_antibiotic,
    has_steroid = EXCLUDED.has_steroid,

    num_procedures = EXCLUDED.num_procedures,
    had_surgery = EXCLUDED.had_surgery,
    had_biopsy = EXCLUDED.had_biopsy,
    readmitted = EXCLUDED.readmitted;
