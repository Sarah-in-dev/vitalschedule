# code/readmission/evaluation.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from sklearn.metrics import (
    roc_curve, precision_recall_curve, auc, 
    roc_auc_score, confusion_matrix, classification_report,
    brier_score_loss,
)

# Handle deprecated or missing calibration_curve
try:
    from sklearn.metrics import calibration_curve
except ImportError:
    from sklearn.calibration import calibration_curve
except ImportError:
    # Fallback implementation if calibration_curve is not available
    def calibration_curve(y_true, y_prob, n_bins=5):
        """Simple implementation of calibration curve for older sklearn versions"""
        bins = np.linspace(0., 1. + 1e-8, n_bins + 1)
        binids = np.digitize(y_prob, bins) - 1
        bin_sums = np.bincount(binids, weights=y_prob, minlength=len(bins))
        bin_true = np.bincount(binids, weights=y_true, minlength=len(bins))
        bin_total = np.bincount(binids, minlength=len(bins))
        nonzero = bin_total != 0
        prob_true = bin_true[nonzero] / bin_total[nonzero]
        prob_pred = bin_sums[nonzero] / bin_total[nonzero]
        return prob_true, prob_pred

def evaluate_model(model, X_test, y_test, threshold=0.5, output_dir=None):
    """
    Evaluate a model's performance on the test set
    
    Parameters:
    -----------
    model : sklearn.pipeline.Pipeline
        Trained model pipeline
    X_test : pandas.DataFrame
        Test features
    y_test : pandas.Series
        True labels
    threshold : float
        Probability threshold for classification
    output_dir : str, optional
        Directory to save evaluation results
        
    Returns:
    --------
    dict
        Dictionary with evaluation metrics
    """
    print("Evaluating model performance...")
    
    # Generate predictions
    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= threshold).astype(int)
    
    # Calculate standard metrics
    metrics = {
        'accuracy': (y_pred == y_test).mean(),
        'auc': roc_auc_score(y_test, y_prob),
        'precision': (y_pred & y_test).sum() / y_pred.sum() if y_pred.sum() > 0 else 0,
        'recall': (y_pred & y_test).sum() / y_test.sum() if y_test.sum() > 0 else 0,
        'specificity': ((1 - y_pred) & (1 - y_test)).sum() / (1 - y_test).sum() if (1 - y_test).sum() > 0 else 0,
        'brier_score': brier_score_loss(y_test, y_prob)
    }
    
    # Calculate F1 score
    if metrics['precision'] + metrics['recall'] > 0:
        metrics['f1'] = 2 * metrics['precision'] * metrics['recall'] / (metrics['precision'] + metrics['recall'])
    else:
        metrics['f1'] = 0
    
    # Print metrics
    print("Model Performance:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.4f}")
    
    # Create visualizations if output directory is specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save metrics to CSV
        pd.DataFrame([metrics]).to_csv(os.path.join(output_dir, "metrics.csv"), index=False)
        
        # ROC curve
        create_roc_curve(y_test, y_prob, output_dir)
        
        # Precision-Recall curve
        create_pr_curve(y_test, y_prob, output_dir)
        
        # Confusion matrix
        create_confusion_matrix(y_test, y_pred, output_dir)
        
        # Calibration curve
        create_calibration_curve(y_test, y_prob, output_dir)
        
        # Threshold analysis
        create_threshold_analysis(y_test, y_prob, output_dir)
    
    return metrics

def create_roc_curve(y_test, y_prob, output_dir):
    """Create and save ROC curve"""
    fpr, tpr, thresholds = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(10, 8))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, "roc_curve.png"))
    plt.close()

def create_pr_curve(y_test, y_prob, output_dir):
    """Create and save Precision-Recall curve"""
    precision, recall, thresholds = precision_recall_curve(y_test, y_prob)
    pr_auc = auc(recall, precision)
    
    plt.figure(figsize=(10, 8))
    plt.plot(recall, precision, color='blue', lw=2, label=f'PR curve (area = {pr_auc:.3f})')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc='lower left')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, "pr_curve.png"))
    plt.close()

def create_confusion_matrix(y_test, y_pred, output_dir):
    """Create and save confusion matrix"""
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(8, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    plt.savefig(os.path.join(output_dir, "confusion_matrix.png"))
    plt.close()
    
    # Generate classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    pd.DataFrame(report).transpose().to_csv(os.path.join(output_dir, "classification_report.csv"))

def create_calibration_curve(y_test, y_prob, output_dir):
    """Create and save calibration curve"""
    fraction_of_positives, mean_predicted_value = calibration_curve(y_test, y_prob, n_bins=10)
    
    plt.figure(figsize=(10, 8))
    plt.plot(mean_predicted_value, fraction_of_positives, "s-", label="Calibration curve")
    plt.plot([0, 1], [0, 1], "--", color="gray", label="Perfect calibration")
    plt.xlabel("Mean predicted probability")
    plt.ylabel("Fraction of positives")
    plt.title("Calibration Curve")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, "calibration_curve.png"))
    plt.close()

def create_threshold_analysis(y_test, y_prob, output_dir):
    """Analyze different probability thresholds"""
    thresholds = np.arange(0.1, 1.0, 0.1)
    metrics = []
    
    for threshold in thresholds:
        y_pred = (y_prob >= threshold).astype(int)
        
        # Calculate metrics
        tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        metrics.append({
            'threshold': threshold,
            'precision': precision,
            'recall': recall,
            'specificity': specificity,
            'f1': f1,
            'tp': tp,
            'fp': fp,
            'tn': tn,
            'fn': fn
        })
    
    # Create DataFrame
    metrics_df = pd.DataFrame(metrics)
    
    # Save to CSV
    metrics_df.to_csv(os.path.join(output_dir, "threshold_analysis.csv"), index=False)
    
    # Plot metrics vs threshold
    plt.figure(figsize=(12, 8))
    for col in ['precision', 'recall', 'specificity', 'f1']:
        plt.plot(metrics_df['threshold'], metrics_df[col], marker='o', label=col)
    plt.xlabel('Threshold')
    plt.ylabel('Score')
    plt.title('Performance Metrics vs. Threshold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, "threshold_analysis.png"))
    plt.close()

def evaluate_on_subgroups(model, X_test, y_test, subgroup_col, output_dir=None):
    """
    Evaluate model performance on different subgroups
    
    Parameters:
    -----------
    model : sklearn.pipeline.Pipeline
        Trained model pipeline
    X_test : pandas.DataFrame
        Test features
    y_test : pandas.Series
        True labels
    subgroup_col : str
        Column to use for defining subgroups
    output_dir : str, optional
        Directory to save evaluation results
    
    Returns:
    --------
    pandas.DataFrame
        Performance metrics by subgroup
    """
    if subgroup_col not in X_test.columns:
        print(f"Subgroup column '{subgroup_col}' not found in test data")
        return None
    
    # Generate predictions
    y_prob = model.predict_proba(X_test)[:, 1]
    
    # Create a DataFrame with test data and predictions
    eval_df = pd.DataFrame({
        'y_true': y_test.values,
        'y_prob': y_prob,
        'subgroup': X_test[subgroup_col].values
    })
    
    # Calculate metrics for each subgroup
    subgroups = eval_df['subgroup'].unique()
    results = []
    
    for subgroup in subgroups:
        subgroup_data = eval_df[eval_df['subgroup'] == subgroup]
        
        if len(subgroup_data) < 10 or subgroup_data['y_true'].nunique() < 2:
            # Skip small subgroups or those with only one class
            continue
        
        # Calculate AUC
        auc = roc_auc_score(subgroup_data['y_true'], subgroup_data['y_prob'])
        
        # Calculate other metrics with threshold 0.5
        y_pred = (subgroup_data['y_prob'] >= 0.5).astype(int)
        precision = (y_pred & subgroup_data['y_true']).sum() / y_pred.sum() if y_pred.sum() > 0 else 0
        recall = (y_pred & subgroup_data['y_true']).sum() / subgroup_data['y_true'].sum() if subgroup_data['y_true'].sum() > 0 else 0
        
        results.append({
            'subgroup': subgroup,
            'count': len(subgroup_data),
            'readmission_rate': subgroup_data['y_true'].mean(),
            'auc': auc,
            'precision': precision,
            'recall': recall
        })
    
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by count
    results_df = results_df.sort_values('count', ascending=False)
    
    # Save to CSV if output directory is specified
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        results_df.to_csv(os.path.join(output_dir, f"subgroup_analysis_{subgroup_col}.csv"), index=False)
        
        # Create visualization
        plt.figure(figsize=(12, 8))
        plt.bar(results_df['subgroup'].astype(str), results_df['auc'])
        plt.xlabel(subgroup_col)
        plt.ylabel('AUC')
        plt.title(f'AUC by {subgroup_col}')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"subgroup_auc_{subgroup_col}.png"))
        plt.close()
    
    return results_df

if __name__ == "__main__":
    print("This module provides functions for evaluating readmission prediction models.")
    print("Import and use these functions in your pipeline or run_evaluation.py.")
