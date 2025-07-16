# Healthcare ML Analytics with DuckDB

This project demonstrates scalable machine learning and analytics workflows using DuckDB as the backend for fast, in-process analytics. It is designed to operate on synthetic or public healthcare datasets and is built to be modular, extensible, and secure. The synthetic EHR raw data was built from the 
Synthea repo: https://github.com/synthetichealth/synthea and consists of all the files in data/csv. This data dump feels similar to data that I've worked
with in real world scenarios. 

Note: In a production or enterprise scenario, the csv data would not be included in this repo, other than maybe a small dump for testing. A better storage location would be in S3 or another cloud storage container.

---

## Features

- Modular database connection interface with support for DuckDB
- CLI utility to load CSV data into DuckDB from YAML configuration
- Support for schema tracking and reproducible ingestion
- Easily extendable for ML workflows and exploratory data analysis
- Galaxy data modeling of healthcare data with snowflake normalization
- Feature store specifically designed for patient readmission prediction
- Training and evaluation of Logistic Regression and XGBoost models
- REST API for serving predictions built with FastAPI
- Streamlit web app for interactive model testing
- Containerized deployment via Docker with shared networking between API and demo app

---

## Requirements

- Python 3.8+
- [DuckDB](https://duckdb.org)
- Conda (Miniconda or Anaconda recommended)
- Docker (for containerized runs)

---

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/kevinw02/ehr-readmissions-prediction
cd ehr-readmissions-prediction
```
2. Create conda environment:
```bash
conda env create -f environment.yml
conda activate ehrml
```
3. Set PYTHONPATH: 
```bash
export PYTHONPATH=$PWD/src:$PYTHONPATH
```
4. Load raw data from csv files: 
```bash
python scripts/load_data.py
```
5. (Optional) Validate raw data load: 
```bash
python scripts/validate_data.py
```
6. Build data models for dimensional attributes and feature store: 
```bash
python scripts/build_schema.py
```
7. Build and train ML models for prediction: 
```bash
python scripts/train_model.py
```
Note: SHAP visualizations suggest that some features may be irrelevant in the current model. However, they are retained in this example because with a larger dataset (e.g., more than 1,000 synthetic patients), these features might show stronger predictive value.

## How To Run
### Via Docker Compose
NOTE: Ensure the steps in Getting Started ^ have been run before this step.

1. Build and start both the API and Streamlit demo containers with a shared network:

Note: You must have saved a model by this step. If no model is saved, run: `python scripts/train_model.py` and input 'y'.
```bash
docker-compose up --build -d
```
Note: This will start two services (API and Streamlit):
- Streamlit Demo App accessible at: http://localhost:8501

2. Stop the containers:
```bash
docker-compose down
```

## Tests
### Unit tests
1. Run via pytest: `pytest test`
Note: Tests cover data loading, validation, model training, API endpoints, and other core functionality.
### Data validation tests (manual)
1. Run python script to ensure raw data load: `python3 scripts/validate_data.py`

## Project Structure
- `app/` – Streamlit demo app for interactive model testing  
- `data/` – Configuration files and raw CSV data (from Synthea)  
- `data_model/` – DDL scripts for schema creation, table definitions, and data loading  
- `docker-compose.yml` – Docker Compose config for running API and Streamlit containers  
- `Dockerfile` – Dockerfile for the FastAPI model serving container  
- `Dockerfile.streamlit` – Dockerfile for the Streamlit UI container  
- `.dockerignore` – Excludes unnecessary files from Docker builds  
- `environment.yml` – Conda environment file with dependencies  
- `ml_model/` – Directory for saved/serialized trained models  
- `scripts/` – Utility scripts for data loading, validation, and training  
- `src/` – Core source code:
  - `src/api/` – FastAPI app and route definitions  
  - `src/db/` – DuckDB database connectors and query utilities  
  - `src/ml/` – Model training, feature engineering, and inference  
- `test/` – Pytest unit and integration tests  
- `.gitignore` – Git ignore rules  
- `README.md` – Project documentation (this file)

## Data Model

This model follows a **galaxy schema** pattern, where conformed dimensions (`patient_dim` and `encounter_dim`) are shared across multiple fact tables. It also uses a **snowflake structure** by normalizing lookup values into separate dimension tables.

---

### Conformed Dimensions (Shared)

| Table                     | Type       | Description                                                                 |
|--------------------------|------------|-----------------------------------------------------------------------------|
| `clinical.patient_dim`   | Dimension  | One row per patient; links to gender, race, and ethnicity dimensions       |
| `clinical.encounter_dim` | Fact-like  | One row per encounter; links to patient, encounter class/code, reason, etc.|

---

### Fact Tables (Galaxy Core)

| Table                      | Type  | Description                                                                 |
|---------------------------|--------|-----------------------------------------------------------------------------|
| `clinical.diagnosis_fact` | Fact  | Encounter-level diagnosis facts; links to diagnosis codes and patient/encounter |
| `clinical.medication_fact`| Fact  | Encounter-level medication facts; links to medication codes and patient/encounter |
| `clinical.procedure_fact` | Fact  | Encounter-level procedure facts; links to procedure codes and patient/encounter |

---

### Snowflaked Lookup Dimensions

| Table                          | Type      | Description                                                                 |
|--------------------------------|-----------|-----------------------------------------------------------------------------|
| `clinical.gender_dim`          | Dimension | Normalized gender values (e.g., male, female, unknown)                      |
| `clinical.race_dim`            | Dimension | Normalized race values                                                      |
| `clinical.ethnicity_dim`       | Dimension | Normalized ethnicity values                                                 |
| `clinical.encounter_class_dim` | Dimension | High-level classification of encounters (e.g., inpatient, outpatient)      |
| `clinical.encounter_code_dim`  | Dimension | Encounter code and description (e.g., SNOMED-CT codes)                     |
| `clinical.reason_code_dim`     | Dimension | Reason for visit codes and descriptions                                     |
| `clinical.diagnosis_dim`       | Dimension | Diagnosis code and description (e.g., ICD-10)                               |
| `clinical.medication_dim`      | Dimension | Medication code and description                                             |
| `clinical.procedure_dim`       | Dimension | Procedure code and description                                              |
| `clinical.organization_dim`    | Dimension | Organizations providing care                                                |
| `clinical.provider_dim`        | Dimension | Providers (e.g., physicians) associated with encounters                     |
| `clinical.payer_dim`           | Dimension | Insurance payers                                                            |


- Only a subset of the Synthea dataset is modeled here for demonstration. A full production environment would likely model more clinical domains and additional data.

## Summary
Synthetic healthcare data was created for 1,000 patients using the Synthea project, then modeled this data dimensionally for analytics and built a feature store tailored for readmission prediction. Data was loaded into DuckDB for efficient querying. Two models—logistic regression and XGBoost—were trained and evaluated, selecting the best model for deployment. The system exposes a FastAPI-based prediction endpoint and a Streamlit demo app for easy interaction. The entire stack is containerized with Docker, facilitating easy deployment and testing.

## Contributions and Support
Contributions are welcome via issues or pull requests.
- Contact: Kevin Winkler
- Email: kevin.winkler1@gmail.com