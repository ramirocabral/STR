from fastapi import FastAPI

from api.predict import router as predict_router
from api.data_retriever import router as data_retriever_router
from ml.loader import find_and_load_model, load_scaler
# import sys
import os

app = FastAPI(title="Energy Consumption Inference")

MODEL = None
X_SCALER = None
Y_SCALER = None

SCALER_DIR = "models"
X_SCALER_PATH = os.path.join(SCALER_DIR, "x_scaler.joblib")
Y_SCALER_PATH = os.path.join(SCALER_DIR, "y_scaler.joblib")


@app.on_event("startup")
def startup():
    global MODEL, X_SCALER, Y_SCALER
    try:
        MODEL = find_and_load_model()
        X_SCALER = load_scaler(X_SCALER_PATH)
        Y_SCALER = load_scaler(Y_SCALER_PATH)
    except Exception as e:
        print(f"Error al cargar recursos: {e}")


@app.get("/health")
def health():
    return {
        "model_loaded": MODEL is not None,
        "scalers_loaded": X_SCALER is not None and Y_SCALER is not None,
    }

app.include_router(predict_router)
app.include_router(data_retriever_router)