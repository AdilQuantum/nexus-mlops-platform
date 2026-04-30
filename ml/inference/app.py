from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
from mlflow.tracking import MlflowClient
import numpy as np
import pickle
import time
import os
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST
)
from fastapi.responses import Response

app = FastAPI(title="Nexus Inference Service", version="1.0.0")

# Prometheus metrics
PREDICTION_LATENCY = Histogram(
    "ml_prediction_latency_seconds",
    "Prediction latency in seconds"
)
PREDICTION_CONFIDENCE = Gauge(
    "ml_prediction_confidence_score",
    "Model prediction confidence"
)
REQUEST_COUNTER = Counter(
    "ml_model_requests_total",
    "Total prediction requests",
    ["status"]
)

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
MLFLOW_RUN_ID = os.getenv("MLFLOW_RUN_ID")
mlflow.set_tracking_uri(MLFLOW_URI)

model = None


def load_model():
    global model
    if not MLFLOW_RUN_ID:
        raise RuntimeError("MLFLOW_RUN_ID env var is required")
    client = MlflowClient(tracking_uri=MLFLOW_URI)
    local_path = client.download_artifacts(MLFLOW_RUN_ID, "model.pkl", "/tmp")
    with open(local_path, "rb") as f:
        model = pickle.load(f)


class PredictionRequest(BaseModel):
    features: list[float]


class PredictionResponse(BaseModel):
    prediction: int
    confidence: float
    model_version: str


@app.on_event("startup")
async def startup_event():
    try:
        load_model()
    except Exception as e:
        print(f"WARNING: model failed to load at startup: {e}")


@app.get("/health/live")
def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
def readiness():
    if model is None:
        raise HTTPException(status_code=503, detail="model not loaded")
    return {"status": "ready", "model_loaded": True}


@app.get("/health")
def health():
    return {"status": "alive", "model_loaded": model is not None}


@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post("/v1/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start = time.time()

    try:
        features = np.array([request.features])

        prediction = model.predict(features)[0]
        confidence = float(max(model.predict_proba(features)[0]))

        latency = time.time() - start
        PREDICTION_LATENCY.observe(latency)
        PREDICTION_CONFIDENCE.set(confidence)
        REQUEST_COUNTER.labels(status="success").inc()

        return PredictionResponse(
            prediction=int(prediction),
            confidence=confidence,
            model_version="1.0.0"
        )

    except Exception as e:
        REQUEST_COUNTER.labels(status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))
