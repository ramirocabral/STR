import json
import os
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from confluent_kafka import Consumer, KafkaException
import asyncio
import pandas as pd
import api.main as main_module
from lib.preprocessing import preprocess_data

router = APIRouter()

# CSV storage for retrieved data (used for periodic retraining)
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = DATA_DIR / "new_data.csv"

# How many retrieved records before triggering retraining (24h = 288 iterations)
RETRAIN_INTERVAL = 288

# Initialize record counter from existing file
try:
    if CSV_PATH.exists():
        with CSV_PATH.open("r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)
        RECORD_COUNT = max(0, lines - 1)
    else:
        RECORD_COUNT = 0
except Exception:
    RECORD_COUNT = 0

# Retraining state and archive
RETRAIN_RUNNING = False
ARCHIVE_DIR = DATA_DIR / "archive"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

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

                # pass DataFrame to scaler to preserve feature names and avoid sklearn warning
                X_scaled = main_module.X_SCALER.transform(df_proc)
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

            # Append the raw record to CSV for retraining later
            try:
                record = {
                    "date": fields.get("date"),
                    "temperature": fields.get("temperature"),
                    "humidity": fields.get("humidity"),
                    "rain": fields.get("rain"),
                    "snow": fields.get("snow"),
                    "pressure": fields.get("pressure"),
                    "wind_speed": fields.get("wind_speed"),
                    "wind_direction": fields.get("wind_direction"),
                    "clouds": fields.get("clouds"),
                    "sunrise": fields.get("sunrise"),
                    "sunset": fields.get("sunset"),
                    "working_day": fields.get("working_day"),
                    "holiday": fields.get("holiday"),
                    "consumption": consumption_real,
                }
                df_append = pd.DataFrame([record])
                write_header = not CSV_PATH.exists()
                df_append.to_csv(CSV_PATH, mode="a", header=write_header, index=False)

                # update counter and possibly trigger retraining
                global RECORD_COUNT
                RECORD_COUNT += 1
            except Exception as e:
                print(f"Warning: could not append record to CSV: {e}")

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

            # If we've collected enough new records, trigger retraining asynchronously
            try:
                if RECORD_COUNT > 0 and RECORD_COUNT % RETRAIN_INTERVAL == 0:
                    async def _run_retraining():
                        global RETRAIN_RUNNING, RECORD_COUNT
                        if RETRAIN_RUNNING:
                            print("Retraining already running, skipping new trigger")
                            return
                        RETRAIN_RUNNING = True
                        retrain_path = str(REPO_ROOT / "api" / "retraining.py")
                        print(f"Triggered retraining using {retrain_path}")
                        try:
                            proc = await asyncio.create_subprocess_exec(
                                sys.executable, retrain_path,
                                cwd=str(REPO_ROOT),
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE,
                            )
                            out, err = await proc.communicate()
                            if out:
                                print("Retraining stdout:", out.decode())
                            if err:
                                print("Retraining stderr:", err.decode())

                            # If retraining succeeded, archive the CSV and reset counter
                            if proc.returncode == 0:
                                try:
                                    from datetime import datetime
                                    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
                                    archive_name = ARCHIVE_DIR / f"new_data_{ts}.csv"
                                    # move current CSV to archive
                                    if CSV_PATH.exists():
                                        CSV_PATH.replace(archive_name)
                                    # recreate empty CSV file (so header will be written by next append)
                                    CSV_PATH.touch()
                                    RECORD_COUNT = 0
                                    print(f"Retraining succeeded — archived CSV to {archive_name} and reset counter")
                                except Exception as e:
                                    print(f"Warning: could not archive/reset CSV after retraining: {e}")
                            else:
                                print(f"Retraining process exited with code {proc.returncode}")
                        except Exception as e:
                            print(f"Error launching retraining: {e}")
                        finally:
                            RETRAIN_RUNNING = False

                    # schedule retraining but don't block the stream
                    asyncio.create_task(_run_retraining())
            except Exception as e:
                print(f"Error checking/triggering retraining: {e}")

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
