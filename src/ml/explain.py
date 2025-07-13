import numpy as np
import pandas as pd
import shap
from typing import Union


def explain_model(
    model: object,
    X_train: Union[pd.DataFrame, np.ndarray],
    X_test: Union[pd.DataFrame, np.ndarray],
    model_type: str = "logreg",
) -> None:
    """
    Generate and plot SHAP explanations for a given model and dataset.

    params:
        model: Trained machine learning model object.
            For 'xgboost' model_type, should be an XGBoost model compatible with shap.Explainer.
            For other models, should be compatible with shap.LinearExplainer.
        X_train: Training dataset used to initialize the SHAP explainer.
        X_test: Test dataset for which SHAP values are computed.
        model_type: Type of model. Determines which SHAP explainer to use.
            Supported values are "logreg" (default) and "xgboost".

    returns: None: This function produces a SHAP summary plot as a side effect.

    Notes:
        - For "logreg" (or other non-XGBoost models), LinearExplainer with 'interventional' perturbation is used.
        - For "xgboost", the general Explainer is used.
        - The SHAP summary plot visualizes feature importance and impact.
    """
    if model_type == "xgboost":
        explainer = shap.Explainer(model)
    else:
        explainer = shap.LinearExplainer(
            model, X_train, feature_perturbation="interventional"
        )
    shap_values = explainer.shap_values(X_test)
    shap_values = np.array(shap_values, dtype=np.float64)
    shap.summary_plot(shap_values, X_test)
