# File: survey_analysis_app.py
# Version: 2.0
# Created by: Claude 3.5 Sonnet (2024-01-01)
# 
# Usage:
# 1. Install required packages: pip install streamlit pandas plotly numpy scipy
# 2. Place this script in your project directory
# 3. Run the app: streamlit run survey_analysis_app.py
# 4. Access the app through your web browser at the provided local URL

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColumnMapper:
    """Handle column name mapping between Korean and English."""
    
    def __init__(self):
        # Define Korean to English column mappings
        self.kr_to_en = {
            '년도': 'year',
            '학기': 'semester',
            '캠퍼스': 'campus',
            '개설단과대학': 'college',
            '강좌번호': 'course_number',
            '교과코드': 'course_code',
            '교과목명': 'course_name',
            '교수명': 'professor',
            '교번': 'professor_id',
            '설문1': 'q1',
            '설문2': 'q2',
            '설문3': 'q3',
            '설문4': 'q4',
            '설문5': 'q5',
            '설문6': 'q6',
            '설문7': 'q7',
            '설문8': 'q8',
            'semester_id': 'semester_id',
            'avg_score': 'avg_score',
            'normalized_score': 'norm_score',
            'response_completeness': 'response_rate',
            'department': 'department',
            'course_category': 'course_type'
        }
        # Create reverse mapping
        self.en_to_kr = {v: k for k, v in self.kr_to_en.items()}
        
    def to_english(self, korean_cols):
        """Convert Korean column names to English."""
        return [self.kr_to_en.get(col, col) for col in korean_cols]
    
    def to_korean(self, english_cols):
        """Convert English column names to Korean."""
        return [self.en_to_kr.get(col, col) for col in english_cols]
    
    def get_display_name(self, col):
        """Get display name (Korean) for English column."""
        return self.en_to_kr.get(col, col)

class SurveyDataAnalyzer:
    """Class to handle survey data analysis and visualization."""
    
    def __init__(self):
        self.data = None
        self.survey_columns = None
        self.demographic_columns = None
        self.mapper = ColumnMapper()
        self.column_types = None
        self.q8_data = None
    
    def detect_column_types(self, df):
        """Dynamically detect column types from the dataframe."""
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        survey_cols = [col for col in numeric_cols if col.startswith('q') and col != 'q8']
        demographic_cols = ['campus', 'college', 'department', 'course_type']
        metric_cols = ['avg_score', 'norm_score', 'response_rate']
        
        return {
            'survey': survey_cols,
            'demographic': demographic_cols,
            'metric': metric_cols
        }
    
    def load_data(self, file):
        """Load and validate survey data from uploaded file."""
        try:
            # Read original CSV
            df_original = pd.read_csv(file)
            
            # Extract Q8 data to separate file
            q8_data = df_original[['교과코드', '설문8']].copy()
            q8_data.to_csv('q8_responses.csv', index=False)
            
            # Drop Q8 column from main dataframe
            df = df_original.drop(columns=['설문8'])
            
            # Convert column names to English
            df.columns = self.mapper.to_english(df.columns)
            
            # Convert survey questions to numeric
            survey_cols = [col for col in df.columns if col.startswith('q')]
            for col in survey_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Detect and store column types
            self.column_types = self.detect_column_types(df)
            
            # Store processed dataframe
            self.data = df
            self.q8_data = q8_data
            
            logger.info(f"Loaded data shape: {df.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            st.error(f"Error loading data: {str(e)}")
            return False
    
    def calculate_descriptive_stats(self, group_by=None):
        """Calculate descriptive statistics for survey responses."""
        try:
            survey_cols = self.column_types['survey']
            
            if group_by and group_by != "None":
                stats_df = (self.data.groupby(group_by)[survey_cols]
                           .agg(['count', 'mean', 'median', 'std', 'min', 'max'])
                           .round(2))
            else:
                stats_df = (self.data[survey_cols]
                           .agg(['count', 'mean', 'median', 'std', 'min', 'max'])
                           .round(2))
            
            # Convert column names back to Korean for display
            if isinstance(stats_df.columns, pd.MultiIndex):
                stats_df.columns = pd.MultiIndex.from_tuples(
                    [(self.mapper.get_display_name(col[0]), col[1]) 
                     for col in stats_df.columns]
                )
            
            return stats_df
            
        except Exception as e:
            logger.error(f"Error in calculate_descriptive_stats: {str(e)}")
            st.error(f"Error calculating statistics: {str(e)}")
            return pd.DataFrame()
    
    def create_distribution_plot(self, column):
        """Create distribution plot for a survey question."""
        try:
            fig = px.histogram(
                self.data,
                x=column,
                title=f"Distribution of {self.mapper.get_display_name(column)}",
                labels={column: "Score", "count": "Frequency"},
                nbins=20
            )
            fig.add_vline(x=self.data[column].mean(), line_dash="dash",
                         annotation_text="Mean")
            fig.add_vline(x=self.data[column].median(), line_dash="dot",
                         annotation_text="Median")
            return fig
        except Exception as e:
            logger.error(f"Error creating distribution plot: {str(e)}")
            st.error(f"Error creating plot: {str(e)}")
            return None

def main():
    st.set_page_config(page_title="Survey Analysis Dashboard", layout="wide")
    
    st.title("Student Survey Analysis Dashboard")
    st.write("Upload your survey data CSV file to begin analysis")
    
    # Initialize analyzer
    analyzer = SurveyDataAnalyzer()
    
    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        if analyzer.load_data(uploaded_file):
            st.success("Data loaded successfully!")
            st.info("Note: Question 8 responses have been saved separately to 'q8_responses.csv'")
            
            # Display data preview
            st.subheader("Data Preview")
            st.dataframe(analyzer.data.head())
            
            # Analysis options
            analysis_type = st.selectbox(
                "Select Analysis Type",
                ["Descriptive Statistics", "Distributions"]
            )
            
            if analysis_type == "Descriptive Statistics":
                st.header("Descriptive Statistics")
                
                # Group by selection
                group_by_options = ["None"] + analyzer.column_types['demographic']
                group_by = st.selectbox(
                    "Group by (optional)",
                    group_by_options
                )
                
                # Calculate and display statistics
                stats_df = analyzer.calculate_descriptive_stats(
                    None if group_by == "None" else group_by
                )
                
                if not stats_df.empty:
                    st.dataframe(stats_df)
                    
                    # Download button for stats
                    csv = stats_df.to_csv().encode('utf-8')
                    st.download_button(
                        "Download Statistics CSV",
                        csv,
                        "survey_statistics.csv",
                        "text/csv",
                        key='download-csv'
                    )
            
            elif analysis_type == "Distributions":
                st.header("Score Distributions")
                
                # Question selection for distribution plot
                selected_question = st.selectbox(
                    "Select Question",
                    analyzer.column_types['survey']
                )
                
                # Create and display distribution plot
                dist_fig = analyzer.create_distribution_plot(selected_question)
                if dist_fig:
                    st.plotly_chart(dist_fig)

if __name__ == "__main__":
    main()
