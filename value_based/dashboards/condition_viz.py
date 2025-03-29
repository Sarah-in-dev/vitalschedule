import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def display_condition_prevalence(patient_data):
    """
    Display chronic condition prevalence visualization
    """
    if patient_data is None:
        return
    
    # Get chronic condition columns
    condition_cols = [col for col in patient_data.columns if col in [
        'hypertension', 'diabetes', 'chf', 'copd', 'ckd', 
        'liver_disease', 'cancer', 'depression', 'dementia'
    ]]
    
    if not condition_cols:
        st.warning("Chronic condition data not available")
        return
    
    st.subheader("Chronic Condition Prevalence")
    
    # Calculate prevalence for each condition
    prevalence_data = []
    for col in condition_cols:
        if col in patient_data.columns:
            prevalence = patient_data[col].mean() * 100
            prevalence_data.append({
                'Condition': col.replace('_', ' ').title(),
                'Prevalence (%)': prevalence
            })
    
    # Create dataframe and sort by prevalence
    prevalence_df = pd.DataFrame(prevalence_data)
    prevalence_df = prevalence_df.sort_values('Prevalence (%)', ascending=False)
    
    # Create horizontal bar chart
    fig = px.bar(
        prevalence_df,
        y='Condition',
        x='Prevalence (%)',
        orientation='h',
        title="Chronic Condition Prevalence",
        color='Prevalence (%)',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_title="Prevalence (%)",
        yaxis_title="",
        xaxis=dict(range=[0, max(100, prevalence_df['Prevalence (%)'].max() * 1.1)])
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_condition_counts(patient_data):
    """
    Display count of chronic conditions per patient
    """
    if patient_data is None or 'unique_chronic_conditions' not in patient_data.columns:
        return
    
    st.subheader("Count of Chronic Conditions")
    
    # Get value counts
    condition_counts = patient_data['unique_chronic_conditions'].value_counts().reset_index()
    condition_counts.columns = ['Count', 'Patients']
    condition_counts = condition_counts.sort_values('Count')
    
    # Create bar chart
    fig = px.bar(
        condition_counts,
        x='Count',
        y='Patients',
        title="Distribution of Chronic Condition Count",
        labels={'Count': 'Number of Chronic Conditions', 'Patients': 'Number of Patients'},
        color='Count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear')
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_multiple_conditions(patient_data):
    """
    Display metrics for patients with multiple chronic conditions
    """
    if patient_data is None or 'multiple_chronic_conditions' not in patient_data.columns:
        return
    
    st.subheader("Multiple Chronic Conditions")
    
    # Calculate percentage with multiple conditions
    mcc_percent = patient_data['multiple_chronic_conditions'].mean() * 100
    
    # Create columns for metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Patients with Multiple Chronic Conditions", f"{mcc_percent:.1f}%")
    
    with col2:
        if 'unique_chronic_conditions' in patient_data.columns:
            avg_conditions = patient_data['unique_chronic_conditions'].mean()
            st.metric("Average Number of Conditions", f"{avg_conditions:.2f}")
    
    # Create pie chart of multiple vs. single/no conditions
    mcc_counts = patient_data['multiple_chronic_conditions'].value_counts().reset_index()
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

def display_condition_cooccurrence(patient_data):
    """
    Display chronic condition co-occurrence matrix
    """
    if patient_data is None:
        return
    
    # Get chronic condition columns
    condition_cols = [col for col in patient_data.columns if col in [
        'hypertension', 'diabetes', 'chf', 'copd', 'ckd', 
        'liver_disease', 'cancer', 'depression', 'dementia'
    ]]
    
    if len(condition_cols) < 2:
        return
    
    st.subheader("Condition Co-occurrence")
    
    # Create co-occurrence matrix
    condition_names = [col.replace('_', ' ').title() for col in condition_cols]
    cooccurrence = pd.DataFrame(index=condition_names, columns=condition_names)
    
    # Calculate co-occurrence rates
    for i, col1 in enumerate(condition_cols):
        for j, col2 in enumerate(condition_cols):
            if i == j:
                # Diagonal is 1 (condition always co-occurs with itself)
                cooccurrence.iloc[i, j] = 1.0
            else:
                # Calculate conditional probability: P(col2=1 | col1=1)
                patients_with_col1 = patient_data[patient_data[col1] == 1]
                if len(patients_with_col1) > 0:
                    cooccurrence.iloc[i, j] = patients_with_col1[col2].mean()
                else:
                    cooccurrence.iloc[i, j] = 0.0
    
    # Create heatmap
    fig = px.imshow(
        cooccurrence,
        labels=dict(x="Condition", y="Condition", color="Co-occurrence Rate"),
        x=condition_names,
        y=condition_names,
        color_continuous_scale='Blues',
        title="Chronic Condition Co-occurrence Matrix"
    )
    
    fig.update_layout(
        xaxis=dict(tickangle=45),
        width=800,
        height=600
    )
    
    # Add text annotations
    for i in range(len(condition_names)):
        for j in range(len(condition_names)):
            fig.add_annotation(
                x=j,
                y=i,
                text=f"{cooccurrence.iloc[i, j]:.2f}",
                showarrow=False,
                font=dict(color="black" if cooccurrence.iloc[i, j] < 0.7 else "white")
            )
    
    st.plotly_chart(fig, use_container_width=True)

def display_condition_by_demographics(patient_data):
    """
    Display chronic conditions by demographics
    """
    if patient_data is None:
        return
    
    # Get chronic condition columns
    condition_cols = [col for col in patient_data.columns if col in [
        'hypertension', 'diabetes', 'chf', 'copd', 'ckd', 
        'liver_disease', 'cancer', 'depression', 'dementia'
    ]]
    
    if not condition_cols:
        return
    
    st.subheader("Chronic Conditions by Demographics")
    
    # Add age group analysis if available
    if 'age_group' in patient_data.columns:
        # Allow user to select condition
        selected_condition = st.selectbox(
            "Select condition to analyze:",
            [col.replace('_', ' ').title() for col in condition_cols],
            key="condition_by_demographics"
        )
        
        # Convert back to column name
        condition_col = condition_cols[[col.replace('_', ' ').title() for col in condition_cols].index(selected_condition)]
        
        # Calculate prevalence by age group
        age_prevalence = patient_data.groupby('age_group')[condition_col].mean().reset_index()
        age_prevalence[f"{selected_condition} Prevalence (%)"] = age_prevalence[condition_col] * 100
        
        # Sort age groups if they match our expected format
        age_order = ['0-18', '19-35', '36-50', '51-65', '66-80', '80+']
        if all(age in age_order for age in age_prevalence['age_group']):
            age_prevalence['age_group'] = pd.Categorical(
                age_prevalence['age_group'],
                categories=age_order,
                ordered=True
            )
            age_prevalence = age_prevalence.sort_values('age_group')
        
        # Create bar chart
        fig = px.bar(
            age_prevalence,
            x='age_group',
            y=f"{selected_condition} Prevalence (%)",
            title=f"{selected_condition} Prevalence by Age Group",
            labels={'age_group': 'Age Group'},
            color=f"{selected_condition} Prevalence (%)",
            color_continuous_scale='Blues'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add gender analysis if available
        if 'gender' in patient_data.columns:
            # Calculate prevalence by gender
            gender_prevalence = patient_data.groupby('gender')[condition_col].mean().reset_index()
            gender_prevalence[f"{selected_condition} Prevalence (%)"] = gender_prevalence[condition_col] * 100
            
            # Create bar chart
            fig = px.bar(
                gender_prevalence,
                x='gender',
                y=f"{selected_condition} Prevalence (%)",
                title=f"{selected_condition} Prevalence by Gender",
                labels={'gender': 'Gender'},
                color='gender'
            )
            
            st.plotly_chart(fig, use_container_width=True)

def display_conditions_dashboard(patient_data, filtered_data=None):
    """
    Display the chronic conditions dashboard section
    """
    st.header("Chronic Conditions Analysis")
    
    # Use filtered data if available, otherwise use all data
    data_to_use = filtered_data if filtered_data is not None else patient_data
    
    # Display condition prevalence
    display_condition_prevalence(data_to_use)
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    with col1:
        display_condition_counts(data_to_use)
    
    with col2:
        display_multiple_conditions(data_to_use)
    
    # Display condition co-occurrence
    display_condition_cooccurrence(data_to_use)
    
    # Display conditions by demographics
    display_condition_by_demographics(data_to_use)
