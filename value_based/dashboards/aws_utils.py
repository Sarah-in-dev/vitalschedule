import os
import boto3
import pandas as pd
import streamlit as st
import io

class AWSDataConnector:
    """Utility class for connecting to AWS S3 buckets and loading VBC data"""
    
    def __init__(self, 
                 org_name="predictiverx",
                 raw_bucket_prefix="vbc-raw-data",
                 processed_bucket_prefix="vbc-processed-data",
                 models_bucket_prefix="vbc-models",
                 use_caching=True):
        """Initialize the AWS data connector.
        
        Parameters:
        -----------
        org_name : str
            Organization name used in bucket naming
        raw_bucket_prefix : str
            Prefix for raw data bucket
        processed_bucket_prefix : str
            Prefix for processed data bucket
        models_bucket_prefix : str
            Prefix for models bucket
        use_caching : bool
            Whether to use Streamlit's caching for data loading
        """
        self.org_name = org_name
        self.raw_bucket = f"{raw_bucket_prefix}-{org_name}"
        self.processed_bucket = f"{processed_bucket_prefix}-{org_name}"
        self.models_bucket = f"{models_bucket_prefix}-{org_name}"
        self.use_caching = use_caching
        
        # Initialize S3 client
        self.s3 = boto3.client('s3')
    
    @property
    def _get_aws_session(self):
        """Get AWS session with appropriate credentials."""
        # Try to get from environment variables first
        if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            return boto3.Session(
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_REGION', 'us-east-1')
            )
        # Fall back to default credentials chain
        else:
            return boto3.Session()
    
    def _get_s3_client(self):
        """Get S3 client with appropriate credentials."""
        session = self._get_aws_session
        return session.client('s3')
    
    def list_available_datasets(self):
        """List all available datasets in the processed data bucket."""
        s3 = self._get_s3_client()
        
        # List objects in processed data bucket
        response = s3.list_objects_v2(Bucket=self.processed_bucket)
        
        if 'Contents' not in response:
            return []
        
        # Group by folder
        folders = {}
        for obj in response['Contents']:
            key = obj['Key']
            if '/' in key:
                folder, filename = key.split('/', 1)
                if folder not in folders:
                    folders[folder] = []
                if filename:  # Skip empty filenames (folder markers)
                    folders[folder].append(filename)
        
        return folders
    
    def list_available_models(self):
        """List all available models in the models bucket."""
        s3 = self._get_s3_client()
        
        # List objects in models bucket
        response = s3.list_objects_v2(Bucket=self.models_bucket)
        
        if 'Contents' not in response:
            return {}
        
        # Group by folder
        folders = {}
        for obj in response['Contents']:
            key = obj['Key']
            if '/' in key:
                parts = key.split('/')
                if len(parts) >= 2:
                    main_folder = parts[0]
                    if main_folder not in folders:
                        folders[main_folder] = []
                    # Store the full path excluding the main folder
                    subfolder = '/'.join(parts[1:])
                    if subfolder:  # Skip empty filenames
                        folders[main_folder].append(subfolder)
        
        return folders
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_patient_cohort(self):
        """Load the patient cohort data from S3."""
        s3 = self._get_s3_client()
        
        try:
            # Get patient cohort file
            response = s3.get_object(
                Bucket=self.processed_bucket,
                Key="patient-cohorts/patient_cohort.csv"
            )
            
            # Read into pandas DataFrame
            patient_data = pd.read_csv(io.BytesIO(response['Body'].read()))
            
            print(f"Loaded patient cohort with {len(patient_data)} records")
            return patient_data
        
        except Exception as e:
            print(f"Error loading patient cohort: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_clinical_data(self):
        """Load clinical data from S3."""
        s3 = self._get_s3_client()
        
        try:
            # Get clinical data file
            response = s3.get_object(
                Bucket=self.processed_bucket,
                Key="clinical-features/patients_with_clinical.csv"
            )
            
            # Read into pandas DataFrame
            clinical_data = pd.read_csv(io.BytesIO(response['Body'].read()))
            
            print(f"Loaded clinical data with {len(clinical_data)} records")
            return clinical_data
        
        except Exception as e:
            print(f"Error loading clinical data: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_conditions_data(self):
        """Load chronic conditions data from S3."""
        s3 = self._get_s3_client()
        
        try:
            # Get conditions data file
            response = s3.get_object(
                Bucket=self.processed_bucket,
                Key="diagnoses/patients_with_conditions.csv"
            )
            
            # Read into pandas DataFrame
            conditions_data = pd.read_csv(io.BytesIO(response['Body'].read()))
            
            print(f"Loaded conditions data with {len(conditions_data)} records")
            return conditions_data
        
        except Exception as e:
            print(f"Error loading conditions data: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_medications_data(self):
        """Load medication data from S3."""
        s3 = self._get_s3_client()
        
        try:
            # Get medications data file
            response = s3.get_object(
                Bucket=self.processed_bucket,
                Key="medications/patients_with_medications.csv"
            )
            
            # Read into pandas DataFrame
            medications_data = pd.read_csv(io.BytesIO(response['Body'].read()))
            
            print(f"Loaded medications data with {len(medications_data)} records")
            return medications_data
        
        except Exception as e:
            print(f"Error loading medications data: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_complexity_data(self):
        """Load patient complexity data from S3."""
        s3 = self._get_s3_client()
        
        try:
            # Get complexity data file
            response = s3.get_object(
                Bucket=self.models_bucket,
                Key="complexity-models/patients_with_complexity.csv"
            )
            
            # Read into pandas DataFrame
            complexity_data = pd.read_csv(io.BytesIO(response['Body'].read()))
            
            print(f"Loaded complexity data with {len(complexity_data)} records")
            return complexity_data
        
        except Exception as e:
            print(f"Error loading complexity data: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_model_metrics(self):
        """Load model metrics data from S3."""
        s3 = self._get_s3_client()
        
        try:
            # Get model metrics file
            response = s3.get_object(
                Bucket=self.models_bucket,
                Key="complexity-models/metrics/model_metrics.csv"
            )
            
            # Read into pandas DataFrame
            metrics_data = pd.read_csv(io.BytesIO(response['Body'].read()))
            
            print(f"Loaded model metrics")
            return metrics_data
        
        except Exception as e:
            print(f"Error loading model metrics: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_feature_importance(self):
        """Load feature importance data from S3."""
        s3 = self._get_s3_client()
        
        try:
            # Get feature importance file
            response = s3.get_object(
                Bucket=self.models_bucket,
                Key="feature-importance/feature_importance.csv"
            )
            
            # Read into pandas DataFrame
            importance_data = pd.read_csv(io.BytesIO(response['Body'].read()))
            
            print(f"Loaded feature importance data")
            return importance_data
        
        except Exception as e:
            print(f"Error loading feature importance: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_model_summary(self):
        """Load model summary data from S3."""
        s3 = self._get_s3_client()
        
        try:
            # Get model summary file
            response = s3.get_object(
                Bucket=self.models_bucket,
                Key="feature-importance/model_summary.csv"
            )
            
            # Read into pandas DataFrame
            summary_data = pd.read_csv(io.BytesIO(response['Body'].read()))
            
            print(f"Loaded model summary data")
            return summary_data
        
        except Exception as e:
            print(f"Error loading model summary: {str(e)}")
            return None
    
    def load_merged_patient_data(self):
        """Load and merge all patient data from different sources."""
        # Load base patient cohort
        patient_data = self.load_patient_cohort()
        
        if patient_data is None:
            return None
        
        # Load and merge clinical data
        clinical_data = self.load_clinical_data()
        if clinical_data is not None:
            clinical_cols = [col for col in clinical_data.columns if col not in patient_data.columns or col == 'subject_id']
            patient_data = patient_data.merge(clinical_data[clinical_cols], on='subject_id', how='left')
        
        # Load and merge conditions data
        conditions_data = self.load_conditions_data()
        if conditions_data is not None:
            condition_cols = [col for col in conditions_data.columns if col not in patient_data.columns or col == 'subject_id']
            patient_data = patient_data.merge(conditions_data[condition_cols], on='subject_id', how='left')
        
        # Load and merge medications data
        medications_data = self.load_medications_data()
        if medications_data is not None:
            medication_cols = [col for col in medications_data.columns if col not in patient_data.columns or col == 'subject_id']
            patient_data = patient_data.merge(medications_data[medication_cols], on='subject_id', how='left')
        
        # Load and merge complexity data
        complexity_data = self.load_complexity_data()
        if complexity_data is not None:
            complexity_cols = [col for col in complexity_data.columns if col not in patient_data.columns or col == 'subject_id']
            patient_data = patient_data.merge(complexity_data[complexity_cols], on='subject_id', how='left')
        
        return patient_data
    
    def load_all_model_results(self):
        """Load all model results into a dictionary."""
        results = {}
        
        # Load model summary
        summary_data = self.load_model_summary()
        if summary_data is not None:
            results['summary'] = summary_data
        
        # Load feature importance
        importance_data = self.load_feature_importance()
        if importance_data is not None:
            results['readmission_importance'] = importance_data
        
        # Add any other specialized model results here
        # For example, if we have additional model-specific feature importance files
        
        return results
