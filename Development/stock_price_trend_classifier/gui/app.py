import sys
from pathlib import Path

# --------------------------------------------------
# Make project root importable
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import yfinance as yf
import joblib

from src.features import (
    compute_rsi,
    compute_moving_average,
    compute_volatility
)

# --------------------------------------------------
# Load trained model and scaler
# --------------------------------------------------
model = joblib.load(PROJECT_ROOT / "models" / "logistic_model.pkl")
scaler = joblib.load(PROJECT_ROOT / "models" / "scaler.pkl")

# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.set_page_config(
    page_title="Tomorrow's Close Predictor",
    layout="centered"
)

st.title("📈 Tomorrow’s Stock Close Predictor")

st.write(
    """
This app predicts whether tomorrow’s closing price
is likely to be higher or lower than today’s,  
using historical price data and a trained ML model.

⚠️ Predictions are **probabilistic**, not guaranteed.
"""
)

ticker = st.text_input(
    "Enter stock ticker (e.g. AAPL, MSFT, GOOGL, RELIANCE.NS):"
)

# --------------------------------------------------
# Main logic
# --------------------------------------------------
if st.button("Analyze Stock"):
    if not ticker:
        st.error("Please enter a stock ticker.")
    else:
        try:
            # ==================================================
            # 1️⃣ COMPANY SUMMARY (SAFE BLOCK)
            # ==================================================
            stock = yf.Ticker(ticker)

            info = stock.info

            company_name = info.get("longName", "N/A")
            sector = info.get("sector", "N/A")
            industry = info.get("industry", "N/A")
            country = info.get("country", "N/A")
            summary = info.get("longBusinessSummary", "No summary available.")

            st.subheader(f"🏢 {company_name}")
            st.markdown(
                f"""
**Sector:** {sector}  
**Industry:** {industry}  
**Country:** {country}
"""
            )

            with st.expander("📄 Company Description"):
                st.write(summary)

            st.markdown("---")

            # ==================================================
            # 2️⃣ PRICE DATA FOR PREDICTION
            # ==================================================
            df = yf.download(
                ticker,
                period="2y",
                auto_adjust=False,
                progress=False
            )

            # FIX: Flatten MultiIndex columns
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            if df.empty:
                st.error("No historical price data available.")
                st.stop()

            df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

            # ==================================================
            # 3️⃣ FEATURE ENGINEERING
            # ==================================================
            df["rsi_14"] = compute_rsi(df["Close"], 14)
            df["ma_10"] = compute_moving_average(df["Close"], 10)
            df["ma_20"] = compute_moving_average(df["Close"], 20)
            df["volatility_10"] = compute_volatility(df["Close"], 10)

            df = df.dropna()

            if df.empty:
                st.error("Not enough data to compute indicators.")
                st.stop()

            # ==================================================
            # 4️⃣ SAFE FEATURE VECTOR
            # ==================================================
            last = df.iloc[-1]

            X_today = [[
                float(last["rsi_14"]),
                float(last["ma_10"]),
                float(last["ma_20"]),
                float(last["volatility_10"]),
            ]]

            X_today_scaled = scaler.transform(X_today)

            # ==================================================
            # 5️⃣ PREDICTION + PROBABILITIES
            # ==================================================
            pred = int(model.predict(X_today_scaled)[0])
            probs = model.predict_proba(X_today_scaled)[0]

            prob_down = probs[0]
            prob_up = probs[1]

            # NEUTRAL ZONE (academic best practice)
            if prob_up >= 0.55:
                direction = "UP 📈"
            elif prob_down >= 0.55:
                direction = "DOWN 📉"
            else:
                direction = "NEUTRAL ⚖️"

            st.subheader("Tomorrow’s Prediction")
            st.success(f"**Direction:** {direction}")

            col1, col2 = st.columns(2)
            col1.metric("📈 Probability UP", f"{prob_up*100:.2f}%")
            col2.metric("📉 Probability DOWN", f"{prob_down*100:.2f}%")

            st.write("### Confidence Meter")
            st.progress(max(prob_up, prob_down))

        except Exception as e:
            st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption(
    "⚠️ Educational use only. This is not financial advice."
)
