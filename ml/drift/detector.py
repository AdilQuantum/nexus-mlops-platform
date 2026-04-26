import pandas as pd
import numpy as np
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import boto3
import json
import os
import requests
from datetime import datetime

DRIFT_THRESHOLD = float(os.getenv("DRIFT_THRESHOLD", "0.2"))
S3_BUCKET = os.getenv("S3_BUCKET", "nexus-mlops-model-artifacts-staging")
AIRFLOW_URL = os.getenv("AIRFLOW_URL", "http://airflow:8080")

def load_reference_data():
    np.random.seed(42)
    return pd.DataFrame({
        "transaction_amount": np.random.exponential(100, 1000),
        "transaction_hour": np.random.randint(0, 24, 1000),
        "account_age_days": np.random.randint(1, 3650, 1000),
        "num_transactions_today": np.random.randint(1, 50, 1000),
        "distance_from_home": np.random.exponential(50, 1000)
    })

def load_current_data():
    # In production: load from feature store or database
    np.random.seed(99)
    return pd.DataFrame({
        "transaction_amount": np.random.exponential(150, 500),
        "transaction_hour": np.random.randint(0, 24, 500),
        "account_age_days": np.random.randint(1, 3650, 500),
        "num_transactions_today": np.random.randint(1, 50, 500),
        "distance_from_home": np.random.exponential(80, 500)
    })

def run_drift_detection():
    reference = load_reference_data()
    current = load_current_data()

    report = Report(metrics=[DataDriftPreset()])
    report.run(reference_data=reference, current_data=current)

    result = report.as_dict()
    drift_detected = result["metrics"][0]["result"]["dataset_drift"]
    drift_score = result["metrics"][0]["result"]["share_of_drifted_columns"]

    print(f"Drift detected: {drift_detected}")
    print(f"Drift score: {drift_score}")

    # Upload report to S3
    s3 = boto3.client("s3")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report.save_html(f"/tmp/drift_report_{timestamp}.html")
    s3.upload_file(
        f"/tmp/drift_report_{timestamp}.html",
        S3_BUCKET,
        f"drift-reports/drift_report_{timestamp}.html"
    )

    # Trigger retraining if drift detected
    if drift_score > DRIFT_THRESHOLD:
        print(f"Drift score {drift_score} exceeded threshold {DRIFT_THRESHOLD}")
        trigger_retraining()

def trigger_retraining():
    response = requests.post(
        f"{AIRFLOW_URL}/api/v1/dags/retrain_model/dagRuns",
        json={"conf": {"triggered_by": "drift_detection"}},
        auth=("airflow", "airflow")
    )
    print(f"Retraining triggered: {response.status_code}")

if __name__ == "__main__":
    run_drift_detection()