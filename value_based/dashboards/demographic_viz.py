import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def display_patient_counts(patient_data, filtered_data=None):
    """
    Display patient count metrics
    """
    total_patients = len(patient_data) if patient_data is not None else 0
    filtered_patients = len(filtered_data) if filtered_data is not None else total_patients
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Patients", f"{total_patients:,}")
    
    with col2:
        if filtered_patients != total_patients:
            st.metric("Filtered Patients", f"{filtered_patients:,}", 
                     f"{filtered_patients/total_patients:.1%} of total")
        else:
            st.metric("Filtered Patients", f"{filtered_patients:,}")

def display_age_distribution(patient_data):
    """
    Display age distribution visualization
    """
    if patient_data is None or 'age_group' not in patient_data.columns:
        st.warning("Age group data not available")
        return
    
    st.subheader("Age Distribution")
    
    # Count patients by age group
    age_counts = patient_data['age_group'].value_counts().reset_index()
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
    
    # Create bar chart
    fig = px.bar(
        age_counts, 
        x='Age Group', 
        y='Count',
        text_auto='.2s',
        title="Patient Distribution by Age Group",
        color='Age Group',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Number of Patients",
        legend_title="Age Group"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_gender_distribution(patient_data):
    """
    Display gender distribution visualization
    """
    if patient_data is None or 'gender' not in patient_data.columns:
        st.warning("Gender data not available")
        return
    
    st.subheader("Gender Distribution")
    
    # Count patients by gender
    gender_counts = patient_data['gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']
    
    # Create pie chart
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

def display_age_gender_distribution(patient_data):
    """
    Display age by gender distribution
    """
    if patient_data is None or 'gender' not in patient_data.columns or 'age_group' not in patient_data.columns:
        return
    
    st.subheader("Age and Gender Distribution")
    
    # Create cross-tabulation of age and gender
    age_gender = pd.crosstab(
        patient_data['age_group'], 
        patient_data['gender'],
        normalize=False
    ).reset_index()
    
    # Sort the age groups in correct order if they match our expected format
    age_order = ['0-18', '19-35', '36-50', '51-65', '66-80', '80+']
    if all(age in age_order for age in age_gender['age_group']):
        age_gender['age_group'] = pd.Categorical(
            age_gender['age_group'],
            categories=age_order,
            ordered=True
        )
        age_gender = age_gender.sort_values('age_group')
    
    # Melt the dataframe for plotting
    age_gender_melted = age_gender.melt(
        id_vars=['age_group'],
        var_name='gender',
        value_name='count'
    )
    
    # Create grouped bar chart
    fig = px.bar(
        age_gender_melted, 
        x='age_group', 
        y='count',
        color='gender',
        barmode='group',
        title="Patient Distribution by Age and Gender",
        labels={'age_group': 'Age Group', 'count': 'Number of Patients', 'gender': 'Gender'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_utilization_metrics(patient_data):
    """
    Display key utilization metrics
    """
    if patient_data is None:
        return
    
    st.subheader("Utilization Metrics")
    
    metrics = []
    
    # Add metrics if they exist in the data
    if 'admission_count' in patient_data.columns:
        metrics.append({
            'name': 'Average Admissions',
            'value': patient_data['admission_count'].mean(),
            'format': '.2f'
        })
    
    if 'los_days' in patient_data.columns:
        metrics.append({
            'name': 'Average Length of Stay',
            'value': patient_data['los_days'].mean(),
            'format': '.1f days'
        })
    
    if 'icu_stay_count' in patient_data.columns:
        metrics.append({
            'name': 'ICU Admission Rate',
            'value': (patient_data['icu_stay_count'] > 0).mean() * 100,
            'format': '.1f%'
        })
    
    if 'emergency_count' in patient_data.columns:
        metrics.append({
            'name': 'Emergency Visit Rate',
            'value': (patient_data['emergency_count'] > 0).mean() * 100,
            'format': '.1f%'
        })
    
    # Display metrics in columns
    if metrics:
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                if metric['format'].endswith('%'):
                    st.metric(metric['name'], f"{metric['value']:{metric['format']}}")
                elif metric['format'].endswith('days'):
                    st.metric(metric['name'], f"{metric['value']:{metric['format'].replace(' days', '')}} days")
                else:
                    st.metric(metric['name'], f"{metric['value']:{metric['format']}}")

def display_utilization_distribution(patient_data):
    """
    Display utilization distribution charts
    """
    if patient_data is None:
        return
    
    # Check if we have utilization metrics
    utilization_cols = [col for col in ['admission_count', 'emergency_count', 'icu_stay_count'] 
                        if col in patient_data.columns]
    
    if not utilization_cols:
        return
    
    st.subheader("Healthcare Utilization")
    
    # Create distribution charts for each utilization metric
    for col in utilization_cols:
        # Prepare data - limit to reasonable range (up to 95th percentile)
        max_val = min(patient_data[col].quantile(0.95), 10)
        plot_data = patient_data[patient_data[col] <= max_val].copy()
        
        # Count values
        value_counts = plot_data[col].value_counts().reset_index()
        value_counts.columns = ['Value', 'Count']
        value_counts = value_counts.sort_values('Value')
        
        # Get column title
        if col == 'admission_count':
            title = "Distribution of Hospital Admissions"
            x_title = "Number of Admissions"
        elif col == 'emergency_count':
            title = "Distribution of Emergency Visits"
            x_title = "Number of ED Visits"
        elif col == 'icu_stay_count':
            title = "Distribution of ICU Stays"
            x_title = "Number of ICU Stays"
        else:
            title = f"Distribution of {col.replace('_', ' ').title()}"
            x_title = "Value"
        
        # Create bar chart
        fig = px.bar(
            value_counts,
            x='Value',
            y='Count',
            title=title,
            labels={'Value': x_title, 'Count': 'Number of Patients'}
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_demographic_dashboard(patient_data, filtered_data=None):
    """
    Display the demographics dashboard section
    """
    st.header("Patient Demographics")
    
    # Show patient counts
    display_patient_counts(patient_data, filtered_data)
    
    # Use filtered data if available, otherwise use all data
    data_to_use = filtered_data if filtered_data is not None else patient_data
    
    # Create two columns for age and gender distributions
    col1, col2 = st.columns(2)
    
    with col1:
        display_age_distribution(data_to_use)
    
    with col2:
        display_gender_distribution(data_to_use)
    
    # Display age by gender distribution
    display_age_gender_distribution(data_to_use)
    
    # Display utilization metrics
    display_utilization_metrics(data_to_use)
    
    # Display utilization distributions
    display_utilization_distribution(data_to_use)
