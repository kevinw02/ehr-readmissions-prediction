"""
Module for training machine learning models for readmission prediction.
This module provides functions to train logistic regression and XGBoost models,
including hyperparameter tuning and evaluation using AUC.
"""

import logging
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, roc_auc_score
from typing import Tuple, Union

# Configure module-level _logger
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def train_logistic_regression(X_train, y_train, X_test, y_test) -> Tuple[LogisticRegression, float]:
    """
    Train a logistic regression model with hyperparameter tuning.
    
    params:
        X_train: Training feature set
        y_train: Training labels
        X_test: Test feature set
        y_test: Test labels
    
    Returns: Tuple of trained model and test AUC score.
    """
    param_grid = {
        "C": [0.01, 0.1, 1, 10],
        "solver": ["liblinear", "lbfgs"],
        "penalty": ["l2"],
    }
    model = LogisticRegression(max_iter=1000)
    return _train_model(model, param_grid, X_train, y_train, X_test, y_test, "Logistic Regression")


def train_xgboost(X_train, y_train, X_test, y_test) -> Tuple[xgb.XGBClassifier, float]:
    """
    Train an XGBoost model with hyperparameter tuning.

    params:
        X_train: Training feature set
        y_train: Training labels
        X_test: Test feature set
        y_test: Test labels
        
    Returns: Tuple of trained model and test AUC score.
    """
    param_grid = {
        "n_estimators": [50, 100],
        "max_depth": [3, 6],
        "learning_rate": [0.01, 0.1],
        "subsample": [0.8, 1.0],
        "eval_metric": ["logloss"],
    }
    model = xgb.XGBClassifier()
    return _train_model(model, param_grid, X_train, y_train, X_test, y_test, "XGBoost")


def _train_model(
    model,
    param_grid: dict,
    X_train,
    y_train,
    X_test,
    y_test,
    model_name: str,
) -> Tuple[Union[LogisticRegression, xgb.XGBClassifier], float]:
    """Generic model training function with grid search and AUC evaluation."""
    scorer = make_scorer(roc_auc_score)
    grid_search = GridSearchCV(
        model, param_grid, scoring=scorer, cv=5, verbose=1, n_jobs=1
    )
    grid_search.fit(X_train, y_train)

    best_model = grid_search.best_estimator_
    _logger.info(f"Best {model_name} params: {grid_search.best_params_}")

    preds = best_model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)
    _logger.info(f"{model_name} Test AUC: {auc:.4f}")

    return best_model, auc