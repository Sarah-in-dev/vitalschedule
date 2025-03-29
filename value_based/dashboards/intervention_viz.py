import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def display_intervention_recommendations(model_results):
    """
    Display intervention recommendations from predictive models
    """
    if model_results is None:
        st.warning("Model results not available")
        return
    
    # Find models with intervention data
    models_with_interventions = [key.replace('_interventions', '') for key in model_results.keys() 
                                if key.endswith('_interventions')]
    
    if not models_with_interventions:
        st.warning("Intervention recommendations not available")
        return
    
    st.subheader("Intervention Recommendations")
    
    # Let user select model
    selected_model = st.selectbox(
        "Select event type:",
        models_with_interventions,
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    # Get interventions for selected model
    intervention_key = f'{selected_model}_interventions'
    if intervention_key in model_results:
        interventions_df = model_results[intervention_key]
        
        # Display interventions as a table
        if 'category' in interventions_df.columns and 'description' in interventions_df.columns:
            display_df = interventions_df[['category', 'description']]
            display_df.columns = ['Intervention Category', 'Description']
            
            # Format table
            st.table(display_df)
        else:
            st.dataframe(interventions_df)
        
        # Show feature importance if available
        importance_key = f'{selected_model}_importance'
        if importance_key in model_results:
            st.subheader("Related Key Factors")
            
            importance_df = model_results[importance_key]
            importance_df = importance_df.sort_values('importance', ascending=False).head(5)
            
            # Create horizontal bar chart
            fig = px.bar(
                importance_df,
                y='feature',
                x='importance',
                orientation='h',
                title=f"Top 5 Factors for {selected_model.replace('_', ' ').title()}",
                labels={'feature': 'Factor', 'importance': 'Importance'},
                color='importance',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(yaxis={'categoryorder': 'total ascending'})
            
            st.plotly_chart(fig, use_container_width=True)

def display_risk_threshold_tool(patient_data):
    """
    Interactive tool to identify high-risk patients based on threshold
    """
    if patient_data is None or 'complexity_score' not in patient_data.columns:
        return
    
    st.subheader("Risk Stratification Tool")
    
    st.markdown("""
    This tool allows you to set a complexity score threshold and identify high-risk patients 
    who would benefit from targeted interventions.
    """)
    
    # Create slider for complexity score threshold
    threshold = st.slider(
        "Complexity Score Threshold:",
        min_value=float(patient_data['complexity_score'].min()),
        max_value=float(patient_data['complexity_score'].max()),
        value=float(patient_data['complexity_score'].quantile(0.75)),
        step=0.01
    )
    
    # Calculate high-risk patients based on threshold
    high_risk_count = (patient_data['complexity_score'] >= threshold).sum()
    total_patients = len(patient_data)
    high_risk_percentage = (high_risk_count / total_patients) * 100
    
    # Display metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "High-Risk Patients", 
            f"{high_risk_count:,}", 
            f"{high_risk_percentage:.1f}% of population"
        )
    
    with col2:
        if 'readmission_flag' in patient_data.columns:
            # Calculate readmission metrics
            overall_readmission_rate = patient_data['readmission_flag'].mean() * 100
            high_risk_readmission_rate = patient_data[patient_data['complexity_score'] >= threshold]['readmission_flag'].mean() * 100
            readmission_difference = high_risk_readmission_rate - overall_readmission_rate
            
            st.metric(
                "Readmission Rate in High-Risk Group", 
                f"{high_risk_readmission_rate:.1f}%", 
                f"{readmission_difference:+.1f}% vs. overall"
            )
    
    # Display characteristics of high-risk group
    if high_risk_count > 0:
        st.subheader("High-Risk Group Characteristics")
        
        high_risk_df = patient_data[patient_data['complexity_score'] >= threshold]
        
        # Calculate key metrics for comparison
        metrics = []
        
        if 'unique_chronic_conditions' in patient_data.columns:
            metrics.append({
                'Metric': 'Avg. Chronic Conditions',
                'High-Risk Group': high_risk_df['unique_chronic_conditions'].mean(),
                'All Patients': patient_data['unique_chronic_conditions'].mean()
            })
        
        if 'unique_medication_count' in patient_data.columns:
            metrics.append({
                'Metric': 'Avg. Medications',
                'High-Risk Group': high_risk_df['unique_medication_count'].mean(),
                'All Patients': patient_data['unique_medication_count'].mean()
            })
        
        if 'admission_count' in patient_data.columns:
            metrics.append({
                'Metric': 'Avg. Admissions',
                'High-Risk Group': high_risk_df['admission_count'].mean(),
                'All Patients': patient_data['admission_count'].mean()
            })
        
        if 'emergency_count' in patient_data.columns:
            metrics.append({
                'Metric': 'Avg. ED Visits',
                'High-Risk Group': high_risk_df['emergency_count'].mean(),
                'All Patients': patient_data['emergency_count'].mean()
            })
        
        if 'clinical_severity_score' in patient_data.columns:
            metrics.append({
                'Metric': 'Avg. Clinical Severity',
                'High-Risk Group': high_risk_df['clinical_severity_score'].mean(),
                'All Patients': patient_data['clinical_severity_score'].mean()
            })
        
        # Create comparison chart
        if metrics:
            metrics_df = pd.DataFrame(metrics)
            
            fig = px.bar(
                metrics_df,
                x='Metric',
                y=['High-Risk Group', 'All Patients'],
                barmode='group',
                title="Comparison of High-Risk Group vs. All Patients",
                labels={'value': 'Value', 'variable': 'Group'},
                color_discrete_map={
                    'High-Risk Group': 'firebrick',
                    'All Patients': 'royalblue'
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Display sample of high-risk patients
        st.subheader("Sample High-Risk Patients")
        
        # Select columns to display
        display_cols = ['subject_id']
        
        if 'age_group' in high_risk_df.columns:
            display_cols.append('age_group')
        
        if 'gender' in high_risk_df.columns:
            display_cols.append('gender')
        
        if 'unique_chronic_conditions' in high_risk_df.columns:
            display_cols.append('unique_chronic_conditions')
        
        if 'unique_medication_count' in high_risk_df.columns:
            display_cols.append('unique_medication_count')
        
        if 'admission_count' in high_risk_df.columns:
            display_cols.append('admission_count')
        
        if 'emergency_count' in high_risk_df.columns:
            display_cols.append('emergency_count')
        
        if 'complexity_score' in high_risk_df.columns:
            display_cols.append('complexity_score')
        
        # Display sample of highest-risk patients
        sample_size = min(10, high_risk_count)
        sample_df = high_risk_df.sort_values('complexity_score', ascending=False).head(sample_size)
        
        st.dataframe(sample_df[display_cols])
        
        st.info(f"Showing top {sample_size} of {high_risk_count} high-risk patients")

def calculate_intervention_roi(patient_data):
    """
    Calculate potential ROI of interventions
    """
    if patient_data is None or 'complexity_score' not in patient_data.columns:
        return
    
    st.subheader("Intervention Cost-Effectiveness Analysis")
    
    st.markdown("""
    This analysis estimates the potential return on investment (ROI) for implementing 
    targeted interventions based on risk stratification.
    """)
    
    # Allow user to set parameters
    st.markdown("### Cost and Effectiveness Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Intervention costs
        st.markdown("#### Intervention Costs ($ per patient)")
        low_risk_cost = st.number_input("Low-risk intervention cost", value=500, step=100)
        medium_risk_cost = st.number_input("Medium-risk intervention cost", value=1500, step=100)
        high_risk_cost = st.number_input("High-risk intervention cost", value=4000, step=100)
    
    with col2:
        # Intervention effectiveness
        st.markdown("#### Intervention Effectiveness (% reduction)")
        low_risk_effect = st.slider("Low-risk effectiveness", min_value=0, max_value=30, value=10, step=5)
        medium_risk_effect = st.slider("Medium-risk effectiveness", min_value=0, max_value=50, value=20, step=5) 
        high_risk_effect = st.slider("High-risk effectiveness", min_value=0, max_value=70, value=30, step=5)
    
    # Set event costs
    st.markdown("### Event Costs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        readmission_cost = st.number_input("Cost per readmission ($)", value=15000, step=1000)
    
    with col2:
        ed_visit_cost = st.number_input("Cost per ED visit ($)", value=3000, step=500)
    
    # Calculate ROI
    
    # Create risk tiers if not already present
    if 'complexity_tier' not in patient_data.columns:
        # Create temporary risk tiers based on percentiles
        patient_data['temp_tier'] = pd.qcut(
            patient_data['complexity_score'], 
            q=[0, 0.5, 0.85, 1.0], 
            labels=['Low', 'Medium', 'High']
        )
        tier_column = 'temp_tier'
    else:
        tier_column = 'complexity_tier'
    
    # Set intervention parameters by tier
    intervention_costs = {
        'Low': low_risk_cost,
        'Medium': medium_risk_cost,
        'High': high_risk_cost
    }
    
    intervention_effects = {
        'Low': low_risk_effect / 100,  # Convert to proportion
        'Medium': medium_risk_effect / 100,
        'High': high_risk_effect / 100
    }
    
    # Calculate for each tier
    results = []
    
    for tier in ['Low', 'Medium', 'High']:
        tier_data = patient_data[patient_data[tier_column] == tier]
        
        if len(tier_data) == 0:
            continue
        
        # Number of patients in tier
        patient_count = len(tier_data)
        
        # Expected events without intervention
        readmission_count = 0
        readmission_rate = 0
        if 'readmission_flag' in tier_data.columns:
            readmission_rate = tier_data['readmission_flag'].mean()
            readmission_count = readmission_rate * patient_count
        
        ed_visit_count = 0
        if 'emergency_count' in tier_data.columns:
            ed_visit_count = tier_data['emergency_count'].sum()
        
        # Cost of events without intervention
        event_cost_without = (readmission_count * readmission_cost) + (ed_visit_count * ed_visit_cost)
        
        # Effect of intervention
        effect = intervention_effects[tier]
        
        # Expected events with intervention
        readmission_count_with = readmission_count * (1 - effect)
        ed_visit_count_with = ed_visit_count * (1 - effect)
        
        # Cost of events with intervention
        event_cost_with = (readmission_count_with * readmission_cost) + (ed_visit_count_with * ed_visit_cost)
        
        # Cost of intervention
        intervention_cost = patient_count * intervention_costs[tier]
        
        # Savings from intervention
        savings = event_cost_without - event_cost_with
        
        # Net benefit
        net_benefit = savings - intervention_cost
        
        # ROI
        roi = (savings / intervention_cost - 1) * 100 if intervention_cost > 0 else 0
        
        # Add to results
        results.append({
            'Risk Tier': tier,
            'Patient Count': patient_count,
            'Readmission Rate': readmission_rate * 100,
            'Intervention Cost': intervention_cost,
            'Expected Savings': savings,
            'Net Benefit': net_benefit,
            'ROI (%)': roi
        })
    
    # Display results
    results_df = pd.DataFrame(results)
    
    # Calculate total/average across all tiers
    if len(results_df) > 0:
        total_row = {
            'Risk Tier': 'Total',
            'Patient Count': results_df['Patient Count'].sum(),
            'Readmission Rate': (results_df['Readmission Rate'] * results_df['Patient Count']).sum() / results_df['Patient Count'].sum(),
            'Intervention Cost': results_df['Intervention Cost'].sum(),
            'Expected Savings': results_df['Expected Savings'].sum(),
            'Net Benefit': results_df['Net Benefit'].sum(),
            'ROI (%)': results_df['Expected Savings'].sum() / results_df['Intervention Cost'].sum() * 100 - 100 if results_df['Intervention Cost'].sum() > 0 else 0
        }
        
        results_df = results_df.append(total_row, ignore_index=True)
        
        # Format and display table
        st.subheader("Cost-Benefit Analysis by Risk Tier")
        
        # Format the display table
        display_df = results_df.copy()
        display_df['Readmission Rate'] = display_df['Readmission Rate'].round(1).astype(str) + '%'
        display_df['Intervention Cost'] = display_df['Intervention Cost'].map('${:,.0f}'.format)
        display_df['Expected Savings'] = display_df['Expected Savings'].map('${:,.0f}'.format)
        display_df['Net Benefit'] = display_df['Net Benefit'].map('${:,.0f}'.format)
        display_df['ROI (%)'] = display_df['ROI (%)'].round(1).astype(str) + '%'
        
        st.table(display_df)
        
        # Create visualizations
        
        # ROI by tier
        fig = px.bar(
            results_df[results_df['Risk Tier'] != 'Total'],
            x='Risk Tier',
            y='ROI (%)',
            title="Return on Investment by Risk Tier",
            labels={'ROI (%)': 'ROI (%)', 'Risk Tier': 'Risk Tier'},
            color='Risk Tier',
            color_discrete_map={
                'Low': 'green',
                'Medium': 'gold',
                'High': 'firebrick'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Cost vs. savings
        fig = px.bar(
            results_df[results_df['Risk Tier'] != 'Total'],
            x='Risk Tier',
            y=['Intervention Cost', 'Expected Savings'],
            title="Intervention Costs vs. Expected Savings by Risk Tier",
            barmode='group',
            labels={'value': 'Amount ($)', 'variable': 'Category', 'Risk Tier': 'Risk Tier'},
            color_discrete_map={
                'Intervention Cost': 'darkred',
                'Expected Savings': 'darkgreen'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for ROI calculation")

def display_intervention_dashboard(patient_data, model_results):
    """
    Display the intervention recommendations dashboard section
    """
    st.header("Intervention Planning")
    
    # Display intervention recommendations
    display_intervention_recommendations(model_results)
    
    # Display risk threshold tool
    display_risk_threshold_tool(patient_data)
    
    # Calculate intervention ROI
    calculate_intervention_roi(patient_data)
