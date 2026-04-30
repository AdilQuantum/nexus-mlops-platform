import mlflow
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

mlflow.set_tracking_uri("http://localhost:5000")

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y)

model = RandomForestClassifier()
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)

with mlflow.start_run():
    mlflow.log_param("model", "RandomForest")
    mlflow.log_metric("accuracy", accuracy)

    # 🔥 Save model manually
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

    # 🔥 Log as artifact (no version conflict)
    mlflow.log_artifact("model.pkl")

print("DONE")