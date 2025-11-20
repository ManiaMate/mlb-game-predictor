from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# Create confusion matrix for binary classfication
def plot_confusion_matrix(y_true, y_pred, title="Confusion Matrix"):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6,4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Pred Away (0)", "Pred Home (1)"],
                yticklabels=["True Away (0)", "True Home (1)"])
    plt.title(title)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

# Season long stats
feature_cols = [
    "Home_ERA_before", "Home_FIP_before", "Home_WHIP_before",
    "Home_K9_before", "Home_BB9_before", "Home_HR9_before",
    "Home_IP_per_start_before",
    "Away_ERA_before", "Away_FIP_before", "Away_WHIP_before",
    "Away_K9_before", "Away_BB9_before", "Away_HR9_before",
    "Away_IP_per_start_before",

    # Vegas moneylines
    "Away ML",
    "Home ML",

    "Home_ERA_last3_before", "Home_WHIP_last3_before", "Home_K9_last3_before",
    "Home_BB9_last3_before", "Home_HR9_last3_before", "Home_IP_last3_before",
    "Away_ERA_last3_before", "Away_WHIP_last3_before", "Away_K9_last3_before",
    "Away_BB9_last3_before", "Away_HR9_last3_before", "Away_IP_last3_before",
]

df = pd.read_csv("mlb-2025-with-starter-stats.csv")

# Fix ml to be actual floats
for col in ["Home ML", "Away ML"]:
    df[col] = df[col].replace("-", np.nan)
    df[col] = pd.to_numeric(df[col], errors="coerce")


# Train-test split on logistic regression / decision tree
X = df[feature_cols].fillna(0)
y = df["Home_Win"]

cutoff_date = "2025-09-01"

train_mask = df["Date_Start"] < cutoff_date
test_mask  = df["Date_Start"] >= cutoff_date

X_train = X[train_mask]
y_train = y[train_mask]

X_test = X[test_mask]
y_test = y[test_mask]

clf = LogisticRegression(max_iter=2000)
clf.fit(X_train, y_train)

pred_lf = clf.predict(X_test)
prob_lf = clf.predict_proba(X_test)[:, 1]

print("LR Accuracy:", accuracy_score(y_test, pred_lf))
print("LR AUC:", roc_auc_score(y_test, prob_lf))

rf = RandomForestClassifier(
    n_estimators=400,
    max_depth=12,
    min_samples_split=20,
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)

pred_rf = rf.predict(X_test)
prob_rf = rf.predict_proba(X_test)[:, 1]

print("RF Accuracy:", accuracy_score(y_test, pred_rf))
print("RF AUC:", roc_auc_score(y_test, prob_rf))

# random predictions (0 or 1 with equal probability)
rand_pred = np.random.randint(0, 2, size=len(y_test))

# random probabilities (0–1 uniform)
rand_prob = np.random.rand(len(y_test))

print("Random Accuracy:", accuracy_score(y_test, rand_pred))
print("Random AUC:", roc_auc_score(y_test, rand_prob))

plot_confusion_matrix(y_test, pred_lf, title="Logistic Regression")
plot_confusion_matrix(y_test, pred_rf, title="Random Forest")

