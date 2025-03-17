# code/readmission/model_training.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def prepare_modeling_data(features_df, test_size=0.2, random_state=42):
    """
    Prepare data for modeling by splitting into train and test sets
    
    Parameters:
    -----------
    features_df : pandas.DataFrame
        Dataset with features for modeling
    test_size : float
        Proportion of data to use for testing
    random_state : int
        Random seed for reproducibility
        
    Returns:
    --------
    tuple
        X_train, X_test, y_train, y_test, num_features, cat_features
    """
    print("Preparing data for modeling...")
    
    # Identify the target
    if 'is_readmission' not in features_df.columns:
        raise ValueError("Target variable 'is_readmission' not found in dataset")
    
    # Split features and target
    X = features_df.drop(columns=['is_readmission'])
    y = features_df['is_readmission']
    
    # Identify numeric and categorical features
    num_features = []
    cat_features = []
    
    for col in X.columns:
        # Skip ID columns and target-related columns
        if col in ['subject_id', 'hadm_id', 'stay_id', 'days_to_readmission']:
            continue
        
        # Check data type
        if X[col].dtype in ['int64', 'float64']:
            num_features.append(col)
        else:
            cat_features.append(col)
    
    print(f"Identified {len(num_features)} numerical features and {len(cat_features)} categorical features")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    return X_train, X_test, y_train, y_test, num_features, cat_features

def create_preprocessing_pipeline(num_features, cat_features):
    """
    Create a preprocessing pipeline for numerical and categorical features
    
    Parameters:
    -----------
    num_features : list
        List of numerical feature names
    cat_features : list
        List of categorical feature names
        
    Returns:
    --------
    sklearn.compose.ColumnTransformer
        Preprocessing pipeline
    """
    # Numerical features pipeline
    num_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', RobustScaler())
    ])
    
    # Categorical features pipeline
    cat_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    # Combine preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, num_features),
            ('cat', cat_transformer, cat_features)
        ],
        remainder='drop'  # Drop any columns not specified
    )
    
    return preprocessor

def train_models(X_train, X_test, y_train, y_test, num_features, cat_features, output_dir=None):
    """
    Train multiple models and evaluate their performance
    
    Parameters:
    -----------
    X_train, X_test : pandas.DataFrame
        Training and test features
    y_train, y_test : pandas.Series
        Training and test target
    num_features, cat_features : list
        Lists of numerical and categorical feature names
    output_dir : str, optional
        Directory to save models and results
        
    Returns:
    --------
    dict
        Dictionary with trained models and their performance
    """
    print("Training models...")
    
    # Create timestamp for this run
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create output directory if specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        run_dir = os.path.join(output_dir, f"run_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)
    else:
        run_dir = None
    
    # Create preprocessing pipeline
    preprocessor = create_preprocessing_pipeline(num_features, cat_features)
    
    # Initialize models
    models = {
        'logistic_regression': {
            'model': LogisticRegression(max_iter=1000, random_state=42),
            'params': {
                'classifier__C': [0.1, 1.0, 10.0],
                'classifier__penalty': ['l2'],
                'classifier__class_weight': [None, 'balanced']
            }
        },
        'random_forest': {
            'model': RandomForestClassifier(random_state=42),
            'params': {
                'classifier__n_estimators': [100, 200],
                'classifier__max_depth': [None, 10, 20],
                'classifier__min_samples_split': [2, 5, 10],
                'classifier__class_weight': [None, 'balanced']
            }
        },
        'gradient_boosting': {
            'model': GradientBoostingClassifier(random_state=42),
            'params': {
                'classifier__n_estimators': [100, 200],
                'classifier__learning_rate': [0.01, 0.1],
                'classifier__max_depth': [3, 5]
            }
        },
        'xgboost': {
            'model': xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
            'params': {
                'classifier__n_estimators': [100, 200],
                'classifier__learning_rate': [0.01, 0.1],
                'classifier__max_depth': [3, 5],
                'classifier__min_child_weight': [1, 5]
            }
        }
    }
    
    # Train and evaluate each model
    results = {}
    
    for model_name, model_info in models.items():
        print(f"\nTraining {model_name}...")
        
        # Create pipeline with preprocessing and model
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model_info['model'])
        ])
        
        # Train the model
        pipeline.fit(X_train, y_train)
        
        # Predict on test set
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        evaluation = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1': f1_score(y_test, y_pred),
            'auc': roc_auc_score(y_test, y_prob)
        }
        
        print(f"{model_name} performance:")
        for metric, value in evaluation.items():
            print(f"  {metric}: {value:.4f}")
        
        # Store the model and evaluation
        results[model_name] = {
            'pipeline': pipeline,
            'evaluation': evaluation,
            'y_pred': y_pred,
            'y_prob': y_prob
        }
        
        # Save the model if output directory is specified
        if run_dir:
            model_path = os.path.join(run_dir, f"{model_name}.joblib")
            joblib.dump(pipeline, model_path)
            print(f"Model saved to {model_path}")
    
    # Optionally perform hyperparameter tuning on the best model
    best_model = max(results.items(), key=lambda x: x[1]['evaluation']['auc'])
    print(f"\nBest model: {best_model[0]} (AUC: {best_model[1]['evaluation']['auc']:.4f})")
    
    # Save comparison results
    if run_dir:
        comparison_df = pd.DataFrame({
            model_name: result['evaluation'] for model_name, result in results.items()
        }).T
        
        comparison_path = os.path.join(run_dir, "model_comparison.csv")
        comparison_df.to_csv(comparison_path)
        print(f"Model comparison saved to {comparison_path}")
        
        # Create a visualization of model performance
        plt.figure(figsize=(10, 6))
        comparison_df[['accuracy', 'precision', 'recall', 'f1', 'auc']].plot(kind='bar')
        plt.title('Model Performance Comparison')
        plt.ylabel('Score')
        plt.xlabel('Model')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(run_dir, "model_comparison.png"))
        plt.close()
    
    return results

def tune_best_model(X_train, X_test, y_train, y_test, num_features, cat_features, model_name, model_info, output_dir=None):
    """
    Perform hyperparameter tuning on a model
    
    Parameters:
    -----------
    X_train, X_test : pandas.DataFrame
        Training and test features
    y_train, y_test : pandas.Series
        Training and test target
    num_features, cat_features : list
        Lists of numerical and categorical feature names
    model_name : str
        Name of the model to tune
    model_info : dict
        Dictionary with model and parameters
    output_dir : str, optional
        Directory to save tuned model
        
    Returns:
    --------
    dict
        Dictionary with tuned model and performance
    """
    print(f"\nTuning {model_name}...")
    
    # Create preprocessing pipeline
    preprocessor = create_preprocessing_pipeline(num_features, cat_features)
    
    # Create pipeline
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model_info['model'])
    ])
    
    # Create cross-validation strategy
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # Create grid search
    grid_search = GridSearchCV(
        pipeline,
        param_grid=model_info['params'],
        cv=cv,
        scoring='roc_auc',
        n_jobs=-1,
        verbose=1
    )
    
    # Perform grid search
    grid_search.fit(X_train, y_train)
    
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    
    # Evaluate on test set
    best_model = grid_search.best_estimator_
    y_pred = best_model.predict(X_test)
    y_prob = best_model.predict_proba(X_test)[:, 1]
    
    # Calculate metrics
    evaluation = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'auc': roc_auc_score(y_test, y_prob)
    }
    
    print(f"Test set performance:")
    for metric, value in evaluation.items():
        print(f"  {metric}: {value:.4f}")
    
    # Save the model if output directory is specified
    if output_dir:
        model_path = os.path.join(output_dir, f"{model_name}_tuned.joblib")
        joblib.dump(best_model, model_path)
        print(f"Tuned model saved to {model_path}")
    
    return {
        'pipeline': best_model,
        'evaluation': evaluation,
        'y_pred': y_pred,
        'y_prob': y_prob,
        'best_params': grid_search.best_params_,
        'cv_results': grid_search.cv_results_
    }

def extract_feature_importance(model, num_features, cat_features, output_dir=None):
    """
    Extract feature importance from a trained model
    
    Parameters:
    -----------
    model : sklearn.pipeline.Pipeline
        Trained model pipeline
    num_features : list
        List of numerical feature names
    cat_features : list
        List of categorical feature names
    output_dir : str, optional
        Directory to save feature importance
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame with feature importance
    """
    print("Extracting feature importance...")
    
    # Get the model from the pipeline
    if hasattr(model, 'named_steps'):
        if 'classifier' in model.named_steps:
            clf = model.named_steps['classifier']
        else:
            print("Model pipeline does not have a 'classifier' step")
            return None
    else:
        clf = model  # Model is not a pipeline
    
    # Check if the model has feature_importances_ attribute
    if hasattr(clf, 'feature_importances_'):
        importance = clf.feature_importances_
    elif hasattr(clf, 'coef_'):
        importance = clf.coef_[0]  # For linear models
    else:
        print("Model does not have feature importance information")
        return None
    
    # Get feature names after preprocessing
    preprocessor = model.named_steps['preprocessor']
    
    # Get feature names from preprocessor
    feature_names = []
    
    # Handle numerical features
    if len(num_features) > 0:
        feature_names.extend(num_features)
    
    # Handle categorical features (one-hot encoded)
    if len(cat_features) > 0:
        cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
        if hasattr(cat_encoder, 'get_feature_names_out'):
            cat_feature_names = cat_encoder.get_feature_names_out(cat_features)
            feature_names.extend(cat_feature_names)
        else:
            # For older scikit-learn versions
            for cat in cat_features:
                values = X_train[cat].dropna().unique()
                for val in values:
                    feature_names.append(f"{cat}_{val}")
    
    # Adjust size of feature_names if needed
    if len(feature_names) > len(importance):
        feature_names = feature_names[:len(importance)]
    elif len(feature_names) < len(importance):
        # Pad with generic names if needed
        feature_names.extend([f"Feature_{i}" for i in range(len(feature_names), len(importance))])
    
    # Create feature importance DataFrame
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    })
    
    # Sort by importance
    importance_df = importance_df.sort_values('importance', ascending=False)
    
    # Save feature importance if output directory is specified
    if output_dir:
        importance_path = os.path.join(output_dir, "feature_importance.csv")
        importance_df.to_csv(importance_path, index=False)
        print(f"Feature importance saved to {importance_path}")
        
        # Create visualization
        plt.figure(figsize=(12, 8))
        sns.barplot(x='importance', y='feature', data=importance_df.head(20))
        plt.title('Top 20 Feature Importance')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "feature_importance.png"))
        plt.close()
    
    return importance_df

if __name__ == "__main__":
    # Example usage
    data_dir = os.path.join(os.getcwd(), 'data', 'processed', 'readmission')
    output_dir = os.path.join(os.getcwd(), 'models', 'readmission')
    
    # Load features
    features_path = os.path.join(data_dir, 'readmission_features.csv')
    if os.path.exists(features_path):
        features_df = pd.read_csv(features_path)
        
        # Prepare data
        X_train, X_test, y_train, y_test, num_features, cat_features = prepare_modeling_data(features_df)
        
        # Train models
        results = train_models(X_train, X_test, y_train, y_test, num_features, cat_features, output_dir)
        
        # Get the best model
        best_model_name = max(results.items(), key=lambda x: x[1]['evaluation']['auc'])[0]
        print(f"\nTuning best model: {best_model_name}")
        
        # Tune the best model
        best_model_info = models[best_model_name]
        tuned_results = tune_best_model(X_train, X_test, y_train, y_test, num_features, cat_features, 
                                       best_model_name, best_model_info, output_dir)
        
        # Extract feature importance
        extract_feature_importance(tuned_results['pipeline'], num_features, cat_features, output_dir)
    else:
        print(f"Features not found at {features_path}")
