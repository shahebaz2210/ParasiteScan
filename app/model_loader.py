import os
import sys

try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("Warning: TensorFlow not found. Running in UI-Only Mock Mode.")

# Use absolute pathing so it doesn't matter where the script is executed from
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(ROOT_DIR, 'models', 'parasitescan_best.h5')
_model = None

def get_model():
    """
    Loads and caches the model to avoid reloading on every request.
    """
    global _model
    if not TF_AVAILABLE:
        raise Exception("TensorFlow is not available. Mock mode enabled.")
        
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at absolute path {MODEL_PATH}")
        print(f"Loading model from {MODEL_PATH}...")
        _model = load_model(MODEL_PATH)
    return _model

def get_model_metrics():
    """
    Returns static mock metrics or reads from a log file.
    In a real app, this might read from an evaluation output JSON.
    """
    return {
        "accuracy": 0.9899,
        "auc": 0.9950,
        "status": "Ready",
        "last_trained": "Today"
    }
