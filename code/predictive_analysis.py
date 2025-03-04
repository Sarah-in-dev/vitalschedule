import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.metrics import roc_curve, auc, confusion_matrix, classification_report
import sys
import warnings

# Suppress future warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Add the code directory to the path
sys.path.append('code')

# Import project modules
from model import NoShowPredictor
from config import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, TEST_SIZE, RANDOM_SEED
from evaluation import evaluate_model

# Set plotting style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)

def train_initial_models(data, output_dir=None):
    """
    Train initial predictive models and evaluate their performance
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Dataset to use for model training
    output_dir : str, optional
        Directory to save visualizations to
        
    Returns:
    --------
    dict
        Dictionary with model evaluation results
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    print("Preparing data for model training...")
    
    # Clean the data to remove infinities and very large values
    data = clean_data_for_modeling(data)
    
    # Verify and adjust features based on available columns
    num_features = [f for f in NUMERICAL_FEATURES if f in data.columns]
    cat_features = [f for f in CATEGORICAL_FEATURES if f in data.columns]
    
    # Add additional features that might be available in the synthetic data
    additional_num_features = ['temperature', 'precipitation_probability', 'weather_severity', 
                              'median_income', 'transit_score', 'population_density', 
                              'poverty_rate', 'health_insurance_rate']
    
    for feature in additional_num_features:
        if feature in data.columns and feature not in num_features:
            num_features.append(feature)
    
    additional_cat_features = ['day_name', 'condition', 'part_of_month', 'season']
    
    for feature in additional_cat_features:
        if feature in data.columns and feature not in cat_features:
            cat_features.append(feature)
    
    print(f"Using {len(num_features)} numerical features and {len(cat_features)} categorical features")
    
    # Prepare feature matrix and target vector
    X = data[num_features + cat_features]
    y = data['is_noshow']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED
    )
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Save a summary of the features used
    if output_dir:
        with open(os.path.join(output_dir, 'features_used.txt'), 'w') as f:
            f.write("Numerical features:\n")
            for feature in num_features:
                f.write(f"- {feature}\n")
            f.write("\nCategorical features:\n")
            for feature in cat_features:
                f.write(f"- {feature}\n")
    
    try:
        # Train Random Forest model
        print("\nTraining Random Forest model...")
        rf_model = train_random_forest(X_train, y_train, X_test, y_test, 
                                    num_features, cat_features, output_dir)
    except Exception as e:
        print(f"Error in Random Forest training: {e}")
        rf_model = {"evaluation": {"accuracy": 0, "auc": 0}}
    
    try:
        # Train XGBoost model
        print("\nTraining XGBoost model...")
        xgb_model = train_xgboost(X_train, y_train, X_test, y_test,
                                num_features, cat_features, output_dir)
    except Exception as e:
        print(f"Error in XGBoost training: {e}")
        xgb_model = {"evaluation": {"accuracy": 0, "auc": 0}}
    
    # Compare models
    results = {
        'random_forest': rf_model['evaluation'] if 'evaluation' in rf_model else {"accuracy": 0, "auc": 0},
        'xgboost': xgb_model['evaluation'] if 'evaluation' in xgb_model else {"accuracy": 0, "auc": 0}
    }
    
    print("\nModel Comparison:")
    print(f"Random Forest AUC: {results['random_forest'].get('auc', 0):.4f}")
    print(f"XGBoost AUC: {results['xgboost'].get('auc', 0):.4f}")
    
    # Analyze feature importance across models if both models trained successfully
    if 'model' in rf_model and 'model' in xgb_model:
        try:
            print("\nAnalyzing feature importance...")
            analyze_feature_importance(rf_model['model'], xgb_model['model'], 
                                    num_features, cat_features, output_dir)
        except Exception as e:
            print(f"Error in feature importance analysis: {e}")
    
    return results

def clean_data_for_modeling(data):
    """Clean data to remove infinity values and prepare for modeling"""
    # Clone the DataFrame to avoid modifying the original
    df = data.copy()
    
    # Loop through numerical columns
    numerical_cols = df.select_dtypes(include=['int', 'float']).columns
    for col in numerical_cols:
        # Replace infinity with NaN
        df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        
        # Get statistics for imputation
        col_mean = df[col].mean()
        col_median = df[col].median()
        
        # If more than 5% of values are NaN, use median, otherwise use mean
        if df[col].isna().mean() > 0.05:
            df[col] = df[col].fillna(col_median)
        else:
            df[col] = df[col].fillna(col_mean)
            
        # Cap extreme values at 3 standard deviations
        std = df[col].std()
        mean = df[col].mean()
        df[col] = df[col].clip(lower=mean - 3*std, upper=mean + 3*std)
    
    # Handle categorical columns - fill missing values with most frequent
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])
    
    return df

def train_random_forest(X_train, y_train, X_test, y_test, num_features, cat_features, output_dir=None):
    """Train and evaluate a Random Forest model"""
    # Define preprocessing steps
    numeric_transformer = Pipeline(steps=[
        ('scaler', RobustScaler())  # RobustScaler is less sensitive to outliers
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_features),
            ('cat', categorical_transformer, cat_features)
        ],
        remainder='drop'  # Drop any columns not specified
    )
    
    # Create and train pipeline
    rf = RandomForestClassifier(n_estimators=100, 
                               max_depth=10,
                               min_samples_leaf=5,
                               random_state=RANDOM_SEED)
    
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', rf)
    ])
    
    # Fit the model
    rf_pipeline.fit(X_train, y_train)
    
    # Make predictions
    y_pred = rf_pipeline.predict(X_test)
    y_proba = rf_pipeline.predict_proba(X_test)
    
    # Evaluate model
    eval_results = evaluate_model(y_test, y_pred, y_proba)
    print(f"Random Forest - Accuracy: {eval_results['accuracy']:.4f}, AUC: {eval_results['auc']:.4f}")
    
    # Generate evaluation visualizations
    if output_dir:
        try:
            # ROC curve
            fpr, tpr, _ = roc_curve(y_test, y_proba[:, 1])
            plt.figure(figsize=(10, 8))
            plt.plot(fpr, tpr, label=f'Random Forest (AUC = {eval_results["auc"]:.4f})')
            plt.plot([0, 1], [0, 1], 'k--')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('ROC Curve - Random Forest')
            plt.legend(loc='lower right')
            plt.savefig(os.path.join(output_dir, 'rf_roc_curve.png'))
            plt.close()
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
            plt.xlabel('Predicted Label')
            plt.ylabel('True Label')
            plt.title('Confusion Matrix - Random Forest')
            plt.savefig(os.path.join(output_dir, 'rf_confusion_matrix.png'))
            plt.close()
            
            # Classification report
            cls_report = classification_report(y_test, y_pred, output_dict=True)
            cls_df = pd.DataFrame(cls_report).transpose()
            plt.figure(figsize=(10, 6))
            sns.heatmap(cls_df.iloc[:-1, :].astype(float), annot=True, cmap='Blues')
            plt.title('Classification Report - Random Forest')
            plt.savefig(os.path.join(output_dir, 'rf_classification_report.png'))
            plt.close()
        except Exception as e:
            print(f"Error generating RF visualizations: {e}")
    
    return {
        'model': rf_pipeline,
        'evaluation': eval_results,
        'y_pred': y_pred,
        'y_proba': y_proba
    }

def train_xgboost(X_train, y_train, X_test, y_test, num_features, cat_features, output_dir=None):
    """Train and evaluate an XGBoost model"""
    # Define preprocessing steps
    numeric_transformer = Pipeline(steps=[
        ('scaler', RobustScaler())  # RobustScaler is less sensitive to outliers
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_features),
            ('cat', categorical_transformer, cat_features)
        ],
        remainder='drop'  # Drop any columns not specified
    )
    
    # Create and train pipeline
    xgb_model = xgb.XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        min_child_weight=3,
        random_state=RANDOM_SEED,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    xgb_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', xgb_model)
    ])
    
    # Fit the model
    xgb_pipeline.fit(X_train, y_train)
    
    # Make predictions
    y_pred = xgb_pipeline.predict(X_test)
    y_proba = xgb_pipeline.predict_proba(X_test)
    
    # Evaluate model
    eval_results = evaluate_model(y_test, y_pred, y_proba)
    print(f"XGBoost - Accuracy: {eval_results['accuracy']:.4f}, AUC: {eval_results['auc']:.4f}")
    
    # Generate evaluation visualizations
    if output_dir:
        try:
            # ROC curve
            fpr, tpr, _ = roc_curve(y_test, y_proba[:, 1])
            plt.figure(figsize=(10, 8))
            plt.plot(fpr, tpr, label=f'XGBoost (AUC = {eval_results["auc"]:.4f})')
            plt.plot([0, 1], [0, 1], 'k--')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('ROC Curve - XGBoost')
            plt.legend(loc='lower right')
            plt.savefig(os.path.join(output_dir, 'xgb_roc_curve.png'))
            plt.close()
            
            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
            plt.xlabel('Predicted Label')
            plt.ylabel('True Label')
            plt.title('Confusion Matrix - XGBoost')
            plt.savefig(os.path.join(output_dir, 'xgb_confusion_matrix.png'))
            plt.close()
            
            # Classification report
            cls_report = classification_report(y_test, y_pred, output_dict=True)
            cls_df = pd.DataFrame(cls_report).transpose()
            plt.figure(figsize=(10, 6))
            sns.heatmap(cls_df.iloc[:-1, :].astype(float), annot=True, cmap='Blues')
            plt.title('Classification Report - XGBoost')
            plt.savefig(os.path.join(output_dir, 'xgb_classification_report.png'))
            plt.close()
        except Exception as e:
            print(f"Error generating XGB visualizations: {e}")
    
    return {
        'model': xgb_pipeline,
        'evaluation': eval_results,
        'y_pred': y_pred,
        'y_proba': y_proba
    }

def analyze_feature_importance(rf_pipeline, xgb_pipeline, num_features, cat_features, output_dir=None):
    """Analyze and compare feature importance across models"""
    try:
        # Extract feature importances from the trained models
        rf_model = rf_pipeline.named_steps['classifier']
        xgb_model = xgb_pipeline.named_steps['classifier']
        
        # Get the preprocessor
        rf_preprocessor = rf_pipeline.named_steps['preprocessor']
        
        # Get feature names after preprocessing
        feature_names = []
        for name, _, cols in rf_preprocessor.transformers_:
            if name == 'num':
                feature_names.extend(cols)
            elif name == 'cat':
                # Create column names for one-hot encoded features
                for col in cols:
                    # Count unique values in column to approximate number of features
                    unique_vals = min(10, len(pd.unique(pd.Series([col]))))
                    for i in range(unique_vals):
                        feature_names.append(f"{col}_{i}")
        
        # Truncate feature names if needed to match model importance shape
        feature_names = feature_names[:len(rf_model.feature_importances_)]
        
        # Store importance values for both models
        rf_importances = rf_model.feature_importances_
        xgb_importances = xgb_model.feature_importances_
        
        # Create DataFrames for better handling
        rf_importance_df = pd.DataFrame({
            'feature': feature_names[:len(rf_importances)],
            'importance': rf_importances
        }).sort_values('importance', ascending=False)
        
        xgb_importance_df = pd.DataFrame({
            'feature': feature_names[:len(xgb_importances)],
            'importance': xgb_importances
        }).sort_values('importance', ascending=False)
        
        # Display top 10 important features for each model
        print("\nTop 10 important features (Random Forest):")
        for i, (_, row) in enumerate(rf_importance_df.head(10).iterrows()):
            print(f"{i+1}. {row['feature']}: {row['importance']:.4f}")
        
        print("\nTop 10 important features (XGBoost):")
        for i, (_, row) in enumerate(xgb_importance_df.head(10).iterrows()):
            print(f"{i+1}. {row['feature']}: {row['importance']:.4f}")
        
        # Save importance data
        if output_dir:
            rf_importance_df.to_csv(os.path.join(output_dir, 'rf_feature_importance.csv'), index=False)
            xgb_importance_df.to_csv(os.path.join(output_dir, 'xgb_feature_importance.csv'), index=False)
            
            # Plot top features for Random Forest
            plt.figure(figsize=(12, 8))
            sns.barplot(x='importance', y='feature', data=rf_importance_df.head(20))
            plt.title('Top 20 Features - Random Forest')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'rf_top_features.png'))
            plt.close()
            
            # Plot top features for XGBoost
            plt.figure(figsize=(12, 8))
            sns.barplot(x='importance', y='feature', data=xgb_importance_df.head(20))
            plt.title('Top 20 Features - XGBoost')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'xgb_top_features.png'))
            plt.close()
            
    except Exception as e:
        print(f"Error in feature importance analysis: {e}")

if __name__ == "__main__":
    # Test the module with a sample dataset
    data_path = "../data/processed/synthetic_full_dataset.csv"
    if os.path.exists(data_path):
        print(f"Loading data from {data_path}")
        data = pd.read_csv(data_path)
        output_dir = "../outputs/test_models"
        os.makedirs(output_dir, exist_ok=True)
        train_initial_models(data, output_dir)
    else:
        print(f"Dataset not found at {data_path}. Please generate the dataset first.")
