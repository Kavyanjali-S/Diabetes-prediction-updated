import sqlite3
import os
from datetime import datetime

# On Render, the persistent disk is mounted at /data
# Locally it falls back to data/predictions.db
DATA_DIR = os.environ.get("DATA_DIR", "data")
DB_PATH = os.path.join(DATA_DIR, "predictions.db")

def get_db_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            patient_name TEXT DEFAULT 'Anonymous Patient',
            pregnancies INTEGER,
            glucose REAL,
            blood_pressure REAL,
            skin_thickness REAL,
            insulin REAL,
            bmi REAL,
            dpf REAL,
            age INTEGER,
            prediction INTEGER,
            probability REAL,
            risk_level TEXT,
            model_used TEXT
        )
    """)

    # Check if empty, populate with a few realistic initial sample records for immediate rich dashboard demo
    cursor.execute("SELECT COUNT(*) FROM predictions")
    count = cursor.fetchone()[0]
    if count == 0:
        sample_records = [
            ('John Doe', 2, 145.0, 78.0, 25.0, 120.0, 32.5, 0.45, 45, 1, 0.825, 'High Risk', 'Random Forest'),
            ('Jane Smith', 0, 95.0, 68.0, 18.0, 50.0, 22.1, 0.18, 28, 0, 0.120, 'Low Risk', 'Random Forest'),
            ('Robert Johnson', 5, 178.0, 88.0, 35.0, 210.0, 39.4, 0.85, 54, 1, 0.942, 'High Risk', 'XGBoost'),
            ('Emily Davis', 1, 110.0, 72.0, 20.0, 75.0, 24.8, 0.25, 33, 0, 0.215, 'Low Risk', 'Random Forest'),
            ('Michael Brown', 3, 132.0, 82.0, 28.0, 140.0, 31.0, 0.52, 48, 1, 0.610, 'Moderate Risk', 'Logistic Regression')
        ]
        cursor.executemany("""
            INSERT INTO predictions (
                patient_name, pregnancies, glucose, blood_pressure, skin_thickness,
                insulin, bmi, dpf, age, prediction, probability, risk_level, model_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_records)

    conn.commit()
    conn.close()

def save_prediction(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    patient_name = data.get('patient_name', 'Anonymous Patient') or 'Anonymous Patient'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO predictions (
            timestamp, patient_name, pregnancies, glucose, blood_pressure, skin_thickness,
            insulin, bmi, dpf, age, prediction, probability, risk_level, model_used
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        timestamp,
        patient_name,
        int(data['pregnancies']),
        float(data['glucose']),
        float(data['blood_pressure']),
        float(data['skin_thickness']),
        float(data['insulin']),
        float(data['bmi']),
        float(data['dpf']),
        int(data['age']),
        int(data['prediction']),
        float(data['probability']),
        data['risk_level'],
        data.get('model_used', 'Random Forest')
    ))

    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def get_all_predictions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_all_predictions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions")
    conn.commit()
    conn.close()

def delete_prediction(pred_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE id = ?", (pred_id,))
    conn.commit()
    conn.close()
    return True

def get_dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction = 1")
    high_risk_count = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(glucose), AVG(bmi), AVG(age) FROM predictions")
    avg_stats = cursor.fetchone()
    avg_glucose = round(avg_stats[0], 1) if avg_stats[0] else 0.0
    avg_bmi = round(avg_stats[1], 1) if avg_stats[1] else 0.0
    avg_age = round(avg_stats[2], 1) if avg_stats[2] else 0.0

    # Risk level distribution breakdown
    cursor.execute("SELECT risk_level, COUNT(*) FROM predictions GROUP BY risk_level")
    risk_counts = dict(cursor.fetchall())

    conn.close()

    return {
        "total_predictions": total_count,
        "high_risk_count": high_risk_count,
        "low_risk_count": total_count - high_risk_count,
        "high_risk_percentage": round((high_risk_count / total_count * 100), 1) if total_count > 0 else 0,
        "avg_glucose": avg_glucose,
        "avg_bmi": avg_bmi,
        "avg_age": avg_age,
        "risk_breakdown": risk_counts
    }
