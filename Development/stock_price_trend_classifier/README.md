# 📈 Next-Day Stock Movement Classification

A machine learning project that predicts whether a stock's **next-day closing price will move UP or DOWN** using historical market data and technical indicators.

The project compares **Logistic Regression** and **Random Forest** classifiers and deploys the trained model through an interactive **Streamlit web application**.

This project was developed as part of the **M.Sc. Data Science program at Symbiosis School for Online and Digital Learning**.

---

# 🚀 Project Overview

Financial markets are noisy, dynamic, and difficult to predict. Instead of forecasting exact prices, this project formulates stock prediction as a **binary classification problem**:

Will tomorrow's closing price be higher or lower than today's?

The system:

1. Fetches historical stock data from **Yahoo Finance**
2. Computes **technical indicators**
3. Trains machine learning models
4. Evaluates performance using classification metrics
5. Deploys predictions through a **Streamlit GUI**

---

# 📊 Models Implemented

Two machine learning models are implemented and compared:

### Logistic Regression
- Linear classifier
- Uses **feature scaling**
- Produces probabilistic predictions
- Performed best in experiments

### Random Forest
- Ensemble tree-based model
- Captures nonlinear feature interactions
- Uses bagging and feature randomness

---

# 📉 Model Performance

| Model | Accuracy | Macro F1 Score |
|------|------|------|
| Logistic Regression | **54.55%** | **0.53** |
| Random Forest | 41.41% | 0.38 |

Results show that **Logistic Regression generalizes better** for this dataset and feature set.

---

# 🧠 Features Used

Technical indicators derived from historical price data:

- **RSI (Relative Strength Index)**
- **MA10 (10-day Moving Average)**
- **MA20 (20-day Moving Average)**
- **Rolling Volatility**

These indicators capture:

- momentum
- short-term trends
- market uncertainty

---

# 🖥️ Streamlit Application

The project includes a **Streamlit GUI** that allows users to:

- Enter any stock ticker (e.g. `AAPL`, `MSFT`, `RELIANCE.NS`)
- Retrieve company information
- Compute technical indicators
- Generate next-day movement prediction
- Display probability scores

Example output:
Prediction: UP 📈
Probability UP: 61%
Probability DOWN: 39%


---

# 🗂 Project Structure
stock_price_trend_classifier

data/
raw/

models/
logistic_model.pkl
scaler.pkl

src/
data_fetch.py
features.py
model.py
train_pipeline.py

gui/
app.py

README.md
requirements.txt


---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/ankdat/stock_price_trend_classifier.git
cd stock_price_trend_classifier

Create virtual environment:

python -m venv env
source env/bin/activate

Install dependencies:

pip install -r requirements.txt
▶️ Train the Model

Run the training pipeline:

python src/train_pipeline.py

This will:

fetch historical stock data

generate features

train models

save trained model files

▶️ Run the Streamlit App
streamlit run gui/app.py

The web interface will open in your browser.

📦 Data Source

Historical stock market data is retrieved using:

yfinance API

Data provided by Yahoo Finance

📚 Technologies Used

Python

pandas

NumPy

scikit-learn

yfinance

Streamlit

matplotlib

seaborn

🎓 Academic Context

This project was developed as part of the M.Sc. Data Science program at Symbiosis School for Online and Digital Learning.

Project Title:

Next-Day Stock Movement Classification Using Logistic Regression and Random Forest

Author:
Ankan Datta

⚠️ Disclaimer

This project is intended for educational and research purposes only.

It does not constitute financial advice. Stock market predictions are inherently uncertain.

📬 Future Improvements

Potential extensions include:

XGBoost / LightGBM models

Walk-forward validation

Multi-stock training

Sentiment analysis integration

Deep learning models (LSTM / GRU)

⭐ If you found this project useful

Consider giving the repository a star ⭐.