import sys
from pathlib import Path

# Make project root importable
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import joblib
from pathlib import Path

from src.features import compute_rsi, compute_moving_average, compute_volatility
from src.model import (
    time_series_split,
    train_logistic_regression,
    train_random_forest,
    evaluate_model
)

from sklearn.metrics import accuracy_score, classification_report

# --------------------------------------------------
# 1️⃣ Load Data
# --------------------------------------------------
df = pd.read_csv("data/raw/AAPL.csv", parse_dates=True, index_col=0)
df = df.sort_index()
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

# --------------------------------------------------
# 2️⃣ Feature Engineering
# --------------------------------------------------
df["rsi_14"] = compute_rsi(df["Close"], 14)
df["ma_10"] = compute_moving_average(df["Close"], 10)
df["ma_20"] = compute_moving_average(df["Close"], 20)
df["volatility_10"] = compute_volatility(df["Close"], 10)

# --------------------------------------------------
# 3️⃣ Target Creation
# --------------------------------------------------
df["target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

df = df.dropna()

# --------------------------------------------------
# 4️⃣ Define Features and Target
# --------------------------------------------------
X = df[["rsi_14", "ma_10", "ma_20", "volatility_10"]]
y = df["target"]

# --------------------------------------------------
# 5️⃣ Time Series Split
# --------------------------------------------------
X_train, X_test, y_train, y_test = time_series_split(X, y)

# --------------------------------------------------
# 6️⃣ Logistic Regression
# --------------------------------------------------
model_lr, scaler = train_logistic_regression(X_train, y_train)
accuracy_lr, report_lr = evaluate_model(model_lr, scaler, X_test, y_test)

print("\n===== Logistic Regression =====")
print("Accuracy:", accuracy_lr)
print(report_lr)

# --------------------------------------------------
# 7️⃣ Random Forest
# --------------------------------------------------
model_rf = train_random_forest(X_train, y_train)

y_pred_rf = model_rf.predict(X_test)
accuracy_rf = accuracy_score(y_test, y_pred_rf)
report_rf = classification_report(y_test, y_pred_rf)

print("\n===== Random Forest =====")
print("Accuracy:", accuracy_rf)
print(report_rf)

# --------------------------------------------------
# 8️⃣ Save Logistic Model (for Streamlit)
# --------------------------------------------------
models_dir = Path("models")
models_dir.mkdir(exist_ok=True)

joblib.dump(model_lr, models_dir / "logistic_model.pkl")
joblib.dump(scaler, models_dir / "scaler.pkl")

print("\nModel and scaler saved successfully.")

from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# cm = confusion_matrix(y_test, y_pred_rf)

# plt.figure()
# sns.heatmap(cm, annot=True, fmt="d")
# plt.title("Confusion Matrix - Random Forest")
# plt.xlabel("Predicted")
# plt.ylabel("Actual")
# plt.show()

# from sklearn.metrics import roc_curve, auc

# y_prob_lr = model_lr.predict_proba(scaler.transform(X_test))[:,1]
# fpr, tpr, _ = roc_curve(y_test, y_prob_lr)

# plt.figure()
# plt.plot(fpr, tpr)
# plt.plot([0,1],[0,1], linestyle="--")
# plt.title("ROC Curve - Logistic Regression")
# plt.xlabel("False Positive Rate")
# plt.ylabel("True Positive Rate")
# plt.show()

importances = model_rf.feature_importances_

plt.figure()
plt.bar(X.columns, importances)
plt.title("Feature Importance - Random Forest")
plt.xticks(rotation=45)
plt.show()