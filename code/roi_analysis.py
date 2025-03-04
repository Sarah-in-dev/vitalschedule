import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from datetime import datetime

# Add code directory to path
sys.path.append('code')

# Import project modules
from intervention_engine import InterventionEngine
from roi_calculator import ROICalculator

class NoShowROIAnalyzer:
    def __init__(self, model_path, data_path=None, data=None):
        """
        Initialize the ROI analyzer
        
        Parameters:
        -----------
        model_path : str
            Path to the trained model
        data_path : str, optional
            Path to appointment data (if not provided in data)
        data : pandas.DataFrame, optional
            Appointment data (if not loading from file)
        """
        # Load model
        self.model = joblib.load(model_path)
        print(f"Loaded model from {model_path}")
        
        # Load or set data
        if data is not None:
            self.data = data
        elif data_path is not None:
            self.data = pd.read_csv(data_path)
            print(f"Loaded data from {data_path}")
        else:
            raise ValueError("Either data or data_path must be provided")
            
        # Initialize components
        self.intervention_engine = InterventionEngine()
        self.roi_calculator = ROICalculator()
        
    def predict_no_show_risks(self):
        """
        Generate no-show risk predictions for appointments
        
        Returns:
        --------
        pandas.DataFrame
            Data with risk predictions added
        """
        # Make a copy of the data to avoid modifying the original
        data = self.data.copy()
        
        # Get feature names from the model pipeline
        # This extracts preprocessor and feature names from the loaded model
        preprocessor = self.model.named_steps.get('preprocessor', None)
        if preprocessor is None:
            raise ValueError("Model does not have a 'preprocessor' step")
            
        # Get numerical and categorical features used by the model
        feature_names = []
        for name, _, cols in preprocessor.transformers_:
            if cols is not None:  # Sometimes cols can be 'remainder'
                if isinstance(cols, list):
                    feature_names.extend(cols)
                    
        # Ensure all required features are in the data
        missing_features = [f for f in feature_names if f not in data.columns]
        if missing_features:
            raise ValueError(f"Data is missing required features: {missing_features}")
            
        # Make predictions
        print("Generating no-show risk predictions...")
        X = data[feature_names]
        data['risk_score'] = self.model.predict_proba(X)[:, 1]
        
        return data
    
    def apply_interventions(self, data=None, risk_threshold=0.5, max_interventions_per_day=None):
        """
        Apply interventions to high-risk appointments
        
        Parameters:
        -----------
        data : pandas.DataFrame, optional
            Data with risk predictions (if not provided, uses previously predicted data)
        risk_threshold : float
            Risk threshold for intervention (0.0-1.0)
        max_interventions_per_day : int, optional
            Maximum number of interventions per day (for budget constraints)
            
        Returns:
        --------
        pandas.DataFrame
            Data with intervention recommendations
        """
        if data is None:
            data = self.predict_no_show_risks()
            
        # Make a copy to avoid modifying the input
        result = data.copy()
        
        # Identify high-risk appointments
        high_risk = result[result['risk_score'] >= risk_threshold].copy()
        print(f"Identified {len(high_risk)} appointments with risk score >= {risk_threshold}")

        # If no high-risk appointments, return original data with empty intervention details
        if len(high_risk) == 0:
            # Add empty intervention columns to the result
            result['baseline_attendance_prob'] = 1 - result['risk_score']
            result['new_attendance_prob'] = result['baseline_attendance_prob']
            result['improvement'] = 0
            result['intervention_cost'] = 0
            result['interventions'] = None
            result['interventions'] = result['interventions'].apply(lambda x: [] if x is None else x)
    
            # Return original data and empty DataFrame with the expected columns
            empty_interventions = pd.DataFrame(columns=[
                'appointment_id', 'risk_score', 'baseline_attendance_prob',
                'new_attendance_prob', 'improvement', 'intervention_cost',
                'interventions', 'intervention_details'
            ])
    
            return result, empty_interventions
        
        # If we have a daily intervention limit, prioritize highest risk
        if max_interventions_per_day is not None:
            # Group by day and select top N highest risk per day
            high_risk['appointment_date'] = pd.to_datetime(high_risk['appointment_datetime']).dt.date
            
            # Sort by risk score within each date and select top N
            high_risk = high_risk.sort_values(['appointment_date', 'risk_score'], ascending=[True, False])
            high_risk = high_risk.groupby('appointment_date').head(max_interventions_per_day)
            
            print(f"Limited to {max_interventions_per_day} interventions per day")
            print(f"Selected {len(high_risk)} total appointments for intervention")
            
        # Apply intervention recommendations for each high-risk appointment
        interventions = []
        
        for idx, row in high_risk.iterrows():
            # Create risk factors dict for the intervention engine
            risk_factors = {
                'transport_score': row.get('transport_score', 5),  # Default if not available
                'lead_time': row.get('lead_time', 7),
                'ses_score': row.get('ses_score', 5)
            }
            
            # Get recommended interventions
            recommended = self.intervention_engine.match_interventions(row['risk_score'], risk_factors)
            
            # Optimize interventions based on ROI
            optimized = self.intervention_engine.optimize_interventions(
                row['risk_score'], risk_factors, budget=20  # $20 max budget per appointment
            )
            
            # Calculate the impact of interventions
            baseline_attendance_prob = 1 - row['risk_score']
            
            # Calculate combined intervention effectiveness
            combined_effectiveness = 0
            for intervention in optimized:
                # Use diminishing returns formula for multiple interventions
                remaining_risk = 1 - (baseline_attendance_prob + combined_effectiveness)
                intervention_impact = remaining_risk * intervention['effectiveness']
                combined_effectiveness += intervention_impact
                
            # Calculate new attendance probability
            new_attendance_prob = baseline_attendance_prob + combined_effectiveness
            
            # Calculate intervention cost
            total_cost = sum(intervention['cost'] for intervention in optimized)
            
            interventions.append({
                'appointment_id': row.get('appointment_id', idx),
                'risk_score': row['risk_score'],
                'baseline_attendance_prob': baseline_attendance_prob,
                'new_attendance_prob': new_attendance_prob,
                'improvement': combined_effectiveness,
                'intervention_cost': total_cost,
                'interventions': [i['type'] for i in optimized],
                'intervention_details': optimized
            })
            
        # Convert to DataFrame
        interventions_df = pd.DataFrame(interventions)
        
        # Merge back with original data
        result = result.merge(
            interventions_df[['appointment_id', 'baseline_attendance_prob', 'new_attendance_prob', 
                            'improvement', 'intervention_cost', 'interventions']], 
            on='appointment_id', how='left'
        )
        
        # Fill NaN values for non-intervened appointments
        result['baseline_attendance_prob'] = result['baseline_attendance_prob'].fillna(1 - result['risk_score'])
        result['new_attendance_prob'] = result['new_attendance_prob'].fillna(result['baseline_attendance_prob'])
        result['improvement'] = result['improvement'].fillna(0)
        result['intervention_cost'] = result['intervention_cost'].fillna(0)
        result['interventions'] = result['interventions'].fillna('[]').apply(
            lambda x: x if isinstance(x, list) else []
        )
        
        return result, interventions_df
    
    def calculate_roi(self, data=None, risk_thresholds=None, appointment_value=150):
        """
        Calculate ROI for different risk thresholds
        
        Parameters:
        -----------
        data : pandas.DataFrame, optional
            Data with risk predictions (if not provided, uses previously predicted data)
        risk_thresholds : list, optional
            Risk thresholds to evaluate (default: 0.3 to 0.9 by 0.1)
        appointment_value : float
            Average revenue per appointment
            
        Returns:
        --------
        pandas.DataFrame
            ROI metrics for each threshold
        """
        if risk_thresholds is None:
            risk_thresholds = np.arange(0.3, 1.0, 0.1)
            
        if data is None:
            data = self.predict_no_show_risks()
            
        print("Calculating ROI for different risk thresholds...")
        
        # Calculate ROI for each threshold
        results = []
        
        for threshold in risk_thresholds:
            # Apply interventions at this threshold
            intervened_data, _ = self.apply_interventions(data, risk_threshold=threshold)
            
            # Calculate financial impact
            n_appointments = len(intervened_data)
            n_interventions = (intervened_data['intervention_cost'] > 0).sum()
            
            # Calculate baseline no-shows
            baseline_no_shows = (intervened_data['risk_score'] >= 0.5).sum()
            
            # Calculate expected no-shows after intervention
            expected_no_shows = n_appointments - intervened_data['new_attendance_prob'].sum()
            
            # Calculate no-shows prevented
            prevented_no_shows = baseline_no_shows - expected_no_shows
            
            # Calculate costs and benefits
            total_intervention_cost = intervened_data['intervention_cost'].sum()
            revenue_gained = prevented_no_shows * appointment_value
            net_benefit = revenue_gained - total_intervention_cost
            
            # Calculate ROI
            roi = (net_benefit / total_intervention_cost) * 100 if total_intervention_cost > 0 else 0
            
            results.append({
                'risk_threshold': threshold,
                'appointments': n_appointments,
                'interventions': n_interventions,
                'baseline_no_shows': baseline_no_shows,
                'expected_no_shows': expected_no_shows,
                'prevented_no_shows': prevented_no_shows,
                'intervention_cost': total_intervention_cost,
                'revenue_gained': revenue_gained,
                'net_benefit': net_benefit,
                'roi_percent': roi
            })
            
        return pd.DataFrame(results)
    
    def visualize_roi(self, roi_data, output_dir=None):
        """
        Create visualizations of ROI analysis
        
        Parameters:
        -----------
        roi_data : pandas.DataFrame
            ROI metrics from calculate_roi method
        output_dir : str, optional
            Directory to save visualizations
        """
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # 1. ROI by threshold
        plt.figure(figsize=(12, 6))
        plt.plot(roi_data['risk_threshold'], roi_data['roi_percent'], marker='o', linewidth=2)
        plt.xlabel('Risk Threshold')
        plt.ylabel('ROI (%)')
        plt.title('Return on Investment by Risk Threshold')
        plt.grid(True, alpha=0.3)
        
        for i, row in roi_data.iterrows():
            plt.annotate(f"{row['roi_percent']:.1f}%", 
                         (row['risk_threshold'], row['roi_percent']),
                         textcoords="offset points", 
                         xytext=(0, 10),
                         ha='center')
            
        if output_dir:
            plt.savefig(os.path.join(output_dir, '01_roi_by_threshold.png'))
        plt.close()
        
        # 2. Costs and benefits
        plt.figure(figsize=(12, 6))
        x = roi_data['risk_threshold']
        width = 0.3
        
        plt.bar(x - width/2, roi_data['intervention_cost'], width, label='Intervention Cost')
        plt.bar(x + width/2, roi_data['revenue_gained'], width, label='Revenue Gained')
        
        plt.xlabel('Risk Threshold')
        plt.ylabel('Amount ($)')
        plt.title('Costs and Benefits by Risk Threshold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if output_dir:
            plt.savefig(os.path.join(output_dir, '02_costs_benefits.png'))
        plt.close()
        
        # 3. Net benefit
        plt.figure(figsize=(12, 6))
        plt.bar(roi_data['risk_threshold'], roi_data['net_benefit'], color='green')
        plt.xlabel('Risk Threshold')
        plt.ylabel('Net Benefit ($)')
        plt.title('Net Benefit by Risk Threshold')
        plt.grid(True, alpha=0.3)
        
        for i, row in roi_data.iterrows():
            plt.annotate(f"${row['net_benefit']:.0f}", 
                         (row['risk_threshold'], row['net_benefit']),
                         textcoords="offset points", 
                         xytext=(0, 10),
                         ha='center')
            
        if output_dir:
            plt.savefig(os.path.join(output_dir, '03_net_benefit.png'))
        plt.close()
        
        # 4. No-shows prevented
        plt.figure(figsize=(12, 6))
        plt.plot(roi_data['risk_threshold'], roi_data['prevented_no_shows'], marker='o', linewidth=2, color='purple')
        plt.xlabel('Risk Threshold')
        plt.ylabel('No-shows Prevented')
        plt.title('No-Shows Prevented by Risk Threshold')
        plt.grid(True, alpha=0.3)
        
        for i, row in roi_data.iterrows():
            plt.annotate(f"{row['prevented_no_shows']:.0f}", 
                         (row['risk_threshold'], row['prevented_no_shows']),
                         textcoords="offset points", 
                         xytext=(0, 10),
                         ha='center')
            
        if output_dir:
            plt.savefig(os.path.join(output_dir, '04_prevented_noshows.png'))
        plt.close()
        
        # 5. Intervention count
        plt.figure(figsize=(12, 6))
        plt.plot(roi_data['risk_threshold'], roi_data['interventions'], marker='o', linewidth=2, color='orange')
        plt.xlabel('Risk Threshold')
        plt.ylabel('Number of Interventions')
        plt.title('Intervention Count by Risk Threshold')
        plt.grid(True, alpha=0.3)
        
        for i, row in roi_data.iterrows():
            plt.annotate(f"{row['interventions']:.0f}", 
                         (row['risk_threshold'], row['interventions']),
                         textcoords="offset points", 
                         xytext=(0, 10),
                         ha='center')
            
        if output_dir:
            plt.savefig(os.path.join(output_dir, '05_intervention_count.png'))
        plt.close()
        
        print(f"Visualizations saved to {output_dir}" if output_dir else "Visualizations displayed")
    
    def generate_intervention_report(self, data=None, risk_threshold=0.5, output_dir=None):
        """
        Generate a detailed intervention report
        
        Parameters:
        -----------
        data : pandas.DataFrame, optional
            Data with risk predictions (if not provided, uses previously predicted data)
        risk_threshold : float
            Risk threshold for intervention
        output_dir : str, optional
            Directory to save report
            
        Returns:
        --------
        pandas.DataFrame
            Detailed intervention report
        """
        if data is None:
            data = self.predict_no_show_risks()
            
        # Apply interventions
        _, interventions_df = self.apply_interventions(data, risk_threshold=risk_threshold)
        
        if len(interventions_df) == 0:
            print("No interventions to report")
            return None
            
        # Analyze interventions
        intervention_types = []
        for interventions in interventions_df['interventions']:
            intervention_types.extend(interventions)
            
        intervention_counts = pd.Series(intervention_types).value_counts()
        
        # Create a summary report
        summary = pd.DataFrame({
            'intervention_type': intervention_counts.index,
            'count': intervention_counts.values,
            'percentage': intervention_counts.values / len(interventions_df) * 100
        })
        
        # Print summary
        print("\nIntervention Summary:")
        print(summary)
        
        # Save report if output_dir provided
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
            # Save intervention details
            interventions_df.to_csv(os.path.join(output_dir, 'intervention_details.csv'), index=False)
            
            # Save summary
            summary.to_csv(os.path.join(output_dir, 'intervention_summary.csv'), index=False)
            
            # Create visualization of intervention types
            plt.figure(figsize=(10, 6))
            plt.bar(summary['intervention_type'], summary['count'])
            plt.xlabel('Intervention Type')
            plt.ylabel('Count')
            plt.title('Intervention Types Distribution')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'intervention_types.png'))
            plt.close()
            
            print(f"Intervention report saved to {output_dir}")
            
        return interventions_df, summary
    
    def run_full_analysis(self, risk_threshold=0.5, appointment_value=150, output_dir=None):
        """
        Run a complete ROI analysis and generate reports/visualizations
        
        Parameters:
        -----------
        risk_threshold : float
            Risk threshold for intervention
        appointment_value : float
            Average revenue per appointment
        output_dir : str, optional
            Directory to save outputs
            
        Returns:
        --------
        dict
            Analysis results
        """
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        # Timestamp for reports
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print("\n===== VitalSchedule ROI Analysis =====")
        print(f"Risk Threshold: {risk_threshold}")
        print(f"Appointment Value: ${appointment_value}")
        print(f"Analysis Date: {timestamp}")
        
        # Step 1: Generate predictions
        data = self.predict_no_show_risks()
        
        # Step 2: Apply interventions at the specified threshold
        intervened_data, intervention_details = self.apply_interventions(data, risk_threshold=risk_threshold)
        
        # Step 3: Calculate ROI for different thresholds
        roi_data = self.calculate_roi(data, appointment_value=appointment_value)
        
        # Step 4: Generate visualizations
        if output_dir:
            viz_dir = os.path.join(output_dir, 'visualizations')
            self.visualize_roi(roi_data, viz_dir)
            
        # Step 5: Generate intervention report
        intervention_report, summary = self.generate_intervention_report(
            data, risk_threshold, os.path.join(output_dir, 'reports') if output_dir else None
        )
        
        # Step 6: Calculate overall financial impact
        selected_roi = roi_data[roi_data['risk_threshold'] == risk_threshold].iloc[0] if len(roi_data) > 0 else None
        
        # Create summary report
        if output_dir:
            with open(os.path.join(output_dir, 'analysis_summary.txt'), 'w') as f:
                f.write("VitalSchedule ROI Analysis Summary\n")
                f.write("=================================\n\n")
                f.write(f"Analysis Date: {timestamp}\n")
                f.write(f"Risk Threshold: {risk_threshold}\n")
                f.write(f"Appointment Value: ${appointment_value}\n\n")
                
                f.write("Dataset Overview:\n")
                f.write(f"  Total Appointments: {len(data)}\n")
                f.write(f"  Average Risk Score: {data['risk_score'].mean():.2%}\n")
                f.write(f"  High-Risk Appointments: {(data['risk_score'] >= risk_threshold).sum()} ({(data['risk_score'] >= risk_threshold).mean():.2%})\n\n")
                
                if selected_roi is not None:
                    f.write("Financial Impact:\n")
                    f.write(f"  Interventions Applied: {selected_roi['interventions']}\n")
                    f.write(f"  Total Intervention Cost: ${selected_roi['intervention_cost']:.2f}\n")
                    f.write(f"  Expected Revenue Gained: ${selected_roi['revenue_gained']:.2f}\n")
                    f.write(f"  Net Benefit: ${selected_roi['net_benefit']:.2f}\n")
                    f.write(f"  Return on Investment: {selected_roi['roi_percent']:.1f}%\n\n")
                
                f.write("Top Intervention Types:\n")
                for i, row in summary.head(3).iterrows():
                    f.write(f"  {row['intervention_type']}: {row['count']} ({row['percentage']:.1f}%)\n")
                    
                f.write("\nRecommendations:\n")
                
                if selected_roi is not None and selected_roi['roi_percent'] > 0:
                    f.write("  - Implement the intervention strategy as it shows positive ROI\n")
                    
                    # Find optimal threshold
                    optimal_threshold = roi_data.loc[roi_data['roi_percent'].idxmax(), 'risk_threshold']
                    f.write(f"  - Consider adjusting risk threshold to {optimal_threshold} for optimal ROI\n")
                    
                    # Additional recommendations based on data
                    if selected_roi['prevented_no_shows'] / selected_roi['baseline_no_shows'] < 0.5:
                        f.write("  - Explore additional intervention types to increase effectiveness\n")
                else:
                    f.write("  - The current intervention strategy does not show positive ROI\n")
                    f.write("  - Reevaluate intervention costs or target higher risk appointments\n")
        
        # Return analysis results
        return {
            'data': intervened_data,
            'roi_data': roi_data,
            'intervention_details': intervention_details,
            'summary': summary,
            'selected_roi': selected_roi
        }

def main():
    """
    Main function to run ROI analysis
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Run ROI Analysis for VitalSchedule')
    parser.add_argument('--model', required=True, help='Path to trained model file')
    parser.add_argument('--data', required=True, help='Path to appointment data file')
    parser.add_argument('--threshold', type=float, default=0.5, help='Risk threshold for interventions')
    parser.add_argument('--value', type=float, default=150, help='Average revenue per appointment')
    parser.add_argument('--output', help='Output directory for results')
    
    args = parser.parse_args()
    
    # Create output directory if specified
    if args.output:
        os.makedirs(args.output, exist_ok=True)
    
    # Run analysis
    analyzer = NoShowROIAnalyzer(args.model, args.data)
    results = analyzer.run_full_analysis(args.threshold, args.value, args.output)
    
    print("\nAnalysis complete!")
    
if __name__ == "__main__":
    main()
