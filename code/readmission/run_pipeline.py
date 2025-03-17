# code/readmission/run_pipeline.py
import os
import sys
import argparse
import pandas as pd
import numpy as np
from datetime import datetime
import joblib

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(parent_dir)
sys.path.insert(0, project_root)

# Import modules
from data_processing import load_mimic_tables, create_readmission_dataset, save_processed_data
from feature_extraction import extract_features, save_features
from model_training import prepare_modeling_data, train_models, tune_best_model, extract_feature_importance
from evaluation import evaluate_model, evaluate_on_subgroups

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run the readmission prediction pipeline')
    parser.add_argument('--data_dir', type=str, default=os.path.join(project_root, 'data'),
                        help='Path to the data directory')
    parser.add_argument('--output_dir', type=str, default=os.path.join(project_root, 'outputs', 'readmission'),
                        help='Path to the output directory')
    parser.add_argument('--readmission_window', type=int, default=30,
                        help='Readmission window in days (default: 30)')
    parser.add_argument('--tune_models', action='store_true',
                        help='Perform hyperparameter tuning')
    parser.add_argument('--skip_data_processing', action='store_true',
                        help='Skip data processing step (use existing processed data)')
    parser.add_argument('--skip_feature_extraction', action='store_true',
                        help='Skip feature extraction step (use existing features)')
    return parser.parse_args()

def create_timestamp_folder(base_dir):
    """Create a timestamped folder for this run"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_dir = os.path.join(base_dir, f"run_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir

def main():
    # Parse command-line arguments
    args = parse_arguments()
    
    # Set up paths
    data_dir = args.data_dir
    raw_dir = os.path.join(data_dir, 'raw', 'mimic-iv')
    processed_dir = os.path.join(data_dir, 'processed', 'readmission')
    output_dir = args.output_dir
    
    # Create output directories
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a timestamped run directory
    run_dir = create_timestamp_folder(output_dir)
    
    # Log run information
    with open(os.path.join(run_dir, 'run_info.txt'), 'w') as f:
        f.write(f"Readmission Prediction Pipeline\n")
        f.write(f"Run timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Readmission window: {args.readmission_window} days\n")
        f.write(f"Data directory: {data_dir}\n")
        f.write(f"Output directory: {run_dir}\n")
        f.write(f"Tune models: {args.tune_models}\n")
    
    # Step 1: Data Processing
    if not args.skip_data_processing:
        print("\n=== Step 1: Data Processing ===")
        
        # Check if MIMIC-IV data exists
        if not os.path.exists(raw_dir):
            print(f"Error: MIMIC-IV data not found at {raw_dir}")
            return
        
        # Load MIMIC-IV tables
        tables = load_mimic_tables(raw_dir)
        
        # Create readmission dataset
        dataset = create_readmission_dataset(tables, readmission_window=args.readmission_window)
        
        # Save processed data
        save_processed_data(dataset, processed_dir)
    else:
        print("\n=== Skipping Data Processing ===")
        
        # Check if processed data exists
        dataset_path = os.path.join(processed_dir, 'readmission_data.csv')
        if not os.path.exists(dataset_path):
            print(f"Error: Processed data not found at {dataset_path}")
            return
        
        print(f"Loading processed data from {dataset_path}")
        dataset = pd.read_csv(dataset_path)
        
        # Convert date columns to datetime
        date_cols = ['admittime', 'dischtime', 'deathtime', 'edregtime', 'edouttime', 'next_admittime']
        for col in date_cols:
            if col in dataset.columns:
                dataset[col] = pd.to_datetime(dataset[col])
    
    # Step 2: Feature Extraction
    if not args.skip_feature_extraction:
        print("\n=== Step 2: Feature Extraction ===")
        
        # Extract features
        features_df = extract_features(dataset)
        
        # Save features
        save_features(features_df, processed_dir)
    else:
        print("\n=== Skipping Feature Extraction ===")
        
        # Check if features exist
        features_path = os.path.join(processed_dir, 'readmission_features.csv')
        if not os.path.exists(features_path):
            print(f"Error: Features not found at {features_path}")
            return
        
        print(f"Loading features from {features_path}")
        features_df = pd.read_csv(features_path)
    
    # Step 3: Model Training
    print("\n=== Step 3: Model Training ===")
    
    # Prepare data for modeling
    X_train, X_test, y_train, y_test, num_features, cat_features = prepare_modeling_data(features_df)
    
    # Save feature lists for reference
    with open(os.path.join(run_dir, 'feature_lists.txt'), 'w') as f:
        f.write("Numerical features:\n")
        for feature in num_features:
            f.write(f"- {feature}\n")
        f.write("\nCategorical features:\n")
        for feature in cat_features:
            f.write(f"- {feature}\n")
    
    # Train models
    model_dir = os.path.join(run_dir, 'models')
    os.makedirs(model_dir, exist_ok=True)
    
    models_results = train_models(X_train, X_test, y_train, y_test, num_features, cat_features, model_dir)
    
    # Find best model
    best_model_name = max(models_results.items(), key=lambda x: x[1]['evaluation']['auc'])[0]
    best_model = models_results[best_model_name]['pipeline']
    
    print(f"\nBest model: {best_model_name}")
    print(f"AUC: {models_results[best_model_name]['evaluation']['auc']:.4f}")
    
    # Save best model separately
    joblib.dump(best_model, os.path.join(model_dir, 'best_model.joblib'))
    
    # Step 4: Model Evaluation
    print("\n=== Step 4: Model Evaluation ===")
    
    # Evaluate best model
    eval_dir = os.path.join(run_dir, 'evaluation')
    os.makedirs(eval_dir, exist_ok=True)
    
    metrics = evaluate_model(best_model, X_test, y_test, output_dir=eval_dir)
    
    # Evaluate on subgroups if available
    for subgroup_col in ['age_group', 'gender', 'los_group', 'emergency']:
        if subgroup_col in X_test.columns:
            print(f"\nEvaluating on subgroup: {subgroup_col}")
            subgroup_results = evaluate_on_subgroups(best_model, X_test, y_test, subgroup_col, eval_dir)
    
    # Extract feature importance
    importance_df = extract_feature_importance(best_model, num_features, cat_features, eval_dir)
    
    # Step 5: Model Tuning (optional)
    if args.tune_models:
        print("\n=== Step 5: Model Tuning ===")
        
        # Define model parameters for tuning
        model_params = {
            'logistic_regression': {
                'model': LogisticRegression(max_iter=1000, random_state=42),
                'params': {
                    'classifier__C': [0.01, 0.1, 1.0, 10.0],
                    'classifier__penalty': ['l1', 'l2'],
                    'classifier__solver': ['liblinear', 'saga'],
                    'classifier__class_weight': [None, 'balanced']
                }
            },
            'random_forest': {
                'model': RandomForestClassifier(random_state=42),
                'params': {
                    'classifier__n_estimators': [100, 200, 300],
                    'classifier__max_depth': [None, 10, 20, 30],
                    'classifier__min_samples_split': [2, 5, 10],
                    'classifier__min_samples_leaf': [1, 2, 4],
                    'classifier__class_weight': [None, 'balanced']
                }
            },
            'xgboost': {
                'model': xgb.XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
                'params': {
                    'classifier__n_estimators': [100, 200, 300],
                    'classifier__learning_rate': [0.01, 0.05, 0.1],
                    'classifier__max_depth': [3, 5, 7],
                    'classifier__min_child_weight': [1, 3, 5],
                    'classifier__subsample': [0.8, 0.9, 1.0],
                    'classifier__colsample_bytree': [0.8, 0.9, 1.0]
                }
            }
        }
        
        # Tune the best model
        tuned_dir = os.path.join(run_dir, 'tuned_models')
        os.makedirs(tuned_dir, exist_ok=True)
        
        tuned_results = tune_best_model(X_train, X_test, y_train, y_test, num_features, cat_features,
                                       best_model_name, model_params[best_model_name], tuned_dir)
        
        # Evaluate tuned model
        tuned_eval_dir = os.path.join(tuned_dir, 'evaluation')
        os.makedirs(tuned_eval_dir, exist_ok=True)
        
        tuned_metrics = evaluate_model(tuned_results['pipeline'], X_test, y_test, output_dir=tuned_eval_dir)
        
        # Extract feature importance from tuned model
        tuned_importance_df = extract_feature_importance(tuned_results['pipeline'], num_features, cat_features, tuned_eval_dir)
        
        # Save comparison of original vs tuned model
        comparison = pd.DataFrame({
            'metric': metrics.keys(),
            'original': metrics.values(),
            'tuned': [tuned_metrics[k] for k in metrics.keys()]
        })
        
        comparison.to_csv(os.path.join(run_dir, 'tuning_comparison.csv'), index=False)
        
        # Create comparison plot
        plt.figure(figsize=(10, 6))
        comparison.plot(x='metric', y=['original', 'tuned'], kind='bar')
        plt.title('Performance Comparison: Original vs Tuned Model')
        plt.ylabel('Score')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(run_dir, 'tuning_comparison.png'))
        plt.close()
    
    # Step 6: Generate Summary Report
    print("\n=== Step 6: Generating Summary Report ===")
    
    # Create a summary report
    with open(os.path.join(run_dir, 'summary_report.md'), 'w') as f:
        f.write("# Hospital Readmission Prediction: Summary Report\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Dataset Statistics\n\n")
        f.write(f"- Total admissions: {len(dataset)}\n")
        f.write(f"- Readmission rate: {dataset['is_readmission'].mean():.2%}\n")
        f.write(f"- Readmission window: {args.readmission_window} days\n\n")
        
        f.write("## Features\n\n")
        f.write(f"- Total features: {len(num_features) + len(cat_features)}\n")
        f.write(f"- Numerical features: {len(num_features)}\n")
        f.write(f"- Categorical features: {len(cat_features)}\n\n")
        
        if importance_df is not None:
            f.write("### Top 10 Important Features\n\n")
            for i, row in importance_df.head(10).iterrows():
                f.write(f"{i+1}. {row['feature']}: {row['importance']:.4f}\n")
            f.write("\n")
        
        f.write("## Model Performance\n\n")
        f.write(f"- Best model: {best_model_name}\n")
        for metric, value in metrics.items():
            f.write(f"- {metric}: {value:.4f}\n")
        f.write("\n")
        
        if args.tune_models:
            f.write("## Tuned Model Performance\n\n")
            for metric, value in tuned_metrics.items():
                f.write(f"- {metric}: {value:.4f}\n")
            f.write("\n")
            
            f.write("### Performance Improvement\n\n")
            for metric in metrics.keys():
                improvement = tuned_metrics[metric] - metrics[metric]
                f.write(f"- {metric}: {improvement:+.4f}\n")
            f.write("\n")
        
        f.write("## Conclusion\n\n")
        if metrics['auc'] > 0.7:
            f.write("The model shows good discriminative ability with AUC > 0.7. It can effectively identify patients at risk of readmission.\n\n")
        else:
            f.write("The model shows moderate discriminative ability. Further refinement may be needed.\n\n")
        
        f.write("## Next Steps\n\n")
        f.write("1. Validate the model on external data\n")
        f.write("2. Develop intervention strategies for high-risk patients\n")
        f.write("3. Implement the model in a clinical setting\n")
        f.write("4. Monitor and update the model periodically\n")
    
    print(f"\nPipeline complete! Results saved to: {run_dir}")
    print(f"Summary report: {os.path.join(run_dir, 'summary_report.md')}")

if __name__ == "__main__":
    main()
