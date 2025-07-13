import pytest
from unittest.mock import MagicMock, patch
from ml.model import ReadmissionModel


def test_model_loads_and_predicts():
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.3, 0.7]]  # simulate probability output

    with patch("ml.model.joblib.load", return_value=mock_model):
        model = ReadmissionModel()
        prob = model.predict([1, 2, 3, 4])
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 1.0
        mock_model.predict_proba.assert_called_once()
