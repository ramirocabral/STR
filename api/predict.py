from fastapi import APIRouter, HTTPException
import numpy as np
import pandas as pd

from api.schemas.predict_request import PredictRequest
from lib.preprocessing import preprocess_data
import api.main as main_module

router = APIRouter()

@router.post("/predict")
def predict(req: PredictRequest):

    if main_module.MODEL is None:
        raise HTTPException(500, "Modelo no cargado.")
    if main_module.X_SCALER is None or main_module.Y_SCALER is None:
        raise HTTPException(500, "Escaladores no cargados.")

    try:
        # Requiere todos los campos, no acepta 'instances'
        fields = {
            "date": req.date,
            "temperature": req.temperature,
            "humidity": req.humidity,
            "rain": req.rain,
            "snow": req.snow,
            "pressure": req.pressure,
            "wind_speed": req.wind_speed,
            "wind_direction": req.wind_direction,
            "clouds": req.clouds,
            "sunrise": req.sunrise,
            "sunset": req.sunset,
            "working_day": req.working_day,
            "holiday": req.holiday,
        }

        if any(v is None for v in fields.values()):
            raise HTTPException(400, "Faltan campos para la predicción.")

        df = pd.DataFrame([fields])
        df_proc = preprocess_data(df)

        # pass DataFrame to scaler so feature names match and sklearn doesn't warn
        X_scaled = main_module.X_SCALER.transform(df_proc)
        preds_scaled = main_module.MODEL.predict(X_scaled)
        preds = main_module.Y_SCALER.inverse_transform(preds_scaled.reshape(-1, 1))

    except Exception as e:
        raise HTTPException(500, f"Error durante la predicción: {e}")

    # Solo un resultado, devolvemos escalar (no lista)
    return {
        "prediction": float(preds[0][0])
    }
