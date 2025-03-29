import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def display_complexity_distribution(patient_data):
    """
    Display patient complexity score distribution
    """
    if patient_data is None or 'complexity_score' not in patient_data.columns:
        st.warning("Complexity score data not available")
        return
    
    st.subheader("Patient Complexity Distribution")
    
    # Create histogram of complexity scores
    fig = px.histogram(
        patient_data,
        x='complexity_score',
        nbins=30,
        title="Distribution of Complexity Scores",
        labels={'complexity_score': 'Complexity Score'},
        color_discrete_sequence=['#3366CC']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display complexity tier distribution if available
    if 'complexity_tier' in patient_data.columns:
        # Count by tier
        tier_counts = patient_data['complexity_tier'].value_counts().reset_index()
        tier_counts.columns = ['Tier', 'Count']
        
        # Define tier order
        if set(tier_counts['Tier']) == set(['Low', 'Medium', 'High']):
            tier_counts['Tier'] = pd.Categorical(
                tier_counts['Tier'],
                categories=['Low', 'Medium', 'High'],
                ordered=True
            )
            tier_counts = tier_counts.sort_values('Tier')
        
        # Create pie chart
        fig = px.pie(
            tier_counts,
            names='Tier',
            values='Count',
            title="Patient Distribution by Complexity Tier",
            color='Tier',
            color_discrete_map={
                'Low': 'green',
                'Medium': 'gold',
                'High': 'firebrick'
            }
        )
        
        fig.update_traces(textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)

def display_model_performance(model_results):
    """
    Display model performance metrics
    """
    if model_results is None or 'summary' not in model_results:
        st.warning("Model performance data not available")
        return
    
    st.subheader("Predictive Model Performance")
    
    summary_df = model_results['summary']
    
    # Create bar chart of AUC scores
    fig = px.bar(
        summary_df,
        x='event',
        y=['roc_auc', 'pr_auc'],
        barmode='group',
        title="Model Performance Metrics",
        labels={
            'event': 'Event Type',
            'value': 'AUC Score',
            'variable': 'Metric'
        },
        color_discrete_map={
            'roc_auc': '#3366CC',
            'pr_auc': '#DC3912'
        }
    )
    
    # Format event names for better display
    fig.update_xaxes(type='category', 
                     categoryorder='array', 
                     categoryarray=summary_df['event'])
    
    # Add a horizontal line at 0.5 (random classifier baseline)
    fig.add_shape(
        type='line',
        x0=-0.5,
        x1=len(summary_df['event'])-0.5,
        y0=0.5,
        y1=0.5,
        line=dict(color='red', width=2, dash='dot')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_feature_importance(model_results):
    """
    Display feature importance visualization
    """
    if model_results is None:
        st.warning("Model results not available")
        return
    
    # Find all models with feature importance data
    models_with_importance = [key.replace('_importance', '') for key in model_results.keys() 
                             if key.endswith('_importance')]
    
    if not models_with_importance:
        st.warning("Feature importance data not available")
        return
    
    st.subheader("Feature Importance Analysis")
    
    # Let user select model
    selected_model = st.selectbox(
        "Select model:",
        models_with_importance,
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    # Get feature importance for selected model
    importance_key = f'{selected_model}_importance'
    if importance_key in model_results:
        importance_df = model_results[importance_key]
        
        # Sort by importance and take top 10
        importance_df = importance_df.sort_values('importance', ascending=False).head(10)
        
        # Create horizontal bar chart
        fig = px.bar(
            importance_df,
            y='feature',
            x='importance',
            orientation='h',
            title=f"Top Features for {selected_model.replace('_', ' ').title()} Model",
            labels={'feature': 'Feature', 'importance': 'Importance'},
            color='importance',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Feature importance data not available for {selected_model}")

def display_risk_stratification(patient_data):
    """
    Display risk stratification analysis
    """
    if patient_data is None or 'complexity_score' not in patient_data.columns:
        return
    
    st.subheader("Patient Risk Stratification")
    
    # Calculate risk percentiles
    patient_data['risk_percentile'] = pd.qcut(
        patient_data['complexity_score'], 
        q=100, 
        labels=False
    )
    
    # Create risk tiers
    risk_tiers = pd.cut(
        patient_data['risk_percentile'],
        bins=[0, 49, 74, 89, 99],
        labels=['Low Risk (0-50%)', 'Medium Risk (50-75%)', 'High Risk (75-90%)', 'Very High Risk (90-100%)']
    )
    
    # Count patients in each tier
    tier_counts = risk_tiers.value_counts().reset_index()
    tier_counts.columns = ['Risk Tier', 'Count']
    
    # Sort tiers in proper order
    tier_order = ['Low Risk (0-50%)', 'Medium Risk (50-75%)', 'High Risk (75-90%)', 'Very High Risk (90-100%)']
    tier_counts['Risk Tier'] = pd.Categorical(
        tier_counts['Risk Tier'],
        categories=tier_order,
        ordered=True
    )
    tier_counts = tier_counts.sort_values('Risk Tier')
    
    # Create bar chart
    fig = px.bar(
        tier_counts,
        x='Risk Tier',
        y='Count',
        title="Patient Distribution by Risk Tier",
        labels={'Risk Tier': 'Risk Tier', 'Count': 'Number of Patients'},
        color='Risk Tier',
        color_discrete_map={
            'Low Risk (0-50%)': 'green',
            'Medium Risk (50-75%)': 'gold',
            'High Risk (75-90%)': 'orange',
            'Very High Risk (90-100%)': 'red'
        }
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add readmission rates by risk tier if available
    if 'readmission_flag' in patient_data.columns:
        readmission_by_tier = patient_data.groupby(risk_tiers)['readmission_flag'].mean() * 100
        readmission_by_tier = readmission_by_tier.reset_index()
        readmission_by_tier.columns = ['Risk Tier', 'Readmission Rate (%)']
        
        # Sort tiers in proper order
        readmission_by_tier['Risk Tier'] = pd.Categorical(
            readmission_by_tier['Risk Tier'],
            categories=tier_order,
            ordered=True
        )
        readmission_by_tier = readmission_by_tier.sort_values('Risk Tier')
        
        # Create bar chart
        fig = px.bar(
            readmission_by_tier,
            x='Risk Tier',
            y='Readmission Rate (%)',
            title="Readmission Rate by Risk Tier",
            labels={'Risk Tier': 'Risk Tier', 'Readmission Rate (%)': 'Readmission Rate (%)'},
            color='Risk Tier',
            color_discrete_map={
                'Low Risk (0-50%)': 'green',
                'Medium Risk (50-75%)': 'gold',
                'High Risk (75-90%)': 'orange',
                'Very High Risk (90-100%)': 'red'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_interventions(model_results, selected_risk_tier=None):
    """
    Display intervention recommendations
    """
    if model_results is None:
        return
    
    # Find models with intervention data
    models_with_interventions = [key.replace('_interventions', '') for key in model_results.keys() 
                               if key.endswith('_interventions')]
    
    if not models_with_interventions:
        return
    
    st.subheader("Recommended Interventions")
    
    # Let user select model
    selected_model = st.selectbox(
        "Select event type:",
        models_with_interventions,
        format_func=lambda x: x.replace('_', ' ').title(),
        key="intervention_model_select"
    )
    
    # Get interventions for selected model
    intervention_key = f'{selected_model}_interventions'
    if intervention_key in model_results:
        interventions_df = model_results[intervention_key]
        
        # Filter interventions based on risk tier if provided
        filtered_interventions = interventions_df
        
        # Display interventions as a table
        st.subheader(f"Interventions for {selected_model.replace('_', ' ').title()}")
        
        # Format the table
        if 'category' in filtered_interventions.columns and 'description' in filtered_interventions.columns:
            display_df = filtered_interventions[['category', 'description']]
            display_df.columns = ['Intervention Category', 'Description']
            st.table(display_df)
        else:
            st.dataframe(filtered_interventions)
        
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

def display_prediction_thresholds(patient_data):
    """
    Allow users to set prediction thresholds and see impact
    """
    if patient_data is None or 'complexity_score' not in patient_data.columns:
        return
    
    st.subheader("Threshold Analysis Tool")
    
    # Create complexity score threshold slider
    threshold = st.slider(
        "Complexity Score Threshold:", 
        min_value=float(patient_data['complexity_score'].min()), 
        max_value=float(patient_data['complexity_score'].max()),
        value=float(patient_data['complexity_score'].quantile(0.75)),
        step=0.01,
        key="complexity_threshold"
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

def display_models_dashboard(patient_data, model_results):
    """
    Display the predictive models dashboard section
    """
    st.header("Predictive Models & Risk Stratification")
    
    # Display complexity score distribution
    display_complexity_distribution(patient_data)
    
    # Display model performance
    display_model_performance(model_results)
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        # Display feature importance
        display_feature_importance(model_results)
    
    with col2:
        # Display risk stratification
        display_risk_stratification(patient_data)
    
    # Display intervention recommendations
    display_interventions(model_results)
    
    # Display prediction threshold tool
    display_prediction_thresholds(patient_data)
