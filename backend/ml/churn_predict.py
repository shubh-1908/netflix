import pandas as pd
import joblib
import os
import sys

# ✅ Fix Windows console encoding to support emojis / UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# ✅ Load trained model safely
model_path = os.path.join(os.path.dirname(__file__), "churn_model.pkl")

if not os.path.exists(model_path):
    print(f"⚠️ Model file not found at {model_path}. Please run churn_model.py first.")
    sys.exit(1)

model = joblib.load(model_path)

if model is None:
    print("⚠️ Loaded model is None. Please retrain using churn_model.py.")
    sys.exit(1)

# ✅ Load exported churn data
data_path = os.path.join(os.path.dirname(__file__), "netflix_churn_data.csv")

if not os.path.exists(data_path):
    print(f"⚠️ Data file not found at {data_path}. Run the backend /api/admin/run-churn endpoint first.")
    sys.exit(1)

df = pd.read_csv(data_path)

# ✅ Expected features in same order used in churn_model.py
expected_features = [
    "user_id",
    "num_videos_watched",
    "avg_watch_time_per_day",
    "last_login_days_ago",
    "support_tickets",
    "tenure_months"
]

# ✅ Ensure all required columns exist
for col in expected_features:
    if col not in df.columns:
        if col == "support_tickets":
            df[col] = 0
        elif col == "tenure_months":
            df[col] = 6
        else:
            df[col] = 0

# ✅ Reorder columns strictly to match model training
df_features = df[expected_features]
df_features = df_features.apply(pd.to_numeric, errors="coerce").fillna(0)

# ✅ Predict churn probabilities
try:
    probs = model.predict_proba(df_features)

    if probs.shape[1] == 1:
        print("⚠️ Only one probability column detected — using fallback probability.")
        df["churn_probability"] = probs[:, 0]
    else:
        df["churn_probability"] = probs[:, 1]

    # ✅ Save the output
    output_path = os.path.join(os.path.dirname(__file__), "churn_results.csv")
    df.to_csv(output_path, index=False)

    print(f"✅ Churn prediction complete! Saved at {output_path}")

except Exception as e:
    print("❌ Error during prediction:", e)
