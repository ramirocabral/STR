import os
from joblib import load
from tensorflow.keras.models import load_model

def find_and_load_model(models_dir: str = "models"):
    c = os.path.join(models_dir, "best_energy_model.keras")
    if os.path.exists(c):
        return load_model(c)
    raise FileNotFoundError("No se encontró un modelo válido en app/models/")


def load_scaler(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return load(path)
