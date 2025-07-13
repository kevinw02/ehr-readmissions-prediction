import logging
import os
from joblib import dump

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


def save_model(model, model_dir, filename):
    filepath = os.path.join(model_dir, filename)
    dump(model, filepath)
    _LOGGER.info(f"Model saved to {filepath}")
