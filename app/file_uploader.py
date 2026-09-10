"""
CSV/Excel File Upload, Validation, and Normalization Module
Handles variable row counts and data preprocessing
"""
import pandas as pd
from datetime import datetime
from typing import Tuple, List, Optional, Dict
import io


class FileUploadError(Exception):
    """Custom exception for file upload errors"""
    pass


class FileUploader:
    """
    Handles CSV and Excel file uploads with validation and normalization
    """
    
    # Required columns for ticket processing
    REQUIRED_COLUMNS = [
        'ticket_id',
        'created_at',
        'customer_tier',
        'product',
        'product_category',
        'product_criticality',
        'issue_type',
        'channel',
        'current_severity',
        'sla_target_hours',
        'production_impact',
        'business_impact'
    ]
    
    # Optional columns that enhance predictions
    OPTIONAL_COLUMNS = [
        'updated_at',
        'customer_id',
        'sla_remaining_hours',
        'sla_breached',
        'reopen_count',
        'customer_contact_count',
        'affected_users_estimate',
        'security_related',
        'customer_sentiment',
        'urgency_keywords',
        'issue_description',
        'waiting_time_hours',
        'status',
        'assigned_team',
        'previous_escalation'
    ]
    
    # All expected columns
    ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS
    
    def __init__(self):
        """Initialize file uploader"""
        pass
    
    def read_file(self, uploaded_file) -> pd.DataFrame:
        """
        Read uploaded CSV or Excel file
        
        Args:
            uploaded_file: Streamlit UploadedFile object or file-like object
            
        Returns:
            DataFrame with uploaded data
            
        Raises:
            FileUploadError: If file cannot be read
        """
        try:
            # Get filename
            filename = uploaded_file.name.lower()
            
            # Read based on file type
            if filename.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, engine='openpyxl')
            elif filename.endswith('.xls'):
                df = pd.read_excel(uploaded_file, engine='xlrd')
            else:
                raise FileUploadError(
                    f"Unsupported file type. Please upload CSV or Excel (.xlsx, .xls) files."
                )
            
            return df
            
        except FileUploadError:
            raise
        except Exception as e:
            raise FileUploadError(f"Failed to read file: {str(e)}")
    
    def validate_columns(self, df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        """
        Validate that required columns are present
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple of (is_valid, missing_columns, extra_columns)
        """
        df_columns = set(df.columns)
        required_columns = set(self.REQUIRED_COLUMNS)
        
        # Check for missing required columns
        missing = list(required_columns - df_columns)
        
        # Check for extra columns (informational only, not an error)
        all_expected = set(self.ALL_COLUMNS)
        extra = list(df_columns - all_expected)
        
        is_valid = len(missing) == 0
        
        return is_valid, missing, extra
    
    def normalize_boolean_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize boolean columns (Yes/No, True/False, 1/0)
        
        Args:
            df: DataFrame to normalize
            
        Returns:
            Normalized DataFrame
        """
        df = df.copy()
        
        boolean_columns = ['sla_breached', 'security_related', 'previous_escalation']
        
        for col in boolean_columns:
            if col in df.columns:
                # Convert to string first
                df[col] = df[col].astype(str).str.strip().str.lower()
                
                # Map various forms to 1/0
                df[col] = df[col].map({
                    'yes': 1, 'y': 1, 'true': 1, 't': 1, '1': 1, '1.0': 1,
                    'no': 0, 'n': 0, 'false': 0, 'f': 0, '0': 0, '0.0': 0,
                    'nan': 0, 'none': 0, '': 0
                })
                
                # Fill any remaining NaN with 0
                df[col] = df[col].fillna(0).astype(int)
        
        return df
    
    def normalize_datetime_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize datetime columns
        
        Args:
            df: DataFrame to normalize
            
        Returns:
            Normalized DataFrame
        """
        df = df.copy()
        
        datetime_columns = ['created_at', 'updated_at']
        
        for col in datetime_columns:
            if col in df.columns:
                # Parse datetime with flexible format
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # For created_at, if missing, use current time
                if col == 'created_at':
                    df[col] = df[col].fillna(pd.Timestamp.now())
        
        return df
    
    def normalize_numerical_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize numerical columns
        
        Args:
            df: DataFrame to normalize
            
        Returns:
            Normalized DataFrame
        """
        df = df.copy()
        
        numerical_columns = [
            'sla_target_hours',
            'sla_remaining_hours',
            'reopen_count',
            'customer_contact_count',
            'affected_users_estimate',
            'waiting_time_hours'
        ]
        
        for col in numerical_columns:
            if col in df.columns:
                # Convert to numeric, coerce errors
                df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Fill NaN with appropriate defaults
                if col in ['sla_target_hours']:
                    df[col] = df[col].fillna(24)  # Default 24 hours
                elif col in ['reopen_count', 'customer_contact_count']:
                    df[col] = df[col].fillna(0)
                elif col == 'affected_users_estimate':
                    df[col] = df[col].fillna(1)  # At least 1 user
                elif col == 'waiting_time_hours':
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna(0)
        
        return df
    
    def normalize_categorical_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize categorical columns
        
        Args:
            df: DataFrame to normalize
            
        Returns:
            Normalized DataFrame
        """
        df = df.copy()
        
        categorical_columns = [
            'customer_tier',
            'product',
            'product_category',
            'product_criticality',
            'issue_type',
            'channel',
            'current_severity',
            'production_impact',
            'business_impact',
            'customer_sentiment',
            'urgency_keywords',
            'status',
            'assigned_team'
        ]
        
        for col in categorical_columns:
            if col in df.columns:
                # Convert to string and strip whitespace
                df[col] = df[col].astype(str).str.strip()
                
                # Replace 'nan', 'None', '' with 'Unknown'
                df[col] = df[col].replace(['nan', 'None', '', 'NaN'], 'Unknown')
                
                # Handle specific defaults
                if col == 'status' and df[col].eq('Unknown').all():
                    df[col] = 'Open'
        
        return df
    
    def check_duplicates(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Check for duplicate ticket IDs
        
        Args:
            df: DataFrame to check
            
        Returns:
            Tuple of (has_duplicates, list_of_duplicate_ids)
        """
        if 'ticket_id' not in df.columns:
            return False, []
        
        duplicates = df[df.duplicated(subset=['ticket_id'], keep=False)]['ticket_id'].unique().tolist()
        has_duplicates = len(duplicates) > 0
        
        return has_duplicates, duplicates
    
    def add_missing_optional_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add missing optional columns with default values
        
        Args:
            df: DataFrame to process
            
        Returns:
            DataFrame with all expected columns
        """
        df = df.copy()
        
        # Default values for missing optional columns
        defaults = {
            'updated_at': pd.Timestamp.now(),
            'customer_id': 'UNKNOWN',
            'sla_remaining_hours': 24,
            'sla_breached': 0,
            'reopen_count': 0,
            'customer_contact_count': 1,
            'affected_users_estimate': 1,
            'security_related': 0,
            'customer_sentiment': 'Neutral',
            'urgency_keywords': 'None',
            'issue_description': 'No description provided',
            'waiting_time_hours': 0,
            'status': 'Open',
            'assigned_team': 'Support',
            'previous_escalation': 0
        }
        
        for col, default_value in defaults.items():
            if col not in df.columns:
                df[col] = default_value
        
        return df
    
    def process_uploaded_file(self, uploaded_file) -> Tuple[pd.DataFrame, Dict[str, any]]:
        """
        Complete processing pipeline for uploaded file
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple of (processed_dataframe, info_dict)
            
        Raises:
            FileUploadError: If validation fails
        """
        # 1. Read file
        df = self.read_file(uploaded_file)
        
        info = {
            'original_rows': len(df),
            'original_columns': len(df.columns),
            'filename': uploaded_file.name
        }
        
        # 2. Validate columns
        is_valid, missing_cols, extra_cols = self.validate_columns(df)
        
        if not is_valid:
            raise FileUploadError(
                f"Missing required columns: {', '.join(missing_cols)}\n\n"
                f"Required columns are:\n" + '\n'.join(f"  • {col}" for col in self.REQUIRED_COLUMNS)
            )
        
        info['missing_columns'] = missing_cols
        info['extra_columns'] = extra_cols
        
        # 3. Check for duplicates (warning only, not blocking)
        has_dupes, duplicate_ids = self.check_duplicates(df)
        info['has_duplicates'] = has_dupes
        info['duplicate_ids'] = duplicate_ids
        
        # 4. Normalize data
        df = self.normalize_datetime_columns(df)
        df = self.normalize_boolean_columns(df)
        df = self.normalize_numerical_columns(df)
        df = self.normalize_categorical_columns(df)
        
        # 5. Add missing optional columns
        df = self.add_missing_optional_columns(df)
        
        # 6. Final validation - remove any rows with missing ticket_id
        df = df[df['ticket_id'].notna() & (df['ticket_id'] != 'Unknown')]
        
        info['processed_rows'] = len(df)
        info['processed_columns'] = len(df.columns)
        
        return df, info
    
    def get_column_template(self) -> pd.DataFrame:
        """
        Generate a template DataFrame with all expected columns
        
        Returns:
            Empty DataFrame with correct columns and example data
        """
        template_data = {
            'ticket_id': ['TKT-001', 'TKT-002'],
            'created_at': [datetime.now().isoformat(), datetime.now().isoformat()],
            'customer_tier': ['Platinum', 'Standard'],
            'product': ['Core Platform', 'Analytics'],
            'product_category': ['Infrastructure', 'Analytics'],
            'product_criticality': ['Critical', 'Medium'],
            'issue_type': ['Outage', 'Question'],
            'channel': ['Phone', 'Email'],
            'current_severity': ['Critical', 'Low'],
            'sla_target_hours': [4, 48],
            'production_impact': ['Major', 'None'],
            'business_impact': ['High', 'Low'],
            'sla_breached': ['No', 'No'],
            'reopen_count': [0, 0],
            'customer_contact_count': [3, 1],
            'affected_users_estimate': [5000, 1],
            'security_related': ['No', 'No'],
            'customer_sentiment': ['Frustrated', 'Neutral'],
            'urgency_keywords': ['Critical', 'None'],
            'waiting_time_hours': [2, 5],
            'status': ['Open', 'Open'],
            'assigned_team': ['Platform', 'Support'],
            'previous_escalation': ['No', 'No'],
            'issue_description': ['System is down', 'How to use feature X?']
        }
        
        return pd.DataFrame(template_data)
