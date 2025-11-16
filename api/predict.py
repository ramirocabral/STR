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
        if req.instances is not None:
            X_np = np.array(req.instances, dtype=float)
            if X_np.ndim != 2:
                raise HTTPException(400, "'instances' debe ser 2D")

        else:
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
                raise HTTPException(400, "Faltan campos. O envía 'instances'.")

            df = pd.DataFrame([fields])
            df_proc = preprocess_data(df)
            X_np = df_proc.values

        X_scaled = main_module.X_SCALER.transform(X_np)
        preds_scaled = main_module.MODEL.predict(X_scaled)
        preds = main_module.Y_SCALER.inverse_transform(preds_scaled.reshape(-1, 1))

    except Exception as e:
        raise HTTPException(500, f"Error durante la predicción: {e}")

    return {
        "predictions": preds.reshape(-1).tolist(),
        "n": len(preds),
    }
