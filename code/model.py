import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
import xgboost as xgb
import joblib

class NoShowPredictor:
    def __init__(self):
        self.pipeline = None
        self.feature_importances = None
        self.categorical_features = []
        self.numerical_features = []
        
    def build_pipeline(self):
        """Build preprocessing and model pipeline"""
        numeric_transformer = Pipeline(steps=[
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, self.numerical_features),
                ('cat', categorical_transformer, self.categorical_features)
            ])
        
        self.pipeline = Pipeline(steps=[
            ('preprocessor', preprocessor),
            ('model', xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss'))
        ])
        
        return self
    
    def train(self, X, y):
        """Train the model pipeline"""
        self.pipeline.fit(X, y)
        # Extract feature importances
        model = self.pipeline.named_steps['model']
        self.feature_importances = model.feature_importances_
        return self
    
    def predict(self, X):
        """Generate predictions"""
        return self.pipeline.predict(X)
    
    def predict_proba(self, X):
        """Generate probability predictions"""
        return self.pipeline.predict_proba(X)
    
    def save(self, filepath):
        """Save model to disk"""
        joblib.dump(self.pipeline, filepath)
        return self
    
    def load(self, filepath):
        """Load model from disk"""
        self.pipeline = joblib.load(filepath)
        return self
