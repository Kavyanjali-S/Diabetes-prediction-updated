import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report, roc_curve
)
import joblib

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("static/eda_plots", exist_ok=True)

def generate_or_load_dataset():
    csv_path = "data/diabetes.csv"
    if os.path.exists(csv_path):
        print(f"Loading existing dataset from {csv_path}...")
        df = pd.read_csv(csv_path)
    else:
        print("Generating standard benchmark PIMA diabetes dataset...")
        np.random.seed(42)
        n_samples = 800

        # Simulating realistic distributions based on PIMA diabetes dataset stats
        pregnancies = np.random.poisson(lam=3.8, size=n_samples)
        pregnancies = np.clip(pregnancies, 0, 17)

        age = np.random.gamma(shape=4.0, scale=8.0, size=n_samples) + 21
        age = np.clip(age, 21, 81).astype(int)

        bmi = np.random.normal(loc=32.0, scale=6.5, size=n_samples)
        bmi = np.clip(bmi, 18.0, 55.0).round(1)

        glucose = np.random.normal(loc=120.0, scale=30.0, size=n_samples)
        # Shift glucose higher for higher age & BMI
        glucose += (age - 30) * 0.4 + (bmi - 25) * 0.8
        glucose = np.clip(glucose, 60.0, 200.0).round(1)

        blood_pressure = np.random.normal(loc=72.0, scale=12.0, size=n_samples)
        blood_pressure += (age - 30) * 0.2 + (bmi - 25) * 0.3
        blood_pressure = np.clip(blood_pressure, 40.0, 122.0).round(1)

        skin_thickness = np.random.normal(loc=20.5, scale=10.0, size=n_samples)
        skin_thickness = np.clip(skin_thickness, 7.0, 60.0).round(1)

        insulin = np.random.exponential(scale=80.0, size=n_samples) + 15
        insulin += (glucose - 100) * 0.7
        insulin = np.clip(insulin, 15.0, 450.0).round(1)

        dpf = np.random.exponential(scale=0.35, size=n_samples) + 0.08
        dpf = np.clip(dpf, 0.08, 2.42).round(3)

        # Logit equation for realistic risk outcome probability
        logit = (
            -7.5
            + 0.035 * glucose
            + 0.075 * bmi
            + 0.03 * age
            + 0.12 * pregnancies
            + 0.9 * dpf
            + 0.01 * insulin
            + 0.008 * blood_pressure
        )
        prob = 1 / (1 + np.exp(-logit))
        outcome = (np.random.binomial(1, prob) == 1).astype(int)

        df = pd.DataFrame({
            'Pregnancies': pregnancies,
            'Glucose': glucose,
            'BloodPressure': blood_pressure,
            'SkinThickness': skin_thickness,
            'Insulin': insulin,
            'BMI': bmi,
            'DiabetesPedigreeFunction': dpf,
            'Age': age,
            'Outcome': outcome
        })

        df.to_csv(csv_path, index=False)
        print(f"Dataset successfully saved to {csv_path} ({len(df)} records).")

    return df

def preprocess_and_eda(df):
    print("\n--- Performing Data Preprocessing & EDA ---")
    
    # Check zero values in biologically non-zero columns
    zero_cols = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']
    df_clean = df.copy()
    
    for col in zero_cols:
        zero_count = (df_clean[col] == 0).sum()
        if zero_count > 0:
            print(f"Imputing {zero_count} zeros in '{col}' with median value...")
            median_val = df_clean[df_clean[col] != 0][col].median()
            df_clean[col] = df_clean[col].replace(0, median_val)

    # 1. Correlation Heatmap
    plt.figure(figsize=(10, 8))
    sns.set_theme(style="whitegrid")
    corr = df_clean.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="vlag", vmin=-1, vmax=1, square=True, linewidths=.5)
    plt.title("Diabetes Risk Factor Correlation Heatmap", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()
    plt.savefig("static/eda_plots/correlation_matrix.png", dpi=300)
    plt.close()

    # 2. Risk Distribution Plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    sns.histplot(data=df_clean, x='Glucose', hue='Outcome', kde=True, ax=axes[0, 0], palette="Set2")
    axes[0, 0].set_title("Glucose Distribution by Outcome", fontweight="bold")
    
    sns.histplot(data=df_clean, x='BMI', hue='Outcome', kde=True, ax=axes[0, 1], palette="Set2")
    axes[0, 1].set_title("BMI Distribution by Outcome", fontweight="bold")

    sns.histplot(data=df_clean, x='Age', hue='Outcome', kde=True, ax=axes[1, 0], palette="Set2")
    axes[1, 0].set_title("Age Distribution by Outcome", fontweight="bold")

    sns.boxplot(data=df_clean, x='Outcome', y='DiabetesPedigreeFunction', ax=axes[1, 1], palette="Set2")
    axes[1, 1].set_title("Diabetes Pedigree Function by Outcome", fontweight="bold")
    
    plt.tight_layout()
    plt.savefig("static/eda_plots/risk_distribution.png", dpi=300)
    plt.close()

    return df_clean

def train_and_evaluate_models(df):
    print("\n--- Training & Comparing Classification Models ---")
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    joblib.dump(scaler, "models/scaler.joblib")
    print("StandardScaler saved to models/scaler.joblib")

    models = {
        "Logistic Regression": LogisticRegression(random_state=42, max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, max_depth=6),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "XGBoost": xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42, n_estimators=100, max_depth=4),
        "Support Vector Machine": SVC(probability=True, random_state=42)
    }

    results = {}
    best_score = 0
    best_model_name = None
    best_model_obj = None

    for name, model in models.items():
        if name in ["Logistic Regression", "Support Vector Machine"]:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_proba)
        cm = confusion_matrix(y_test, y_pred).tolist()

        cv_scores = cross_val_score(
            model, X_train_scaled if name in ["Logistic Regression", "Support Vector Machine"] else X_train,
            y_train, cv=5, scoring='accuracy'
        )

        results[name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "cv_accuracy_mean": round(cv_scores.mean(), 4),
            "cv_accuracy_std": round(cv_scores.std(), 4),
            "confusion_matrix": cm
        }

        print(f"[{name}] Acc: {acc:.4f} | F1: {f1:.4f} | ROC-AUC: {auc:.4f} | CV Mean: {cv_scores.mean():.4f}")

        if auc > best_score:
            best_score = auc
            best_model_name = name
            best_model_obj = model

    print(f"\n---> Selected Best Model: {best_model_name} (ROC-AUC: {best_score:.4f})")
    joblib.dump(best_model_obj, "models/diabetes_model.joblib")
    print("Saved best model to models/diabetes_model.joblib")

    with open("models/model_comparison.json", "w") as f:
        json.dump(results, f, indent=2)

    # Plot Model Comparison Bar Chart
    plt.figure(figsize=(10, 6))
    model_names = list(results.keys())
    accuracies = [results[m]["accuracy"] for m in model_names]
    f1_scores = [results[m]["f1_score"] for m in model_names]
    rocs = [results[m]["roc_auc"] for m in model_names]

    x = np.arange(len(model_names))
    width = 0.25

    plt.bar(x - width, accuracies, width, label='Accuracy', color='#3b82f6')
    plt.bar(x, f1_scores, width, label='F1-Score', color='#10b981')
    plt.bar(x + width, rocs, width, label='ROC-AUC', color='#8b5cf6')

    plt.xlabel('Classification Models', fontweight='bold')
    plt.ylabel('Score (0.0 to 1.0)', fontweight='bold')
    plt.title('Algorithm Performance Comparison', fontsize=14, fontweight='bold', pad=15)
    plt.xticks(x, model_names, rotation=15)
    plt.ylim(0.5, 1.0)
    plt.legend(loc='lower right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig("static/eda_plots/model_comparison.png", dpi=300)
    plt.close()

    # Feature Importance Plot (for Random Forest or XGBoost)
    rf_model = models["Random Forest"]
    importances = rf_model.feature_importances_
    features = X.columns
    indices = np.argsort(importances)[::-1]

    plt.figure(figsize=(9, 5))
    plt.title("Feature Importance Analysis (Random Forest)", fontsize=14, fontweight='bold', pad=15)
    sns.barplot(x=importances[indices], y=features[indices], palette="viridis")
    plt.xlabel("Relative Importance Score", fontweight='bold')
    plt.tight_layout()
    plt.savefig("static/eda_plots/feature_importance.png", dpi=300)
    plt.close()

    print("Generated all EDA & Model comparison plots successfully!")

if __name__ == "__main__":
    df = generate_or_load_dataset()
    df_clean = preprocess_and_eda(df)
    train_and_evaluate_models(df_clean)
