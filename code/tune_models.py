import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder, RobustScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
import time

# Add the code directory to the path
sys.path.append('code')

# Import project modules
from config import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, TEST_SIZE, RANDOM_SEED, MODEL_DIR
from evaluation import evaluate_model

def load_data(data_path):
    """
    Load and prepare data for model training
    
    Parameters:
    -----------
    data_path : str
        Path to the dataset
        
    Returns:
    --------
    tuple
        X_train, X_test, y_train, y_test, num_features, cat_features
    """
    print(f"Loading data from {data_path}")
    data = pd.read_csv(data_path)
    
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
    
    return X_train, X_test, y_train, y_test, num_features, cat_features

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

def tune_random_forest(X_train, y_train, X_test, y_test, num_features, cat_features, output_dir=None):
    """
    Perform hyperparameter tuning for Random Forest model
    
    Parameters:
    -----------
    X_train, y_train : pandas.DataFrame, pandas.Series
        Training data
    X_test, y_test : pandas.DataFrame, pandas.Series
        Test data
    num_features : list
        List of numerical feature names
    cat_features : list
        List of categorical feature names
    output_dir : str, optional
        Directory to save results
        
    Returns:
    --------
    dict
        Best model and performance metrics
    """
    print("\n===== Random Forest Hyperparameter Tuning =====")
    start_time = time.time()
    
    # Define preprocessing steps
    numeric_transformer = Pipeline(steps=[
        ('scaler', RobustScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_features),
            ('cat', categorical_transformer, cat_features)
        ],
        remainder='drop'
    )
    
    # Create pipeline with placeholder model
    rf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=RANDOM_SEED))
    ])
    
    # Define parameter grid
    param_grid = {
        'classifier__n_estimators': [100, 200, 300],
        'classifier__max_depth': [5, 10, 15, None],
        'classifier__min_samples_split': [2, 5, 10],
        'classifier__min_samples_leaf': [1, 2, 4],
        'classifier__max_features': ['sqrt', 'log2', None]
    }
    
    # Perform randomized search with cross-validation
    # Using RandomizedSearchCV because there are many combinations
    print("Starting RandomizedSearchCV for Random Forest...")
    grid_search = RandomizedSearchCV(
        rf_pipeline, 
        param_distributions=param_grid,
        n_iter=20,  # Try 20 combinations
        cv=3,       # 3-fold cross-validation
        scoring='roc_auc',
        n_jobs=-1,  # Use all cores
        verbose=1,
        random_state=RANDOM_SEED
    )
    
    # Fit the grid search
    grid_search.fit(X_train, y_train)
    
    # Get best model
    best_rf_model = grid_search.best_estimator_
    
    # Make predictions
    y_pred = best_rf_model.predict(X_test)
    y_proba = best_rf_model.predict_proba(X_test)
    
    # Evaluate model
    eval_results = evaluate_model(y_test, y_pred, y_proba)
    
    elapsed_time = time.time() - start_time
    print(f"Random Forest tuning completed in {elapsed_time:.2f} seconds")
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    print(f"Test set performance - Accuracy: {eval_results['accuracy']:.4f}, AUC: {eval_results['auc']:.4f}")
    
    # Save best model
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, 'tuned_random_forest.pkl')
        joblib.dump(best_rf_model, model_path)
        print(f"Best model saved to {model_path}")
        
        # Save tuning results
        results_df = pd.DataFrame(grid_search.cv_results_)
        results_path = os.path.join(output_dir, 'rf_tuning_results.csv')
        results_df.to_csv(results_path, index=False)
        print(f"Tuning results saved to {results_path}")
    
    return {
        'model': best_rf_model,
        'evaluation': eval_results,
        'best_params': grid_search.best_params_,
        'cv_score': grid_search.best_score_
    }

def tune_xgboost(X_train, y_train, X_test, y_test, num_features, cat_features, output_dir=None):
    """
    Perform hyperparameter tuning for XGBoost model
    
    Parameters:
    -----------
    X_train, y_train : pandas.DataFrame, pandas.Series
        Training data
    X_test, y_test : pandas.DataFrame, pandas.Series
        Test data
    num_features : list
        List of numerical feature names
    cat_features : list
        List of categorical feature names
    output_dir : str, optional
        Directory to save results
        
    Returns:
    --------
    dict
        Best model and performance metrics
    """
    print("\n===== XGBoost Hyperparameter Tuning =====")
    start_time = time.time()
    
    # Define preprocessing steps
    numeric_transformer = Pipeline(steps=[
        ('scaler', RobustScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, num_features),
            ('cat', categorical_transformer, cat_features)
        ],
        remainder='drop'
    )
    
    # Create pipeline with placeholder model
    xgb_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', xgb.XGBClassifier(
            use_label_encoder=False, 
            eval_metric='logloss',
            random_state=RANDOM_SEED
        ))
    ])
    
    # Define parameter grid
    param_grid = {
        'classifier__n_estimators': [100, 200, 300],
        'classifier__learning_rate': [0.01, 0.05, 0.1, 0.2],
        'classifier__max_depth': [3, 5, 7, 9],
        'classifier__min_child_weight': [1, 3, 5],
        'classifier__subsample': [0.6, 0.8, 1.0],
        'classifier__colsample_bytree': [0.6, 0.8, 1.0],
        'classifier__gamma': [0, 0.1, 0.2]
    }
    
    # Perform randomized search with cross-validation
    print("Starting RandomizedSearchCV for XGBoost...")
    grid_search = RandomizedSearchCV(
        xgb_pipeline, 
        param_distributions=param_grid,
        n_iter=20,  # Try 20 combinations
        cv=3,       # 3-fold cross-validation
        scoring='roc_auc',
        n_jobs=-1,  # Use all cores
        verbose=1,
        random_state=RANDOM_SEED
    )
    
    # Fit the grid search
    grid_search.fit(X_train, y_train)
    
    # Get best model
    best_xgb_model = grid_search.best_estimator_
    
    # Make predictions
    y_pred = best_xgb_model.predict(X_test)
    y_proba = best_xgb_model.predict_proba(X_test)
    
    # Evaluate model
    eval_results = evaluate_model(y_test, y_pred, y_proba)
    
    elapsed_time = time.time() - start_time
    print(f"XGBoost tuning completed in {elapsed_time:.2f} seconds")
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best cross-validation score: {grid_search.best_score_:.4f}")
    print(f"Test set performance - Accuracy: {eval_results['accuracy']:.4f}, AUC: {eval_results['auc']:.4f}")
    
    # Save best model
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, 'tuned_xgboost.pkl')
        joblib.dump(best_xgb_model, model_path)
        print(f"Best model saved to {model_path}")
        
        # Save tuning results
        results_df = pd.DataFrame(grid_search.cv_results_)
        results_path = os.path.join(output_dir, 'xgb_tuning_results.csv')
        results_df.to_csv(results_path, index=False)
        print(f"Tuning results saved to {results_path}")
    
    return {
        'model': best_xgb_model,
        'evaluation': eval_results,
        'best_params': grid_search.best_params_,
        'cv_score': grid_search.best_score_
    }

def plot_performance_comparison(rf_results, xgb_results, output_dir):
    """Create visualizations comparing model performance"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Compare metrics
    models = ['Random Forest', 'XGBoost']
    metrics = ['accuracy', 'precision', 'recall', 'f1', 'auc']
    values = [
        [rf_results['evaluation'][m] for m in metrics],
        [xgb_results['evaluation'][m] for m in metrics]
    ]
    
    # Create comparison bar chart
    plt.figure(figsize=(12, 6))
    x = np.arange(len(metrics))
    width = 0.35
    
    bar1 = plt.bar(x - width/2, values[0], width, label='Random Forest')
    bar2 = plt.bar(x + width/2, values[1], width, label='XGBoost')
    
    plt.xlabel('Metric')
    plt.ylabel('Score')
    plt.title('Model Performance Comparison')
    plt.xticks(x, metrics)
    plt.ylim(0, 1.1)
    plt.legend()
    
    # Add value labels
    for i, bars in enumerate([bar1, bar2]):
        for bar in bars:
            height = bar.get_height()
            plt.annotate(f'{height:.3f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'model_comparison.png'))
    plt.close()
    
    # Create a summary table
    summary = {
        'Model': models,
        'Accuracy': [rf_results['evaluation']['accuracy'], xgb_results['evaluation']['accuracy']],
        'Precision': [rf_results['evaluation']['precision'], xgb_results['evaluation']['precision']],
        'Recall': [rf_results['evaluation']['recall'], xgb_results['evaluation']['recall']],
        'F1 Score': [rf_results['evaluation']['f1'], xgb_results['evaluation']['f1']],
        'AUC': [rf_results['evaluation']['auc'], xgb_results['evaluation']['auc']],
        'CV Score': [rf_results['cv_score'], xgb_results['cv_score']]
    }
    
    pd.DataFrame(summary).to_csv(os.path.join(output_dir, 'model_summary.csv'), index=False)

def main():
    """Main function to run hyperparameter tuning"""
    # Create output directory
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join('outputs', f'tuning_{timestamp}')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Output directory: {output_dir}")
    
    # Load data
    data_path = os.path.join('data', 'processed', 'synthetic_full_dataset.csv')
    X_train, X_test, y_train, y_test, num_features, cat_features = load_data(data_path)
    
    # Tune Random Forest
    rf_results = tune_random_forest(
        X_train, y_train, X_test, y_test, 
        num_features, cat_features, 
        os.path.join(output_dir, 'random_forest')
    )
    
    # Tune XGBoost
    xgb_results = tune_xgboost(
        X_train, y_train, X_test, y_test,
        num_features, cat_features,
        os.path.join(output_dir, 'xgboost')
    )
    
    # Plot comparison
    plot_performance_comparison(rf_results, xgb_results, output_dir)
    
    print("\n===== Hyperparameter Tuning Complete =====")
    print(f"Results saved to {output_dir}")
    
    # Return best model based on test AUC
    if rf_results['evaluation']['auc'] > xgb_results['evaluation']['auc']:
        print("Random Forest performed better on test data")
        best_model = rf_results['model']
        best_model_name = 'random_forest'
    else:
        print("XGBoost performed better on test data")
        best_model = xgb_results['model']
        best_model_name = 'xgboost'
    
    # Save the overall best model
    best_model_path = os.path.join(output_dir, f'best_model_{best_model_name}.pkl')
    joblib.dump(best_model, best_model_path)
    print(f"Best overall model saved to {best_model_path}")
    
    # Create a summary file
    with open(os.path.join(output_dir, 'tuning_summary.txt'), 'w') as f:
        f.write("VitalSchedule Model Tuning Summary\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Random Forest Best Parameters:\n")
        for param, value in rf_results['best_params'].items():
            f.write(f"- {param.replace('classifier__', '')}: {value}\n")
        f.write(f"Cross-validation AUC: {rf_results['cv_score']:.4f}\n")
        f.write(f"Test AUC: {rf_results['evaluation']['auc']:.4f}\n\n")
        
        f.write("XGBoost Best Parameters:\n")
        for param, value in xgb_results['best_params'].items():
            f.write(f"- {param.replace('classifier__', '')}: {value}\n")
        f.write(f"Cross-validation AUC: {xgb_results['cv_score']:.4f}\n")
        f.write(f"Test AUC: {xgb_results['evaluation']['auc']:.4f}\n\n")
        
        f.write(f"Best overall model: {best_model_name.replace('_', ' ').title()}")

if __name__ == "__main__":
    main()
