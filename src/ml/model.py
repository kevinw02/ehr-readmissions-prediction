"""
Readmission model loading and prediction logic.
"""

import joblib
import logging
import numpy as np
import os
from typing import List

# Configure module-level _logger
_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Constants
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL_PATH = os.path.join(MODULE_DIR, "..", "..", "ml_model", "xgboost_readmission_model.joblib")


class ReadmissionModel:
    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        """
        Load the readmission prediction model from disk.

        params:
            model_path (str): Path to the serialized model file.
        """
        self.model = self._load_model(model_path)

    def predict(self, features: List[float]) -> float:
        """
        Predict the probability of readmission given input features.

        params:
            features (List[float]): List of numerical input features.

        Returns: Probability of readmission (0.0–1.0).
        """
        X = np.array([features], dtype=np.float32)
        prob = self.model.predict_proba(X)[0][1]
        _logger.debug(f"Input features: {features}, Predicted probability: {prob:.4f}")
        return float(prob)
    
    def _load_model(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at: {path}")
        _logger.info(f"Loading model from {path}")
        return joblib.load(path)
