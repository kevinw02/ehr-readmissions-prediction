import logging
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import make_scorer, roc_auc_score
from sklearn.model_selection import GridSearchCV

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


def train_logistic_regression(X_train, y_train, X_test, y_test):
    param_grid_lr = {
        "C": [0.01, 0.1, 1, 10],
        "solver": ["liblinear", "lbfgs"],
        "penalty": ["l2"],
    }
    lr = LogisticRegression(max_iter=1000)
    auc_scorer = make_scorer(roc_auc_score)
    grid_search_lr = GridSearchCV(
        lr, param_grid_lr, scoring=auc_scorer, cv=5, verbose=1, n_jobs=1
    )
    grid_search_lr.fit(X_train, y_train)
    best_lr = grid_search_lr.best_estimator_
    _LOGGER.info(f"Best Logistic Regression params: {grid_search_lr.best_params_}")
    preds_lr = best_lr.predict_proba(X_test)[:, 1]
    auc_lr = roc_auc_score(y_test, preds_lr)
    _LOGGER.info(f"Logistic Regression Test AUC: {auc_lr:.4f}")
    return best_lr, auc_lr


def train_xgboost(X_train, y_train, X_test, y_test):
    param_grid_xgb = {
        "n_estimators": [50, 100],
        "max_depth": [3, 6],
        "learning_rate": [0.01, 0.1],
        "subsample": [0.8, 1.0],
        "eval_metric": ["logloss"],
    }
    xgb_clf = xgb.XGBClassifier()
    auc_scorer = make_scorer(roc_auc_score)
    grid_search_xgb = GridSearchCV(
        xgb_clf, param_grid_xgb, scoring=auc_scorer, cv=5, verbose=1, n_jobs=1
    )
    grid_search_xgb.fit(X_train, y_train)
    best_xgb = grid_search_xgb.best_estimator_
    _LOGGER.info(f"Best XGBoost params: {grid_search_xgb.best_params_}")
    preds_xgb = best_xgb.predict_proba(X_test)[:, 1]
    auc_xgb = roc_auc_score(y_test, preds_xgb)
    _LOGGER.info(f"XGBoost Test AUC: {auc_xgb:.4f}")
    return best_xgb, auc_xgb
