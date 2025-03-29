import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
import plotly.graph_objects as go

# Import visualization modules
from data_loaders import load_patient_data, load_model_results, prepare_filter_options, filter_patient_data
from demographic_viz import display_demographic_dashboard
from condition_viz import display_conditions_dashboard
from utilization_viz import display_utilization_dashboard
from model_viz import display_models_dashboard
from intervention_viz import display_intervention_dashboard
from aws_utils import AWSDataConnector

# Set page configuration
st.set_page_config(
    page_title="Value-Based Care Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Page title and description
    st.title("Value-Based Care Analytics Dashboard")
    
    st.markdown("""
    This dashboard visualizes data from the Value-Based Care analytics pipeline, 
    which processes MIMIC-IV data to identify high-risk patients and recommend interventions.
    """)
    
    # Sidebar for navigation and filters
    st.sidebar.title("Navigation")
    
    # Data source selection
    with st.sidebar.expander("Data Source", expanded=False):
        # AWS vs Local data source
        data_source = st.radio(
            "Select Data Source:",
            ["AWS S3", "Local Files"],
            index=0  # Default to AWS
        )
        
        if data_source == "AWS S3":
            # AWS organization name
            org_name = st.text_input(
                "Organization Name",
                value="predictiverx",
                key="org_name"
            )
            
            # Create AWS connector
            aws_connector = AWSDataConnector(org_name=org_name)
            
            use_aws = True
            data_dir = None
            models_dir = None
        else:
            # Local file paths
            data_dir = st.text_input(
                "Processed Data Directory",
                value="~/vitalschedule/value_based/processed_data",
                key="data_dir"
            )
            
            models_dir = st.text_input(
                "Models Directory",
                value="~/vitalschedule/value_based/models",
                key="models_dir"
            )
            
            # Expand paths if needed
            data_dir = os.path.expanduser(data_dir)
            models_dir = os.path.expanduser(models_dir)
            
            use_aws = False
            aws_connector = None
    
    # Load data
    with st.spinner("Loading data..."):
        if use_aws:
            patient_data = load_patient_data(use_aws=True, aws_connector=aws_connector)
            model_results = load_model_results(use_aws=True, aws_connector=aws_connector)
        else:
            patient_data = load_patient_data(data_dir=data_dir, use_aws=False)
            model_results = load_model_results(models_dir=models_dir, use_aws=False)
    
    if patient_data is None:
        if use_aws:
            st.error(f"Could not load patient data from AWS S3")
            st.info("Please check your AWS credentials and bucket names.")
        else:
            st.error(f"Could not load patient data from {data_dir}")
            st.info("Please check the data directory path and ensure the required files exist.")
        return
    
    # Data summary
    with st.expander("Data Summary", expanded=False):
        st.write(f"Loaded {len(patient_data)} patient records")
        st.write(f"Available columns: {', '.join(patient_data.columns)}")
        
        if model_results:
            st.write(f"Loaded model results: {', '.join(model_results.keys())}")
    
    # Prepare filter options
    filter_options = prepare_filter_options(patient_data)
    
    # Sidebar filters
    st.sidebar.title("Filters")
    
    # Create filters based on available data
    selected_filters = {}
    
    # Age group filter
    if 'age_groups' in filter_options:
        selected_filters['age_group'] = st.sidebar.multiselect(
            "Age Group",
            options=filter_options['age_groups'],
            default=[]
        )
    
    # Gender filter
    if 'genders' in filter_options:
        selected_filters['gender'] = st.sidebar.multiselect(
            "Gender",
            options=filter_options['genders'],
            default=[]
        )
    
    # Chronic condition filter
    if 'chronic_conditions' in filter_options:
        selected_filters['conditions'] = st.sidebar.multiselect(
            "Chronic Conditions",
            options=[cond.replace('_', ' ').title() for cond in filter_options['chronic_conditions']],
            default=[]
        )
        # Convert back to column names
        if selected_filters['conditions']:
            selected_filters['conditions'] = [cond.replace(' ', '_').lower() 
                                            for cond in selected_filters['conditions']]
    
    # Complexity tier filter
    if 'complexity_tiers' in filter_options:
        selected_filters['complexity_tier'] = st.sidebar.multiselect(
            "Complexity Tier",
            options=filter_options['complexity_tiers'],
            default=[]
        )
    
    # Apply filters
    filtered_data = filter_patient_data(patient_data, selected_filters)
    
    # Display filter summary
    if filtered_data is not None and len(filtered_data) < len(patient_data):
        st.info(f"Showing {len(filtered_data)} patients out of {len(patient_data)} total")
    
    # Navigation tabs
    page = st.sidebar.radio(
        "Select Page",
        ["Overview", "Demographics", "Chronic Conditions", 
         "Healthcare Utilization", "Predictive Models", "Interventions"]
    )
    
    # Display the selected page
    if page == "Overview":
        display_overview(patient_data, filtered_data, model_results)
    elif page == "Demographics":
        display_demographic_dashboard(patient_data, filtered_data)
    elif page == "Chronic Conditions":
        display_conditions_dashboard(patient_data, filtered_data)
    elif page == "Healthcare Utilization":
        display_utilization_dashboard(patient_data, filtered_data)
    elif page == "Predictive Models":
        display_models_dashboard(patient_data if filtered_data is None else filtered_data, model_results)
    elif page == "Interventions":
        display_intervention_dashboard(patient_data if filtered_data is None else filtered_data, model_results)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        "This dashboard visualizes the Value-Based Care analytics pipeline results. "
        "It provides insights into patient demographics, chronic conditions, risk profiles, "
        "and recommended interventions for high-risk patients."
    )
    
    # Add CSS for better styling
    st.markdown("""
    <style>
        .reportview-container .main .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #2c3e50;
        }
        h2, h3 {
            color: #34495e;
        }
        .stMetric {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        }
        .stMetric label {
            color: #7f8c8d;
        }
        .stMetric .metric-value {
            font-weight: bold;
            color: #2c3e50;
        }
        .aws-connected {
            color: #27ae60;
            font-weight: bold;
        }
        .local-connected {
            color: #2980b9;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

def display_overview(patient_data, filtered_data, model_results):
    """
    Display overview dashboard with key metrics
    """
    # Use filtered data if available, otherwise use all data
    data_to_use = filtered_data if filtered_data is not None else patient_data
    
    # Key metrics in a row
    st.subheader("Population Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Patients", f"{len(data_to_use):,}")
    
    with col2:
        if 'unique_chronic_conditions' in data_to_use.columns:
            avg_conditions = data_to_use['unique_chronic_conditions'].mean()
            st.metric("Avg. Chronic Conditions", f"{avg_conditions:.1f}")
    
    with col3:
        if 'complexity_score' in data_to_use.columns:
            avg_complexity = data_to_use['complexity_score'].mean()
            st.metric("Avg. Complexity Score", f"{avg_complexity:.2f}")
    
    with col4:
        if 'readmission_flag' in data_to_use.columns:
            readmission_rate = data_to_use['readmission_flag'].mean() * 100
            st.metric("Readmission Rate", f"{readmission_rate:.1f}%")
    
    # Demographics summary
    st.subheader("Demographic Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Age distribution
        if 'age_group' in data_to_use.columns:
            age_counts = data_to_use['age_group'].value_counts().reset_index()
            age_counts.columns = ['Age Group', 'Count']
            
            # Sort the age groups in correct order
            age_order = ['0-18', '19-35', '36-50', '51-65', '66-80', '80+']
            
            # Check if the age groups match our expected format
            if all(age in age_order for age in age_counts['Age Group']):
                age_counts['Age Group'] = pd.Categorical(
                    age_counts['Age Group'],
                    categories=age_order,
                    ordered=True
                )
                age_counts = age_counts.sort_values('Age Group')
            
            fig = px.bar(
                age_counts, 
                x='Age Group', 
                y='Count',
                title="Patient Distribution by Age Group",
                color='Age Group',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gender distribution
        if 'gender' in data_to_use.columns:
            gender_counts = data_to_use['gender'].value_counts().reset_index()
            gender_counts.columns = ['Gender', 'Count']
            
            fig = px.pie(
                gender_counts, 
                names='Gender', 
                values='Count',
                title="Patient Distribution by Gender",
                color='Gender',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            fig.update_traces(textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Chronic conditions summary
    st.subheader("Chronic Conditions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Display top conditions if available
        condition_cols = [col for col in data_to_use.columns if col in [
            'hypertension', 'diabetes', 'chf', 'copd', 'ckd', 
            'liver_disease', 'cancer', 'depression', 'dementia'
        ]]
        
        if condition_cols:
            # Calculate prevalence for each condition
            prevalence_data = []
            for col in condition_cols:
                if col in data_to_use.columns:
                    prevalence = data_to_use[col].mean() * 100
                    prevalence_data.append({
                        'Condition': col.replace('_', ' ').title(),
                        'Prevalence (%)': prevalence
                    })
            
            # Create dataframe and sort by prevalence
            prevalence_df = pd.DataFrame(prevalence_data)
            prevalence_df = prevalence_df.sort_values('Prevalence (%)', ascending=False).head(5)
            
            # Create horizontal bar chart
            fig = px.bar(
                prevalence_df,
                y='Condition',
                x='Prevalence (%)',
                orientation='h',
                title="Top 5 Chronic Conditions",
                color='Prevalence (%)',
                color_continuous_scale='Blues'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Multiple chronic conditions
        if 'multiple_chronic_conditions' in data_to_use.columns:
            mcc_counts = data_to_use['multiple_chronic_conditions'].value_counts().reset_index()
            mcc_counts.columns = ['Has Multiple Conditions', 'Count']
            mcc_counts['Has Multiple Conditions'] = mcc_counts['Has Multiple Conditions'].map({
                1: "Yes (2+ conditions)",
                0: "No (0-1 conditions)"
            })
            
            fig = px.pie(
                mcc_counts,
                names='Has Multiple Conditions',
                values='Count',
                title="Patients with Multiple Chronic Conditions",
                color='Has Multiple Conditions',
                color_discrete_map={
                    'Yes (2+ conditions)': 'firebrick',
                    'No (0-1 conditions)': 'lightblue'
                }
            )
            
            fig.update_traces(textinfo='percent+label')
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Utilization summary
    st.subheader("Healthcare Utilization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Admission distribution
        if 'admission_count' in data_to_use.columns:
            # Create histogram with limited range
            max_admissions = min(int(data_to_use['admission_count'].quantile(0.95)), 10)
            
            # Count patients by admission count
            admission_counts = data_to_use['admission_count'].value_counts().reset_index()
            admission_counts.columns = ['Admissions', 'Count']
            admission_counts = admission_counts[admission_counts['Admissions'] <= max_admissions]
            admission_counts = admission_counts.sort_values('Admissions')
            
            fig = px.bar(
                admission_counts,
                x='Admissions',
                y='Count',
                title="Distribution of Admission Counts",
                labels={'Admissions': 'Number of Admissions', 'Count': 'Number of Patients'},
                color='Admissions',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(xaxis=dict(tickmode='linear'))
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Emergency visits
        if 'emergency_count' in data_to_use.columns:
            # Create histogram with limited range
            max_visits = min(int(data_to_use['emergency_count'].quantile(0.95)), 10)
            
            # Count patients by ED visit count
            ed_counts = data_to_use['emergency_count'].value_counts().reset_index()
            ed_counts.columns = ['ED Visits', 'Count']
            ed_counts = ed_counts[ed_counts['ED Visits'] <= max_visits]
            ed_counts = ed_counts.sort_values('ED Visits')
            
            fig = px.bar(
                ed_counts,
                x='ED Visits',
                y='Count',
                title="Distribution of ED Visit Counts",
                labels={'ED Visits': 'Number of ED Visits', 'Count': 'Number of Patients'},
                color='ED Visits',
                color_continuous_scale='Reds'
            )
            
            fig.update_layout(xaxis=dict(tickmode='linear'))
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Risk stratification
    st.subheader("Risk Stratification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Complexity tier distribution if available
        if 'complexity_tier' in data_to_use.columns:
            # Count by tier
            tier_counts = data_to_use['complexity_tier'].value_counts().reset_index()
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
    
    with col2:
        # Model performance if available
        if model_results is not None and 'summary' in model_results:
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
            
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
