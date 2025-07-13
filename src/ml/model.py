"""
Readmission model loading and prediction logic.
"""

import joblib
import numpy as np
import os

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    MODULE_DIR, "..", "..", "ml_model", "xgboost_readmission_model.joblib"
)


class ReadmissionModel:
    def __init__(self, model_path=MODEL_PATH):
        """
        Load the model from disk.
        """
        self.model = joblib.load(model_path)

    def predict(self, features: list) -> float:
        """
        Predict the probability of readmission given a feature list.

        params:
            features: List of numerical input features.

        returns: Predicted probability of readmission (0.0–1.0).
        """
        X = np.array([features])
        print("Input features to model:", X)
        return float(self.model.predict_proba(X)[0][1])
