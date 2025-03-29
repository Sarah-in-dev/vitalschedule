import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def display_utilization_summary(patient_data):
    """
    Display utilization summary metrics
    """
    if patient_data is None:
        st.warning("Patient data not available")
        return
    
    st.subheader("Healthcare Utilization Summary")
    
    # Create metrics for utilization
    metrics = []
    
    if 'admission_count' in patient_data.columns:
        metrics.append({
            'name': 'Total Admissions',
            'value': patient_data['admission_count'].sum(),
            'format': ',d'
        })
        
        metrics.append({
            'name': 'Avg. Admissions per Patient',
            'value': patient_data['admission_count'].mean(),
            'format': '.2f'
        })
    
    if 'los_days' in patient_data.columns:
        metrics.append({
            'name': 'Avg. Length of Stay',
            'value': patient_data['los_days'].mean(),
            'format': '.1f days'
        })
    
    if 'emergency_count' in patient_data.columns:
        metrics.append({
            'name': 'Total ED Visits',
            'value': patient_data['emergency_count'].sum(),
            'format': ',d'
        })
    
    # Display metrics in columns
    if metrics:
        # Determine number of columns (max 4)
        num_cols = min(len(metrics), 4)
        cols = st.columns(num_cols)
        
        # Display metrics
        for i, metric in enumerate(metrics):
            with cols[i % num_cols]:
                if 'days' in metric['format']:
                    st.metric(metric['name'], f"{metric['value']:{metric['format'].replace(' days', '')}} days")
                elif ',' in metric['format']:
                    st.metric(metric['name'], f"{metric['value']:,}")
                else:
                    st.metric(metric['name'], f"{metric['value']:{metric['format']}}")

def display_admission_distribution(patient_data):
    """
    Display admission count distribution
    """
    if patient_data is None or 'admission_count' not in patient_data.columns:
        return
    
    st.subheader("Hospital Admission Distribution")
    
    # Create histogram with limited range (e.g., up to 95th percentile or max of 10)
    max_admissions = min(int(patient_data['admission_count'].quantile(0.95)), 10)
    
    # Count patients by admission count
    admission_counts = patient_data['admission_count'].value_counts().reset_index()
    admission_counts.columns = ['Admissions', 'Count']
    admission_counts = admission_counts[admission_counts['Admissions'] <= max_admissions]
    admission_counts = admission_counts.sort_values('Admissions')
    
    # Create bar chart
    fig = px.bar(
        admission_counts,
        x='Admissions',
        y='Count',
        title=f"Distribution of Admission Counts (limited to {max_admissions})",
        labels={'Admissions': 'Number of Admissions', 'Count': 'Number of Patients'},
        color='Admissions',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(xaxis=dict(tickmode='linear'))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add high utilizer analysis
    high_utilizer_threshold = 3  # Define high utilizer as 3+ admissions
    
    high_util_count = (patient_data['admission_count'] >= high_utilizer_threshold).sum()
    high_util_percent = (high_util_count / len(patient_data)) * 100
    
    # Display metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("High Utilizers (3+ admissions)", f"{high_util_count:,}")
    
    with col2:
        st.metric("Percentage of Population", f"{high_util_percent:.1f}%")

def display_emergency_distribution(patient_data):
    """
    Display emergency visit distribution
    """
    if patient_data is None or 'emergency_count' not in patient_data.columns:
        return
    
    st.subheader("Emergency Department Utilization")
    
    # Create histogram with limited range (e.g., up to 95th percentile or max of 10)
    max_visits = min(int(patient_data['emergency_count'].quantile(0.95)), 10)
    
    # Count patients by ED visit count
    ed_counts = patient_data['emergency_count'].value_counts().reset_index()
    ed_counts.columns = ['ED Visits', 'Count']
    ed_counts = ed_counts[ed_counts['ED Visits'] <= max_visits]
    ed_counts = ed_counts.sort_values('ED Visits')
    
    # Create bar chart
    fig = px.bar(
        ed_counts,
        x='ED Visits',
        y='Count',
        title=f"Distribution of ED Visit Counts (limited to {max_visits})",
        labels={'ED Visits': 'Number of ED Visits', 'Count': 'Number of Patients'},
        color='ED Visits',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(xaxis=dict(tickmode='linear'))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add frequent ED user analysis
    freq_ed_threshold = 2  # Define frequent ED user as 2+ visits
    
    freq_ed_count = (patient_data['emergency_count'] >= freq_ed_threshold).sum()
    freq_ed_percent = (freq_ed_count / len(patient_data)) * 100
    
    # Display metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Frequent ED Users (2+ visits)", f"{freq_ed_count:,}")
    
    with col2:
        st.metric("Percentage of Population", f"{freq_ed_percent:.1f}%")

def display_icu_utilization(patient_data):
    """
    Display ICU utilization metrics
    """
    if patient_data is None or 'icu_stay_count' not in patient_data.columns:
        return
    
    st.subheader("ICU Utilization")
    
    # Calculate ICU utilization metrics
    icu_admission_count = (patient_data['icu_stay_count'] > 0).sum()
    icu_admission_rate = (icu_admission_count / len(patient_data)) * 100
    
    multi_icu_count = (patient_data['icu_stay_count'] > 1).sum()
    multi_icu_rate = (multi_icu_count / len(patient_data)) * 100
    
    # Display metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Patients with ICU Stay", f"{icu_admission_count:,} ({icu_admission_rate:.1f}%)")
    
    with col2:
        st.metric("Patients with Multiple ICU Stays", f"{multi_icu_count:,} ({multi_icu_rate:.1f}%)")
    
    # Create histogram with limited range
    max_icu_stays = min(int(patient_data['icu_stay_count'].quantile(0.95)), 5)
    
    # Count patients by ICU stay count
    icu_counts = patient_data['icu_stay_count'].value_counts().reset_index()
    icu_counts.columns = ['ICU Stays', 'Count']
    icu_counts = icu_counts[icu_counts['ICU Stays'] <= max_icu_stays]
    icu_counts = icu_counts.sort_values('ICU Stays')
    
    # Create bar chart
    fig = px.bar(
        icu_counts,
        x='ICU Stays',
        y='Count',
        title=f"Distribution of ICU Stay Counts (limited to {max_icu_stays})",
        labels={'ICU Stays': 'Number of ICU Stays', 'Count': 'Number of Patients'},
        color='ICU Stays',
        color_continuous_scale='Purples'
    )
    
    fig.update_layout(xaxis=dict(tickmode='linear'))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display extended ICU stay information if available
    if 'extended_icu_stay' in patient_data.columns:
        extended_icu_count = patient_data['extended_icu_stay'].sum()
        extended_icu_rate = (extended_icu_count / len(patient_data)) * 100
        
        st.metric("Patients with Extended ICU Stay (>7 days)", f"{extended_icu_count:,} ({extended_icu_rate:.1f}%)")

def display_los_distribution(patient_data):
    """
    Display length of stay distribution
    """
    if patient_data is None or 'los_days' not in patient_data.columns:
        return
    
    st.subheader("Length of Stay Analysis")
    
    # Calculate LOS statistics
    avg_los = patient_data['los_days'].mean()
    median_los = patient_data['los_days'].median()
    
    # Display metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Average Length of Stay", f"{avg_los:.1f} days")
    
    with col2:
        st.metric("Median Length of Stay", f"{median_los:.1f} days")
    
    # Create histogram with limited range (e.g., up to 95th percentile or max of 30 days)
    max_los = min(patient_data['los_days'].quantile(0.95), 30)
    
    # Create histogram
    fig = px.histogram(
        patient_data[patient_data['los_days'] <= max_los],
        x='los_days',
        nbins=30,
        title=f"Distribution of Length of Stay (limited to {max_los:.1f} days)",
        labels={'los_days': 'Length of Stay (days)'},
        color_discrete_sequence=['teal']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create length of stay categorization
    los_categories = pd.cut(
        patient_data['los_days'],
        bins=[0, 2, 5, 10, 30, float('inf')],
        labels=['0-2 days', '3-5 days', '6-10 days', '11-30 days', '>30 days']
    )
    
    # Count patients by LOS category
    los_counts = los_categories.value_counts().reset_index()
    los_counts.columns = ['LOS Category', 'Count']
    
    # Order categories
    los_counts['LOS Category'] = pd.Categorical(
        los_counts['LOS Category'],
        categories=['0-2 days', '3-5 days', '6-10 days', '11-30 days', '>30 days'],
        ordered=True
    )
    los_counts = los_counts.sort_values('LOS Category')
    
    # Create bar chart
    fig = px.bar(
        los_counts,
        x='LOS Category',
        y='Count',
        title="Patients by Length of Stay Category",
        labels={'LOS Category': 'Length of Stay', 'Count': 'Number of Patients'},
        color='LOS Category',
        color_discrete_sequence=px.colors.sequential.Teal
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_utilization_by_demographics(patient_data):
    """
    Display utilization metrics by demographics
    """
    if patient_data is None:
        return
    
    st.subheader("Utilization by Demographics")
    
    # Define potential utilization metrics
    utilization_metrics = []
    
    if 'admission_count' in patient_data.columns:
        utilization_metrics.append(('admission_count', 'Admissions'))
    
    if 'emergency_count' in patient_data.columns:
        utilization_metrics.append(('emergency_count', 'ED Visits'))
    
    if 'icu_stay_count' in patient_data.columns:
        utilization_metrics.append(('icu_stay_count', 'ICU Stays'))
    
    if 'los_days' in patient_data.columns:
        utilization_metrics.append(('los_days', 'Length of Stay (days)'))
    
    if not utilization_metrics:
        return
    
    # Allow user to select metric to visualize
    selected_metric = st.selectbox(
        "Select utilization metric:",
        [metric[1] for metric in utilization_metrics],
        key="utilization_demographic_metric"
    )
    
    # Get corresponding column name
    metric_col = next(metric[0] for metric in utilization_metrics if metric[1] == selected_metric)
    
    # Create visualizations by demographics
    
    # By age group if available
    if 'age_group' in patient_data.columns:
        # Calculate average by age group
        age_utilization = patient_data.groupby('age_group')[metric_col].mean().reset_index()
        age_utilization.columns = ['Age Group', selected_metric]
        
        # Sort age groups if they match our expected format
        age_order = ['0-18', '19-35', '36-50', '51-65', '66-80', '80+']
        if all(age in age_order for age in age_utilization['Age Group']):
            age_utilization['Age Group'] = pd.Categorical(
                age_utilization['Age Group'],
                categories=age_order,
                ordered=True
            )
            age_utilization = age_utilization.sort_values('Age Group')
        
        # Create bar chart
        fig = px.bar(
            age_utilization,
            x='Age Group',
            y=selected_metric,
            title=f"Average {selected_metric} by Age Group",
            labels={'Age Group': 'Age Group'},
            color='Age Group',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # By gender if available
    if 'gender' in patient_data.columns:
        # Calculate average by gender
        gender_utilization = patient_data.groupby('gender')[metric_col].mean().reset_index()
        gender_utilization.columns = ['Gender', selected_metric]
        
        # Create bar chart
        fig = px.bar(
            gender_utilization,
            x='Gender',
            y=selected_metric,
            title=f"Average {selected_metric} by Gender",
            labels={'Gender': 'Gender'},
            color='Gender',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # By chronic condition count if available
    if 'unique_chronic_conditions' in patient_data.columns:
        # Calculate average by condition count (limit to reasonable range)
        max_conditions = min(patient_data['unique_chronic_conditions'].max(), 8)
        condition_utilization = patient_data[patient_data['unique_chronic_conditions'] <= max_conditions].groupby('unique_chronic_conditions')[metric_col].mean().reset_index()
        condition_utilization.columns = ['Chronic Conditions', selected_metric]
        
        # Create bar chart
        fig = px.bar(
            condition_utilization,
            x='Chronic Conditions',
            y=selected_metric,
            title=f"Average {selected_metric} by Number of Chronic Conditions",
            labels={'Chronic Conditions': 'Number of Chronic Conditions'},
            color='Chronic Conditions',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(xaxis=dict(tickmode='linear'))
        
        st.plotly_chart(fig, use_container_width=True)

def display_readmission_analysis(patient_data):
    """
    Display readmission analysis if available
    """
    if patient_data is None or 'readmission_flag' not in patient_data.columns:
        return
    
    st.subheader("Readmission Analysis")
    
    # Calculate readmission rate
    readmission_count = patient_data['readmission_flag'].sum()
    readmission_rate = (readmission_count / len(patient_data)) * 100
    
    # Display metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Patients with Readmission", f"{readmission_count:,}")
    
    with col2:
        st.metric("Readmission Rate", f"{readmission_rate:.1f}%")
    
    # Analyze readmissions by demographics
    
    # By age group if available
    if 'age_group' in patient_data.columns:
        # Calculate readmission rate by age group
        age_readmission = patient_data.groupby('age_group')['readmission_flag'].mean().reset_index()
        age_readmission['Readmission Rate (%)'] = age_readmission['readmission_flag'] * 100
        
        # Sort age groups if they match our expected format
        age_order = ['0-18', '19-35', '36-50', '51-65', '66-80', '80+']
        if all(age in age_order for age in age_readmission['age_group']):
            age_readmission['age_group'] = pd.Categorical(
                age_readmission['age_group'],
                categories=age_order,
                ordered=True
            )
            age_readmission = age_readmission.sort_values('age_group')
        
        # Create bar chart
        fig = px.bar(
            age_readmission,
            x='age_group',
            y='Readmission Rate (%)',
            title="Readmission Rate by Age Group",
            labels={'age_group': 'Age Group'},
            color='Readmission Rate (%)',
            color_continuous_scale='Reds'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # By chronic condition count if available
    if 'unique_chronic_conditions' in patient_data.columns:
        # Calculate readmission rate by condition count (limit to reasonable range)
        max_conditions = min(patient_data['unique_chronic_conditions'].max(), 8)
        condition_readmission = patient_data[patient_data['unique_chronic_conditions'] <= max_conditions].groupby('unique_chronic_conditions')['readmission_flag'].mean().reset_index()
        condition_readmission['Readmission Rate (%)'] = condition_readmission['readmission_flag'] * 100
        
        # Create bar chart
        fig = px.bar(
            condition_readmission,
            x='unique_chronic_conditions',
            y='Readmission Rate (%)',
            title="Readmission Rate by Number of Chronic Conditions",
            labels={'unique_chronic_conditions': 'Number of Chronic Conditions'},
            color='Readmission Rate (%)',
            color_continuous_scale='Reds'
        )
        
        fig.update_layout(xaxis=dict(tickmode='linear'))
        
        st.plotly_chart(fig, use_container_width=True)

def display_utilization_dashboard(patient_data, filtered_data=None):
    """
    Display the healthcare utilization dashboard section
    """
    st.header("Healthcare Utilization Analysis")
    
    # Use filtered data if available, otherwise use all data
    data_to_use = filtered_data if filtered_data is not None else patient_data
    
    # Display utilization summary
    display_utilization_summary(data_to_use)
    
    # Display admission distribution
    display_admission_distribution(data_to_use)
    
    # Display emergency visit distribution
    display_emergency_distribution(data_to_use)
    
    # Display ICU utilization
    display_icu_utilization(data_to_use)
    
    # Display length of stay distribution
    display_los_distribution(data_to_use)
    
    # Display utilization by demographics
    display_utilization_by_demographics(data_to_use)
    
    # Display readmission analysis
    display_readmission_analysis(data_to_use)
