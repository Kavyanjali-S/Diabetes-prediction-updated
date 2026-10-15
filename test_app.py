import unittest
from fastapi.testclient import TestClient
import os
import io

from app import app
import database

class TestDiabetesSystem(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_01_serve_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("DiabetesAI Predictor", response.text)

    def test_02_predict_high_risk(self):
        payload = {
            "patient_name": "Test High Risk",
            "pregnancies": 5,
            "glucose": 180.0,
            "blood_pressure": 90.0,
            "skin_thickness": 35.0,
            "insulin": 220.0,
            "bmi": 38.5,
            "dpf": 0.85,
            "age": 52
        }
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("probability", data)
        self.assertIn("risk_level", data)
        self.assertIn("recommendations", data)
        self.assertEqual(data["patient_name"], "Test High Risk")

    def test_03_predict_low_risk(self):
        payload = {
            "patient_name": "Test Low Risk",
            "pregnancies": 0,
            "glucose": 85.0,
            "blood_pressure": 65.0,
            "skin_thickness": 15.0,
            "insulin": 45.0,
            "bmi": 21.0,
            "dpf": 0.15,
            "age": 24
        }
        response = self.client.post("/api/predict", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("probability", data)
        self.assertEqual(data["risk_level"], "Low Risk")

    def test_04_dashboard_api(self):
        response = self.client.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("stats", data)

    def test_05_history_api(self):
        response = self.client.get("/api/history")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertGreater(len(data["data"]), 0)

    def test_06_model_comparison_api(self):
        response = self.client.get("/api/model-comparison")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("Logistic Regression", data["comparison"])

    def test_07_batch_predict_csv(self):
        csv_content = (
            "Name,Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age\n"
            "Batch Patient 1,1,130,70,20,80,26.5,0.4,35\n"
            "Batch Patient 2,4,175,85,30,190,34.0,0.7,50\n"
        )
        files = {"file": ("test_batch.csv", io.BytesIO(csv_content.encode('utf-8')), "text/csv")}
        response = self.client.post("/api/batch-predict", files=files)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["total_processed"], 2)

if __name__ == "__main__":
    unittest.main()
