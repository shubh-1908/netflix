# backend/ml/churn_visuals.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "churn_results.csv")

df = pd.read_csv(DATA_PATH)

# Plot 1: Distribution
plt.figure(figsize=(7, 4))
sns.histplot(df["churn_probability"], bins=10, kde=True, color="red")
plt.title("Churn Probability Distribution")
plt.xlabel("Churn Probability")
plt.ylabel("Users")
plt.savefig(os.path.join(BASE_DIR, "churn_probability_plot.png"))
plt.close()
print("📊 churn_probability_plot.png saved!")

# Plot 2: Top high-risk users
df_sorted = df.sort_values(by="churn_probability", ascending=False).head(5)
plt.figure(figsize=(7, 4))
sns.barplot(x="churn_probability", y=df_sorted.index, data=df_sorted, color="crimson")
plt.title("Top 5 High-Risk Users")
plt.xlabel("Churn Probability")
plt.ylabel("User Index")
plt.savefig(os.path.join(BASE_DIR, "top_risky_users.png"))
plt.close()
print("📊 top_risky_users.png saved!")
