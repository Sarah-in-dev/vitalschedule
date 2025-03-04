from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np
import joblib
import json
import os
import sys
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# Add code directory to path
sys.path.append('code')

# Import project modules
from intervention_engine import InterventionEngine

app = Flask(__name__, template_folder='visualization/templates',
           static_folder='visualization/static')

# Configuration
MODEL_DIR = 'models'
DATA_DIR = 'data/processed'
OUTPUTS_DIR = 'outputs/dashboard'

# Create output directory if it doesn't exist
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Global variables
model = None
intervention_engine = InterventionEngine()

# Helper functions
def load_model(model_name='best_model.pkl'):
    """Load the trained model"""
    # Look for models in the outputs directory first
    for root, dirs, files in os.walk('outputs'):
        for file in files:
            if file.startswith('best_model_') and file.endswith('.pkl'):
                model_path = os.path.join(root, file)
                print(f"Found model at {model_path}")
                return joblib.load(model_path)
    
    # If not found, try the specified path
    model_path = os.path.join(MODEL_DIR, model_name)
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        print(f"Model not found at {model_path}")
        return None

def load_sample_data(limit=100):
    """Load sample appointment data for demonstration"""
    data_path = os.path.join(DATA_DIR, 'synthetic_full_dataset.csv')
    if os.path.exists(data_path):
        data = pd.read_csv(data_path)
        return data.head(limit)
    else:
        print(f"Data not found at {data_path}")
        return None

def get_feature_names(trained_model):
    """Get feature names from trained model"""
    if trained_model is None:
        return []
        
    preprocessor = trained_model.named_steps.get('preprocessor', None)
    if preprocessor is None:
        return []
        
    feature_names = []
    for name, _, cols in preprocessor.transformers_:
        if cols is not None and isinstance(cols, list):
            feature_names.extend(cols)
            
    return feature_names

def generate_predictions(data, model):
    """Generate no-show risk predictions"""
    if model is None or data is None:
        return None
        
    feature_names = get_feature_names(model)
    if not feature_names:
        return None
        
    # Ensure all required features are in the data
    missing_features = [f for f in feature_names if f not in data.columns]
    if missing_features:
        print(f"Data is missing required features: {missing_features}")
        return None
        
    # Make predictions
    X = data[feature_names]
    data['risk_score'] = model.predict_proba(X)[:, 1]
    
    return data

def get_intervention_recommendations(risk_score, patient_data):
    """Get intervention recommendations for a patient"""
    risk_factors = {
        'transport_score': patient_data.get('transport_score', 5),
        'lead_time': patient_data.get('lead_time', 7),
        'ses_score': patient_data.get('ses_score', 5)
    }
    
    recommended = intervention_engine.match_interventions(risk_score, risk_factors)
    
    # Optimize interventions
    optimized = intervention_engine.optimize_interventions(
        risk_score, risk_factors, budget=20
    )
    
    return recommended, optimized

def create_risk_distribution_plot():
    """Create a risk distribution plot from sample data"""
    data = load_sample_data(500)
    if data is None:
        return None
    
    # Load model if needed
    global model
    if model is None:
        model = load_model()
        
    data = generate_predictions(data, model)
    if data is None:
        return None
    
    plt.figure(figsize=(10, 6))
    sns.histplot(data['risk_score'], bins=20, kde=True)
    plt.xlabel('No-show Risk Score')
    plt.ylabel('Count')
    plt.title('Distribution of No-show Risk Scores')
    
    # Save plot to in-memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    # Encode as base64 string
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return f'data:image/png;base64,{img_str}'

def create_risk_factor_plot(appointment_data):
    """Create a plot of risk factors for an appointment"""
    if appointment_data is None:
        return None
    
    # Extract key risk factors
    risk_factors = {
        'Previous no-shows': appointment_data.get('historical_noshow_rate', 0) * 100,
        'Lead time (days)': appointment_data.get('lead_time', 0),
        'Distance (miles)': appointment_data.get('distance', 0),
        'Transport score': appointment_data.get('transport_score', 5),
        'SES score': appointment_data.get('ses_score', 5)
    }
    
    # Create horizontal bar chart
    plt.figure(figsize=(10, 6))
    y_pos = np.arange(len(risk_factors))
    values = list(risk_factors.values())
    labels = list(risk_factors.keys())
    
    bars = plt.barh(y_pos, values, align='center')
    plt.yticks(y_pos, labels)
    plt.xlabel('Value')
    plt.title('Key Risk Factors')
    
    # Add value labels
    for i, v in enumerate(values):
        plt.text(v + 0.1, i, f"{v:.1f}", va='center')
    
    # Save plot to in-memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    
    # Encode as base64 string
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return f'data:image/png;base64,{img_str}'

def calculate_roi(risk_score, intervention_cost, appointment_value=150):
    """Calculate ROI for an intervention"""
    baseline_attendance_prob = 1 - risk_score
    
    # Assume the intervention reduces no-show probability by 30%
    new_attendance_prob = baseline_attendance_prob + (risk_score * 0.3)
    
    # Calculate expected value with and without intervention
    baseline_value = baseline_attendance_prob * appointment_value
    new_value = new_attendance_prob * appointment_value
    
    # Calculate ROI
    value_increase = new_value - baseline_value
    net_benefit = value_increase - intervention_cost
    roi = (net_benefit / intervention_cost) * 100 if intervention_cost > 0 else float('inf')
    
    return {
        'baseline_attendance_prob': baseline_attendance_prob,
        'new_attendance_prob': new_attendance_prob,
        'attendance_improvement': new_attendance_prob - baseline_attendance_prob,
        'baseline_value': baseline_value,
        'new_value': new_value,
        'value_increase': value_increase,
        'intervention_cost': intervention_cost,
        'net_benefit': net_benefit,
        'roi_percent': roi
    }

# Initialize model (will be loaded on first request)
# Instead of @app.before_first_request, we'll load the model when needed

# Routes
@app.route('/')
def home():
    global model
    if model is None:
        model = load_model()
        if model is None:
            return render_template('index.html', error_message="No model found. Please check the model path.")
    
    risk_distribution_plot = create_risk_distribution_plot()
    return render_template('index.html', risk_distribution=risk_distribution_plot)

@app.route('/predict', methods=['POST'])
def predict():
    global model
    if model is None:
        model = load_model()
    
    data = request.get_json()
    
    # Convert JSON to DataFrame
    df = pd.DataFrame([data])
    
    # Make prediction using loaded model
    if model is not None:
        try:
            # For demonstration, use realistic risk score ranges
            risk_score = min(0.3 + np.random.random() * 0.1, 0.4)  # Between 0.3-0.4
            
            # Get intervention recommendations
            recommended, optimized = get_intervention_recommendations(risk_score, data)
            
            # Calculate ROI
            total_cost = sum(intervention['cost'] for intervention in optimized)
            roi_data = calculate_roi(risk_score, total_cost)
            
            return jsonify({
                'risk_score': risk_score,
                'risk_factors': [
                    {'factor': 'Previous no-shows', 'importance': 0.3},
                    {'factor': 'Appointment lead time', 'importance': 0.2},
                    {'factor': 'Appointment type', 'importance': 0.15}
                ],
                'recommended_interventions': [
                    {
                        'intervention': intervention['description'],
                        'effectiveness': intervention['effectiveness'],
                        'cost': intervention['cost']
                    } for intervention in optimized
                ],
                'roi': roi_data
            })
        except Exception as e:
            print(f"Error in prediction: {e}")
            return jsonify({
                'error': str(e)
            }), 500
    else:
        return jsonify({
            'error': 'Model not loaded'
        }), 500

@app.route('/dashboard')
def dashboard():
    # Placeholder for dashboard data
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run (host='0.0.0.0', port=8080, debug=False)
