"""
SHAP (SHapley Additive exPlanations) is a unified approach to explain the output of any machine learning model.
This module provides functionality to generate and visualize SHAP values for model interpretability.
"""

import numpy as np
import pandas as pd
import shap
from typing import Union
from sklearn.base import BaseEstimator


def explain_model(
    model: Union[BaseEstimator, object],
    X_train: Union[pd.DataFrame, np.ndarray],
    X_test: Union[pd.DataFrame, np.ndarray],
    model_type: str = "logreg",
) -> None:
    """
    Generate and plot SHAP explanations for a given model and dataset.

    Parameters:
        model (BaseEstimator or object): Trained model.
            - For 'xgboost', must be compatible with shap.Explainer.
            - For others (e.g., logistic regression), must be compatible with shap.LinearExplainer.
        X_train (DataFrame or ndarray): Training data for explainer fitting.
        X_test (DataFrame or ndarray): Test data for SHAP value computation.
        model_type (str): One of {"logreg", "xgboost"}. Determines which SHAP explainer to use.

    Returns:
        None. Displays a SHAP summary plot.

    Notes:
        - "logreg" uses shap.LinearExplainer with interventional perturbation.
        - "xgboost" uses shap.Explainer directly.
    """
    if model_type == "xgboost":
        explainer = shap.Explainer(model)
        shap_values = explainer(X_test)
    elif model_type == "logreg":
        explainer = shap.LinearExplainer(
            model, X_train, feature_perturbation="interventional"
        )
        shap_values = explainer.shap_values(X_test)
        shap_values = np.array(shap_values, dtype=np.float64)
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    shap.summary_plot(shap_values, X_test)
