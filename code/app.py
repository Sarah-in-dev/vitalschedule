from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import joblib
import json

app = Flask(__name__, template_folder='../visualization/templates',
           static_folder='../visualization/static')

# Load model (will update this when model is trained)
model = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    # Convert JSON to DataFrame
    df = pd.DataFrame([data])
    
    # Make prediction
    risk_score = 0.75  # Placeholder until model is loaded
    
    # Return prediction
    return jsonify({
        'risk_score': risk_score,
        'risk_factors': [
            {'factor': 'Previous no-shows', 'importance': 0.3},
            {'factor': 'Appointment lead time', 'importance': 0.2},
            {'factor': 'Weather forecast', 'importance': 0.1}
        ],
        'recommended_interventions': [
            {'intervention': 'Personal phone call', 'effectiveness': 0.8},
            {'intervention': 'Transportation assistance', 'effectiveness': 0.6}
        ]
    })

@app.route('/dashboard')
def dashboard():
    # Placeholder for dashboard data
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
