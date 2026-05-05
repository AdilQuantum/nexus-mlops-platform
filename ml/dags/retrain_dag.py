from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import os

default_args = {
    "owner": "mlops",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow.mlflow.svc.cluster.local:5000")
DRIFT_THRESHOLD = float(os.getenv("DRIFT_THRESHOLD", "0.2"))


def check_drift(**context):
    import mlflow
    mlflow.set_tracking_uri(MLFLOW_URI)
    client = mlflow.tracking.MlflowClient()

    runs = client.search_runs(
        experiment_ids=["0"],
        filter_string="tags.component = 'drift-detection'",
        order_by=["start_time DESC"],
        max_results=1
    )

    if not runs:
        print("No drift detection runs found — skipping retrain")
        return "skip_retraining"

    drift_score = runs[0].data.metrics.get("drift_share", 0)
    print(f"Latest drift score: {drift_score:.3f}")

    if drift_score > DRIFT_THRESHOLD:
        context["ti"].xcom_push(key="drift_score", value=drift_score)
        return "retrain_model"
    return "skip_retraining"


def retrain(**context):
    import mlflow
    import pandas as pd
    import numpy as np
    import pickle
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score

    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment("fraud-detection")

    np.random.seed(int(datetime.now().timestamp()) % 100000)
    n = 1000
    X = pd.DataFrame({
        "transaction_amount": np.random.exponential(100, n),
        "transaction_hour": np.random.randint(0, 24, n),
        "account_age_days": np.random.randint(1, 3650, n),
        "num_transactions_today": np.random.randint(1, 50, n),
        "distance_from_home": np.random.exponential(50, n)
    })
    y = ((X["transaction_amount"] > 300) & (X["distance_from_home"] > 100)).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    with mlflow.start_run(run_name="airflow-retrain") as run:
        model = RandomForestClassifier(n_estimators=100, max_depth=6)
        model.fit(X_train, y_train)

        f1 = f1_score(y_test, model.predict(X_test))
        mlflow.log_metric("f1_score", f1)
        mlflow.set_tag("triggered_by", "airflow-drift-pipeline")

        with open("/tmp/model.pkl", "wb") as f:
            pickle.dump(model, f)
        mlflow.log_artifact("/tmp/model.pkl", artifact_path="")

        run_id = run.info.run_id
        print(f"Retrained model. Run ID: {run_id} | F1: {f1:.4f}")
        context["ti"].xcom_push(key="new_run_id", value=run_id)
        context["ti"].xcom_push(key="new_f1", value=f1)


def validate_and_deploy(**context):
    import mlflow
    ti = context["ti"]
    new_run_id = ti.xcom_pull(task_ids="retrain_model", key="new_run_id")
    new_f1 = ti.xcom_pull(task_ids="retrain_model", key="new_f1")

    mlflow.set_tracking_uri(MLFLOW_URI)
    client = mlflow.tracking.MlflowClient()

    current_run_id = os.getenv("CURRENT_MLFLOW_RUN_ID", "")
    current_f1 = 0.0
    if current_run_id:
        try:
            current_f1 = client.get_run(current_run_id).data.metrics.get("f1_score", 0)
        except Exception:
            pass

    print(f"Current F1: {current_f1:.4f} → New F1: {new_f1:.4f}")

    with mlflow.start_run(run_name="model-validation"):
        mlflow.log_metric("current_f1", current_f1)
        mlflow.log_metric("new_f1", new_f1)
        mlflow.log_param("new_run_id", new_run_id)
        mlflow.log_param("deploy_decision", "deploy" if new_f1 > current_f1 else "keep_current")

    if new_f1 > current_f1:
        # Production path: update MLFLOW_RUN_ID in k8s manifest via git + ArgoCD
        print(f"DEPLOY: update MLFLOW_RUN_ID={new_run_id} in k8s/inference-deployment.yaml")
    else:
        print("New model not better — keeping current deployment")


with DAG(
    "retrain_model",
    default_args=default_args,
    description="Automated retraining triggered by drift detection",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["mlops", "retraining"],
) as dag:

    check = BranchPythonOperator(
        task_id="check_drift",
        python_callable=check_drift,
    )

    retrain_task = PythonOperator(
        task_id="retrain_model",
        python_callable=retrain,
    )

    validate = PythonOperator(
        task_id="validate_and_deploy",
        python_callable=validate_and_deploy,
    )

    skip = EmptyOperator(task_id="skip_retraining")

    check >> [retrain_task, skip]
    retrain_task >> validate
