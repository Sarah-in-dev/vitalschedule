#!/usr/bin/env python
"""
VitalSchedule Analysis Runner

This script orchestrates the full analysis pipeline for the VitalSchedule project:
1. Generate synthetic data
2. Run exploratory analysis
3. Train predictive models
4. Generate insights report

Usage:
  python run_analysis.py [--no-plots] [--sample-size SAMPLE_SIZE]

Options:
  --no-plots           Don't generate plots (useful on headless systems)
  --sample-size SIZE   Number of appointments to generate (default: 10000)
"""

import os
import sys
import argparse
from datetime import datetime
import pandas as pd

# Add local modules to path
sys.path.append('code')

# Import analysis modules
from generate_explore_data import generate_full_dataset, create_exploratory_visualizations, analyze_noshow_factors
from predictive_analysis import train_initial_models

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run the VitalSchedule analysis pipeline')
parser.add_argument('--no-plots', action='store_true', help="Don't generate plots")
parser.add_argument('--sample-size', type=int, default=10000, help='Number of appointments to generate')
args = parser.parse_args()

def main():
    # Create output directories
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join('outputs', timestamp)
    viz_dir = os.path.join(output_dir, 'visualizations')
    model_dir = os.path.join(output_dir, 'models')
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(viz_dir, exist_ok=True)
    os.makedirs(model_dir, exist_ok=True)
    
    print(f"===== VitalSchedule Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
    print(f"Output directory: {output_dir}")
    print(f"Sample size: {args.sample_size} appointments")
    
    # Step 1: Generate synthetic data
    print("\n===== STEP 1: GENERATING SYNTHETIC DATA =====")
    data = generate_full_dataset(n_patients=args.sample_size//5, n_appointments=args.sample_size, save=True)
    
    # Save a copy to the output directory
    data_path = os.path.join(output_dir, 'synthetic_dataset.csv')
    data.to_csv(data_path, index=False)
    print(f"Dataset saved to {data_path}")
    
    # Step 2: Run exploratory analysis
    print("\n===== STEP 2: RUNNING EXPLORATORY ANALYSIS =====")
    if not args.no_plots:
        create_exploratory_visualizations(data, viz_dir)
    
    # Analyze key factors
    factors_df = analyze_noshow_factors(data)
    factors_df.to_csv(os.path.join(output_dir, 'noshow_factors.csv'), index=False)
    
    # Step 3: Train predictive models
    print("\n===== STEP 3: TRAINING PREDICTIVE MODELS =====")
    model_results = train_initial_models(data, model_dir if not args.no_plots else None)
    
    # Save model results
    pd.DataFrame({k: v for k, v in model_results.items() if isinstance(v, dict)}).to_csv(
        os.path.join(output_dir, 'model_performance.csv')
    )
    
    # Step 4: Generate summary
    print("\n===== STEP 4: GENERATING SUMMARY REPORT =====")
    with open(os.path.join(output_dir, 'analysis_summary.txt'), 'w') as f:
        f.write(f"VitalSchedule Analysis Summary\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"Dataset Statistics:\n")
        f.write(f"- Total appointments: {len(data)}\n")
        f.write(f"- No-show rate: {data['is_noshow'].mean():.2%}\n")
        f.write(f"- Number of patients: {data['patient_id'].nunique()}\n\n")
        
        f.write(f"Top 5 No-Show Factors:\n")
        for i, row in factors_df.head(5).iterrows():
            f.write(f"- {row['feature']}: {row['importance']:.4f}\n")
            f.write(f"  Highest in {row['max_category']} ({row['max_rate']:.1%}), Lowest in {row['min_category']} ({row['min_rate']:.1%})\n")
        f.write("\n")
        
        f.write(f"Model Performance:\n")
        for model, metrics in model_results.items():
            f.write(f"- {model.title()}:\n")
            for metric, value in metrics.items():
                f.write(f"  {metric}: {value:.4f}\n")
        
    print(f"\nAnalysis complete! Results saved to {output_dir}")
    print(f"Run 'python -m http.server' in the output directory to view visualizations in a web browser")

if __name__ == "__main__":
    main()
