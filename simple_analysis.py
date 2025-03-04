#!/usr/bin/env python
"""
VitalSchedule Simple Analysis

This script generates synthetic data and performs basic analysis for the VitalSchedule project.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Import your existing synthetic data module
sys.path.append('code')
from synthetic_data import generate_synthetic_data

# Create outputs directory
os.makedirs('outputs', exist_ok=True)

def main():
    print("Generating synthetic appointment data...")
    # Generate synthetic data
    data = generate_synthetic_data(n_patients=500, n_appointments=2000)
    
    # Save the data
    data.to_csv('outputs/synthetic_data.csv', index=False)
    print(f"Generated dataset with {len(data)} appointments")
    
    # Basic data exploration
    print("\nData Summary:")
    print(f"Total appointments: {len(data)}")
    print(f"No-show rate: {data['is_noshow'].mean():.2%}")
    print(f"Number of patients: {data['patient_id'].nunique()}")
    
    # Analyze no-show rates by different factors
    print("\nNo-show Rates by Appointment Type:")
    appt_type_noshow = data.groupby('appointment_type')['is_noshow'].mean().sort_values(ascending=False)
    print(appt_type_noshow)
    
    print("\nNo-show Rates by Day of Week:")
    day_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    data['day_name'] = data['day_of_week'].map(day_mapping)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_noshow = data.groupby('day_name')['is_noshow'].mean()
    day_noshow = day_noshow.reindex(day_order)
    print(day_noshow)
    
    print("\nNo-show Rates by Hour of Day:")
    hour_noshow = data.groupby('hour_of_day')['is_noshow'].mean()
    print(hour_noshow)
    
    # Create some simple visualizations if matplotlib is available
    try:
        # Create a plots directory
        os.makedirs('outputs/plots', exist_ok=True)
        
        # 1. No-show distribution
        plt.figure(figsize=(10, 6))
        show_counts = data['is_noshow'].value_counts()
        ax = sns.barplot(x=show_counts.index, y=show_counts.values)
        plt.title('Distribution of No-shows vs. Attended Appointments')
        plt.xlabel('No-show Status (1 = No-show, 0 = Attended)')
        plt.ylabel('Count')
        for i, count in enumerate(show_counts.values):
            ax.text(i, count + 100, f'{count} ({count/sum(show_counts.values):.1%})', 
                    ha='center', va='bottom')
        plt.savefig('outputs/plots/01_noshow_distribution.png')
        plt.close()
        
        # 2. No-show rate by appointment type
        plt.figure(figsize=(12, 7))
        ax = sns.barplot(x=appt_type_noshow.index, y=appt_type_noshow.values)
        plt.title('No-show Rate by Appointment Type')
        plt.xlabel('Appointment Type')
        plt.ylabel('No-show Rate')
        plt.ylim(0, max(appt_type_noshow.values) * 1.2)
        for i, rate in enumerate(appt_type_noshow.values):
            ax.text(i, rate + 0.01, f'{rate:.1%}', ha='center', va='bottom')
        plt.savefig('outputs/plots/02_noshow_by_appt_type.png')
        plt.close()
        
        print("\nCreated visualizations in outputs/plots/")
        
    except Exception as e:
        print(f"Warning: Could not create visualizations: {e}")
    
    print("\nAnalysis complete! Results saved to outputs/")

if __name__ == "__main__":
    main()
