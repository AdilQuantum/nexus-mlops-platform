import mlflow
import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score
import os

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment("fraud-detection")


def generate_sample_data(n_samples=1000):
    np.random.seed(42)
    X = pd.DataFrame({
        "transaction_amount": np.random.exponential(100, n_samples),
        "transaction_hour": np.random.randint(0, 24, n_samples),
        "account_age_days": np.random.randint(1, 3650, n_samples),
        "num_transactions_today": np.random.randint(1, 50, n_samples),
        "distance_from_home": np.random.exponential(50, n_samples)
    })
    y = (
        (X["transaction_amount"] > 300) &
        (X["distance_from_home"] > 100)
    ).astype(int)
    return X, y


def train():
    X, y = generate_sample_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    with mlflow.start_run():
        params = {
            "n_estimators": 100,
            "max_depth": 6,
            "random_state": 42
        }

        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        f1 = f1_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)

        mlflow.log_params(params)
        mlflow.log_metric("f1_score", f1)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)

        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name="fraud-detection-model"
        )

        print(f"F1: {f1:.4f} | Precision: {precision:.4f} | Recall: {recall:.4f}")
        print(f"Run ID: {mlflow.active_run().info.run_id}")


if __name__ == "__main__":
    train()