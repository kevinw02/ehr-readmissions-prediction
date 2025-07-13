from ml.train import train_logistic_regression, train_xgboost


def test_train_logistic_regression_runs(synthetic_data):
    X_train, y_train, X_test, y_test = synthetic_data
    model, auc = train_logistic_regression(X_train, y_train, X_test, y_test)
    assert hasattr(model, "predict_proba")
    assert 0.0 <= auc <= 1.0


def test_train_xgboost_runs(synthetic_data):
    X_train, y_train, X_test, y_test = synthetic_data
    model, auc = train_xgboost(X_train, y_train, X_test, y_test)
    assert hasattr(model, "predict_proba")
    assert 0.0 <= auc <= 1.0
