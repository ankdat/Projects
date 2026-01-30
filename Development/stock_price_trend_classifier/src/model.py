from typing import Tuple

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report


def time_series_split(
    X: pd.DataFrame,
    y: pd.Series,
    train_ratio: float = 0.8
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split features and target into train and test sets
    while preserving time order.
    """
    split_index = int(len(X) * train_ratio)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    return X_train, X_test, y_train, y_test


def train_logistic_regression(
    X_train: pd.DataFrame,
    y_train: pd.Series
):
    """
    Train Logistic Regression with feature scaling.
    Returns trained model and scaler.
    """
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_scaled, y_train)

    return model, scaler


def evaluate_model(
    model,
    scaler,
    X_test: pd.DataFrame,
    y_test: pd.Series
):
    """
    Evaluate model on test data and print metrics.
    """
    X_test_scaled = scaler.transform(X_test)
    y_pred = model.predict(X_test_scaled)

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    return accuracy, report

from sklearn.ensemble import RandomForestClassifier


def train_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series
):
    """
    Train a Random Forest classifier.
    """
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=5,
        min_samples_split=20,
        min_samples_leaf=10,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    return model


