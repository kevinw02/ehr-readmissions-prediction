import argparse
import logging
import os
import yaml
from db.connection import create_db_connection
from ml.explain import explain_model
from ml.train import train_logistic_regression, train_xgboost
from ml.util import save_model

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(SCRIPT_DIR, "..", "ml_model")
FEATURES = [
    "age_at_encounter",
    "gender_key",
    "race_key",
    "ethnicity_key",
    "has_diabetes",
    "has_hypertension",
    "has_copd",
    "has_asthma",
    "has_heart_failure",
    "has_arthritis",
    "has_depression",
    "has_kidney_disease",
    "has_cancer",
    "has_alzheimers",
    "chronic_dx_count",
    "num_meds",
    "has_anticoagulant",
    "has_antibiotic",
    "has_steroid",
    "num_procedures",
    "had_surgery",
    "had_biopsy",
]

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


def _arg_parse():
    parser = argparse.ArgumentParser(
        description="Train and tune logistic regression and xgboost models for readmission prediction."
    )
    parser.add_argument(
        "--config-path",
        type=str,
        default="data/duckdb_config.yaml",
        help="Path to db YAML configuration file.",
    )
    return parser.parse_args()


# This is pretty specific for the readmission use case
def _load_data(conn, features):
    df = conn.execute("SELECT * FROM readmission.encounter_fact")
    df = df.sort_values("encounter_start")
    train = df[df["encounter_start"] < "2018-01-01"]
    test = df[df["encounter_start"] >= "2018-01-01"]
    X_train = train[features]
    y_train = train["readmitted"]
    X_test = test[features]
    y_test = test["readmitted"]
    return X_train, y_train, X_test, y_test


if __name__ == "__main__":
    args = _arg_parse()
    with open(args.config_path) as f:
        config = yaml.safe_load(f)
    conn = create_db_connection(config)

    X_train, y_train, X_test, y_test = _load_data(conn, FEATURES)

    best_lr, auc_lr = train_logistic_regression(X_train, y_train, X_test, y_test)
    best_xgb, auc_xgb = train_xgboost(X_train, y_train, X_test, y_test)

    if auc_xgb > auc_lr:
        best_model = best_xgb
        model_name = "xgboost_readmission_model.joblib"
        _LOGGER.info("XGBoost selected as best model.")
        explain_model(best_model, X_train, X_test, model_type="xgboost")
    else:
        best_model = best_lr
        model_name = "logreg_readmission_model.joblib"
        _LOGGER.info("Logistic Regression selected as best model.")
        explain_model(best_model, X_train, X_test, model_type="logreg")

    save_input = input("Save model? (y/n): ").strip().lower()
    if save_input == "y":
        save_model(best_model, MODEL_DIR, model_name)
    else:
        _LOGGER.info("Model not saved.")
