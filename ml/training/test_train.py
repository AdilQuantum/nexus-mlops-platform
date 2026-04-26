import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))


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


def test_generate_sample_data_shape():
    X, y = generate_sample_data(100)
    assert X.shape[0] == 100
    assert X.shape[1] == 5


def test_generate_sample_data_columns():
    X, y = generate_sample_data(100)
    expected_columns = [
        "transaction_amount",
        "transaction_hour",
        "account_age_days",
        "num_transactions_today",
        "distance_from_home"
    ]
    assert list(X.columns) == expected_columns


def test_generate_sample_data_labels():
    X, y = generate_sample_data(100)
    assert set(y.unique()).issubset({0, 1})


def test_transaction_amount_positive():
    X, y = generate_sample_data(100)
    assert (X["transaction_amount"] > 0).all()


def test_transaction_hour_range():
    X, y = generate_sample_data(100)
    assert X["transaction_hour"].between(0, 23).all()
