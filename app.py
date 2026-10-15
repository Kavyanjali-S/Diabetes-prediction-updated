import os
import json
import io
import pandas as pd
import numpy as np
from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import joblib

import database

# Initialize database
database.init_db()

app = FastAPI(
    title="AI Diabetes Risk Prediction System",
    description="Machine Learning Powered Early Diabetes Risk Assessment & Analytics Engine",
    version="1.0.0"
)

# Mount Static & Templates
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Load ML Model and Scaler
MODEL_PATH = "models/diabetes_model.joblib"
SCALER_PATH = "models/scaler.joblib"
COMPARISON_PATH = "models/model_comparison.json"

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("ML Model and Scaler loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load ML artifacts: {e}")
    model = None
    scaler = None

class PatientMetrics(BaseModel):
    patient_name: str = Field(default="Anonymous Patient", description="Name of the patient")
    pregnancies: int = Field(ge=0, le=20, default=1, description="Number of times pregnant")
    glucose: float = Field(ge=0.0, le=300.0, default=120.0, description="Plasma glucose concentration 2h after oral glucose test")
    blood_pressure: float = Field(ge=0.0, le=200.0, default=70.0, description="Diastolic blood pressure (mm Hg)")
    skin_thickness: float = Field(ge=0.0, le=100.0, default=20.0, description="Triceps skin fold thickness (mm)")
    insulin: float = Field(ge=0.0, le=900.0, default=79.0, description="2-Hour serum insulin (mu U/ml)")
    bmi: float = Field(ge=0.0, le=70.0, default=28.5, description="Body mass index (weight in kg/(height in m)^2)")
    dpf: float = Field(ge=0.0, le=3.0, default=0.47, description="Diabetes pedigree function (genetic score)")
    age: int = Field(ge=1, le=120, default=33, description="Age in years")
    selected_model: str = Field(default="Best Model", description="Model selected for inference")

def generate_health_recommendations(data, prob, risk_level):
    recommendations = []
    risk_factors = []

    if data['glucose'] >= 140:
        risk_factors.append("High Plasma Glucose (> 140 mg/dL)")
        recommendations.append("Schedule a Fasting Blood Sugar and HbA1c test with your healthcare provider.")
    elif data['glucose'] >= 100:
        risk_factors.append("Elevated Fasting Glucose (Pre-diabetes range)")
        recommendations.append("Reduce refined sugars and high-glycemic carbohydrates in daily diet.")

    if data['bmi'] >= 30:
        risk_factors.append("Obesity (BMI ≥ 30)")
        recommendations.append("Aim for 150 minutes of moderate aerobic exercise per week to achieve a healthy weight.")
    elif data['bmi'] >= 25:
        risk_factors.append("Overweight (BMI 25 - 29.9)")
        recommendations.append("Incorporate daily 30-minute brisk walks and calorie balance.")

    if data['blood_pressure'] >= 90:
        risk_factors.append("Stage 2 Hypertension (Diastolic ≥ 90 mm Hg)")
        recommendations.append("Monitor blood pressure regularly and consult a cardiologist.")
    elif data['blood_pressure'] >= 80:
        risk_factors.append("Prehypertension (Diastolic 80-89 mm Hg)")
        recommendations.append("Adopt a low-sodium DASH diet.")

    if data['dpf'] > 0.5:
        risk_factors.append("Strong Genetic/Family Predisposition")
        recommendations.append("Perform annual diabetes screening due to strong family history factor.")

    if data['age'] >= 45:
        risk_factors.append("Age Group (≥ 45 years)")

    if not recommendations:
        recommendations.append("Maintain your current healthy lifestyle, balanced diet, and active routine.")

    return risk_factors, recommendations

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/predict")
async def predict_diabetes_risk(metrics: PatientMetrics):
    if model is None or scaler is None:
        raise HTTPException(status_code=500, detail="Machine Learning model is not loaded.")

    feature_names = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    input_df = pd.DataFrame([[
        metrics.pregnancies,
        metrics.glucose,
        metrics.blood_pressure,
        metrics.skin_thickness,
        metrics.insulin,
        metrics.bmi,
        metrics.dpf,
        metrics.age
    ]], columns=feature_names)

    # Scaling input features
    input_scaled = scaler.transform(input_df)

    # Predict class & probability
    prediction_class = int(model.predict(input_scaled)[0])
    probabilities = model.predict_proba(input_scaled)[0]
    prob_positive = float(probabilities[1])

    # Categorize Risk
    if prob_positive < 0.35:
        risk_level = "Low Risk"
    elif prob_positive < 0.65:
        risk_level = "Moderate Risk"
    else:
        risk_level = "High Risk"

    risk_factors, recommendations = generate_health_recommendations(metrics.model_dump(), prob_positive, risk_level)

    # Record to DB
    record_data = metrics.model_dump()
    record_data['prediction'] = prediction_class
    record_data['probability'] = round(prob_positive, 4)
    record_data['risk_level'] = risk_level
    record_data['model_used'] = type(model).__name__

    inserted_id = database.save_prediction(record_data)

    return {
        "id": inserted_id,
        "patient_name": metrics.patient_name,
        "prediction": prediction_class,
        "probability": round(prob_positive * 100, 1),
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        "model_used": type(model).__name__
    }

@app.get("/api/history")
async def get_history():
    records = database.get_all_predictions()
    return {"status": "success", "count": len(records), "data": records}

@app.delete("/api/history/all")
async def clear_all_records():
    database.clear_all_predictions()
    return {"status": "success", "message": "All prediction records have been cleared."}

@app.delete("/api/history/{record_id}")
async def delete_record(record_id: int):
    success = database.delete_prediction(record_id)
    if success:
        return {"status": "success", "message": f"Record #{record_id} deleted."}
    raise HTTPException(status_code=404, detail="Record not found.")

@app.get("/api/dashboard")
async def get_dashboard():
    stats = database.get_dashboard_summary()
    return {"status": "success", "stats": stats}

@app.get("/api/model-comparison")
async def get_model_comparison():
    if os.path.exists(COMPARISON_PATH):
        with open(COMPARISON_PATH, "r") as f:
            data = json.load(f)
        return {"status": "success", "comparison": data}
    raise HTTPException(status_code=404, detail="Comparison file not found.")

@app.post("/api/batch-predict")
async def batch_predict(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a valid CSV file.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV file: {str(e)}")

    required_cols = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns in CSV: {missing}")

    X_batch = df[required_cols]
    X_batch_scaled = scaler.transform(X_batch)

    preds = model.predict(X_batch_scaled)
    probas = model.predict_proba(X_batch_scaled)[:, 1]

    results = []
    for idx, row in df.iterrows():
        prob = float(probas[idx])
        if prob < 0.35:
            risk = "Low Risk"
        elif prob < 0.65:
            risk = "Moderate Risk"
        else:
            risk = "High Risk"

        # Store probability as decimal (0-1) in DB — consistent with single predictions
        db_record = {
            "patient_name": row.get("Name", f"Batch Patient #{idx+1}"),
            "pregnancies": int(row['Pregnancies']),
            "glucose": float(row['Glucose']),
            "blood_pressure": float(row['BloodPressure']),
            "skin_thickness": float(row['SkinThickness']),
            "insulin": float(row['Insulin']),
            "bmi": float(row['BMI']),
            "dpf": float(row['DiabetesPedigreeFunction']),
            "age": int(row['Age']),
            "prediction": int(preds[idx]),
            "probability": round(prob, 4),   # decimal for DB storage
            "risk_level": risk,
            "model_used": type(model).__name__
        }
        database.save_prediction(db_record)

        # Expose percentage in the API response for convenience
        results.append({**db_record, "probability": round(prob * 100, 1)})

    return {
        "status": "success",
        "total_processed": len(results),
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
