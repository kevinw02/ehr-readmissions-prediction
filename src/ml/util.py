import logging
import os
from joblib import dump

# Configure module-level _logger
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


def save_model(model, model_dir, filename):
    filepath = os.path.join(model_dir, filename)
    dump(model, filepath)
    _logger.info(f"Model saved to {filepath}")
