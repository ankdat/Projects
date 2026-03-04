📈 Stock Price Direction Prediction (Machine Learning + Streamlit)

Predict the direction of tomorrow’s stock closing price (📈 UP / 📉 DOWN / ⚖️ NEUTRAL) using historical price data, technical indicators, and machine learning — with a live Streamlit web app.

⚠️ This project focuses on directional prediction, not exact price forecasting.

🚀 Live Demo (Local)
streamlit run gui/app.py


The app allows you to:

enter any stock ticker (e.g. AAPL, MSFT, RELIANCE.NS)

view company information

see tomorrow’s predicted direction

understand prediction confidence via probabilities

🧠 What This Project Does

Uses historical price data only

Engineers technical indicators:

RSI (14)

Moving Averages (10, 20)

Rolling Volatility (10)

Trains a Logistic Regression classifier

Predicts whether tomorrow’s close will be higher or lower than today’s

Displays:

direction (UP / DOWN / NEUTRAL)

probabilities

confidence meter

company summary

🎯 Why Directional Prediction?

Predicting exact stock prices is unrealistic in short horizons.

Instead, this project answers a more meaningful question:

Is tomorrow more likely to close higher or lower than today?

This formulation:

avoids false precision

aligns with academic financial ML practice

allows probabilistic interpretation

🖥️ Streamlit App Features

🔎 Stock ticker input

🏢 Company overview (sector, industry, country, description)

🔮 Next-day direction prediction

📊 Probability of UP vs DOWN

📈 Confidence meter

⚖️ NEUTRAL output when confidence is low

📂 Project Structure
stock_price_trend_classifier/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   └── 02_feature_engineering.ipynb
│
├── src/
│   ├── features.py
│   └── model.py
│
├── models/
│   ├── logistic_model.pkl
│   └── scaler.pkl
│
├── gui/
│   └── app.py
│
├── requirements.txt
└── README.md

⚙️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/your-username/stock-price-trend-classifier.git
cd stock-price-trend-classifier

2️⃣ Create virtual environment
python -m venv env
source env/bin/activate   # macOS / Linux

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the app
streamlit run gui/app.py

📊 Model Details

Algorithm: Logistic Regression

Problem Type: Binary Classification

Target Definition:

1 → Close(t+1) > Close(t)
0 → otherwise


Evaluation: Time-aware train/test split (no shuffling)

Typical Accuracy: ~55% (realistic for daily stock direction)

⚠️ Limitations (Important)

No exact price prediction

No trading strategy

No transaction costs

No volume or fundamental data

Short-horizon predictions are inherently noisy

This is expected and discussed openly in the project.

🧪 Key Takeaways

Financial markets have weak predictive signals

Correct methodology matters more than high accuracy

Simpler models can outperform complex ones

Probabilities are more honest than hard predictions

🔮 Future Improvements

Add volume-based indicators

Include macroeconomic data

Extend horizon (weekly prediction)

Backtesting with trading rules

Probability calibration

🎓 Academic Context

Developed as an MSc-level Machine Learning / Data Science project, with emphasis on:

data leakage prevention

realistic modeling assumptions

reproducibility

interpretability

📜 Disclaimer

This project is for educational purposes only.
It does not constitute financial advice or a trading system.