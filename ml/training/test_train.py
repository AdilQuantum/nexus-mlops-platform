import sys
import os
from train import generate_sample_data

sys.path.insert(0, os.path.dirname(__file__))


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
