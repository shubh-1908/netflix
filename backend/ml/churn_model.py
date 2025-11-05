import pandas as pd
import joblib
import os
import sys
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

# ✅ Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# ✅ Load dataset
data_path = os.path.join(os.path.dirname(__file__), "netflix_churn_data.csv")
if not os.path.exists(data_path):
    print(f"❌ Dataset not found at {data_path}")
    sys.exit(1)

df = pd.read_csv(data_path)

# ✅ Convert columns to numeric safely
numeric_cols = [
    "user_id", "num_videos_watched", "avg_watch_time_per_day",
    "last_login_days_ago", "support_tickets", "tenure_months", "churn"
]
for col in numeric_cols:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

# ✅ Define features & target
X = df[["user_id", "num_videos_watched", "avg_watch_time_per_day",
        "last_login_days_ago", "support_tickets", "tenure_months"]]
y = df["churn"]

# ✅ Handle small datasets
if len(df) < 5:
    print(f"⚠️ Not enough data to train real model — only {len(df)} records found.")
    print("🧩 Training DummyClassifier instead (predicts 0 for all users).")
    model = DummyClassifier(strategy="most_frequent")
    model.fit(X, y)
else:
    # ✅ Ensure two churn classes exist
    if len(y.unique()) == 1:
        print("⚠️ Only one churn class found. Adding synthetic churn=1 samples.")
        y = y.copy()
        y.iloc[: int(max(1, 0.3 * len(y)))] = 1

    # ✅ Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # ✅ Define models
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="logloss"),
    }

    best_model = None
    best_auc = 0

    for name, model in models.items():
        try:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            proba = model.predict_proba(X_test)
            probs = proba[:, 1] if proba.shape[1] > 1 else [0.0] * len(X_test)

            acc = accuracy_score(y_test, preds)
            prec = precision_score(y_test, preds, zero_division=0)
            rec = recall_score(y_test, preds, zero_division=0)
            f1 = f1_score(y_test, preds, zero_division=0)
            auc = roc_auc_score(y_test, probs) if len(set(y_test)) > 1 else 0.5

            print(f"\n🔹 {name} Results:")
            print(f"Accuracy:  {acc:.3f}")
            print(f"Precision: {prec:.3f}")
            print(f"Recall:    {rec:.3f}")
            print(f"F1 Score:  {f1:.3f}")
            print(f"ROC-AUC:   {auc:.3f}")

            if auc > best_auc:
                best_auc = auc
                best_model = model
        except Exception as e:
            print(f"⚠️ Error training {name}: {e}")

    # ✅ Fallback: if no model trained successfully
    if best_model is None:
        print("⚠️ No valid model trained — using DummyClassifier.")
        best_model = DummyClassifier(strategy="most_frequent")
        best_model.fit(X, y)
    model = best_model

# ✅ Save final model
model_path = os.path.join(os.path.dirname(__file__), "churn_model.pkl")
joblib.dump(model, model_path)
print(f"\n✅ Model saved successfully at {model_path}")
