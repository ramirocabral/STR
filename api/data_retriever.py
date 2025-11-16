import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from confluent_kafka import Consumer, KafkaException
import asyncio
import pandas as pd
import api.main as main_module
from lib.preprocessing import preprocess_data

router = APIRouter()

def create_consumer():
    conf = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'g8',
        'auto.offset.reset': 'earliest'
    }
    return Consumer(conf)

async def kafka_event_generator():
    consumer = create_consumer()
    consumer.subscribe(["energy-snapshots"])

    loop = asyncio.get_event_loop()
    
    try:
        while True:
            msg = await loop.run_in_executor(None, consumer.poll, 1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            
            try:
                data_str = msg.value().decode("utf-8")
                data_json = json.loads(data_str)
                print("MENSAJE: ", data_json)
            except Exception:
                continue

            fields = {
                "date": data_json.get("date"),
                "temperature": data_json.get("temperature"),
                "humidity": data_json.get("humidity"),
                "rain": data_json.get("rain") or 0,
                "snow": data_json.get("snow") or 0,
                "pressure": data_json.get("pressure"),
                "wind_speed": data_json.get("wind_speed"),
                "wind_direction": data_json.get("wind_direction"),
                "clouds": data_json.get("clouds"),
                "sunrise": data_json.get("sunrise"),
                "sunset": data_json.get("sunset"),
                "working_day": data_json.get("working_day"),
                "holiday": data_json.get("holiday"),
            }

            fields = {k: 0 if v is None else v for k, v in fields.items()}

            df = pd.DataFrame([fields])
            try:
                df_proc = preprocess_data(df)
                X_np = df_proc.values

                X_scaled = main_module.X_SCALER.transform(X_np)
                preds_scaled = main_module.MODEL.predict(X_scaled)
                preds = main_module.Y_SCALER.inverse_transform(preds_scaled.reshape(-1, 1))
                pred_value = float(preds[0][0])
            except Exception as e:
                yield f"event: error\ndata: {json.dumps({'error': f'Error en predicción: {str(e)}'})}\n\n"
                continue

            # Obtenemos consumo real
            consumption_real = data_json.get("consumption")
            if consumption_real is None:
                yield f"event: error\ndata: {json.dumps({'error': 'No viene consumption en mensaje'})}\n\n"
                continue

            diff_rel = abs(pred_value - consumption_real) / consumption_real if consumption_real != 0 else 0

            alert = None
            if diff_rel > 0.05:
              alert = "La predicción difiere del consumo real más de un 5%."
            else:
              alert = "Normal."

            payload = {
                "prediction": pred_value,
                "consumption_real": consumption_real,
                "difference_percent": round(diff_rel * 100, 2),
                "state": alert
            }

            yield f"event: prediction\ndata: {json.dumps(payload)}\n\n"

    except asyncio.CancelledError:
        pass
    finally:
        consumer.close()

@router.get("/stream-predictions")
async def stream_predictions():
    if main_module.MODEL is None or main_module.X_SCALER is None or main_module.Y_SCALER is None:
        raise HTTPException(500, "Modelo o escaladores no cargados")

    async def event_generator():
        async for chunk in kafka_event_generator():
            yield chunk

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no"
    })
