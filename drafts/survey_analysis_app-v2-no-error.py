# File: survey_analysis_app.py
# Version: 2.1
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
            '설문7': 'q7'
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
        """Initialize the analyzer with default settings."""
        self.data = None
        self.survey_columns = None
        self.demographic_columns = None
        self.mapper = ColumnMapper()
        self.column_types = None
    
    def detect_column_types(self, df):
        """Dynamically detect column types from the dataframe."""
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        survey_cols = [col for col in numeric_cols if col.startswith('q')]
        
        # Define grouping columns
        demographic_cols = ['campus', 'college', 'course_name', 'course_number']
        
        # Create combined course identifier
        df['course_id'] = df['course_name'] + ' (' + df['course_number'].astype(str) + ')'
        demographic_cols.append('course_id')
        
        return {
            'survey': survey_cols,
            'demographic': demographic_cols,
            'grouping_options': {
                'campus': '캠퍼스',
                'college': '개설단과대학',
                'course_id': '교과목명 (강좌번호)'
            }
        }
    
    def load_data(self, file):
        """Load and validate survey data from uploaded file."""
        try:
            # Read original CSV
            df_original = pd.read_csv(file)
            
            # Select only the columns we want to keep
            columns_to_keep = [col for col in df_original.columns 
                             if not col.startswith('설문8') and 
                             not col in ['교수명', '교번'] and
                             not col in ['semester_id', 'avg_score', 'normalized_score', 
                                       'response_completeness', 'department', 'course_category']]
            
            df = df_original[columns_to_keep].copy()
            
            # Convert column names to English internally
            df.columns = self.mapper.to_english(df.columns)
            
            # Convert survey questions to numeric
            survey_cols = [col for col in df.columns if col.startswith('q')]
            for col in survey_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Detect and store column types
            self.column_types = self.detect_column_types(df)
            
            # Store processed dataframe
            self.data = df
            
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
                # Prepare data for grouping
                df_stats = self.data.copy()
                
                # Calculate statistics
                stats_df = (df_stats.groupby(group_by)[survey_cols]
                           .agg(['count', 'mean', 'median', 'std', 'min', 'max'])
                           .round(2))
                
                # Sort by count in descending order
                if isinstance(stats_df.columns, pd.MultiIndex):
                    count_col = stats_df.columns[0][0]  # First column's count
                    stats_df = stats_df.sort_values((count_col, 'count'), ascending=False)
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
            # Ensure we're using a single column name
            if isinstance(column, list):
                column = column[0]
                
            fig = px.histogram(
                self.data,
                x=column,
                title=f"{self.mapper.get_display_name(column)} 점수 분포",
                labels={column: "점수", "count": "빈도"},
                nbins=20,
                text_auto=True  # Show counts on top of bars
            )
            
            mean_val = self.data[column].mean()
            median_val = self.data[column].median()
            
            fig.add_vline(
                x=mean_val, 
                line_dash="dash",
                annotation_text=f"평균: {mean_val:.2f}",
                annotation_position="top right"
            )
            fig.add_vline(
                x=median_val, 
                line_dash="dot",
                annotation_text=f"중앙값: {median_val:.2f}",
                annotation_position="bottom right"
            )
            
            # Update layout for better readability
            fig.update_layout(
                bargap=0.1,
                xaxis_title="점수",
                yaxis_title="빈도",
                showlegend=False,
                font=dict(size=12)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating distribution plot: {str(e)}")
            st.error(f"Error creating plot: {str(e)}")
            return None

def main():
    st.set_page_config(
        page_title="강의평가 분석 대시보드",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS to handle column width issues
    st.markdown("""
        <style>
        .dataframe {
            min-width: 100% !important;
            width: 100% !important;
        }
        .dataframe td, .dataframe th {
            min-width: 120px !important;  /* Minimum width for columns */
            white-space: normal !important;  /* Allow text wrapping */
            padding: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("강의평가 분석 대시보드")
    st.write("분석할 CSV 파일을 업로드해주세요")
    
    # Initialize analyzer
    analyzer = SurveyDataAnalyzer()
    
    # File upload
    uploaded_file = st.file_uploader("CSV 파일 선택", type="csv")
    
    if uploaded_file is not None:
        if analyzer.load_data(uploaded_file):
            st.success("데이터를 성공적으로 불러왔습니다!")
            
            # Display data preview
            st.subheader("데이터 미리보기")
            st.dataframe(analyzer.data.head())
            
            # Analysis options
            analysis_type = st.selectbox(
                "분석 유형 선택",
                ["기술통계", "분포 분석"]
            )
            
            if analysis_type == "기술통계":
                st.header("기술통계 분석")
                
                # Group by selection
                group_by_options = ["없음"] + list(analyzer.column_types['grouping_options'].values())
                group_by = st.selectbox(
                    "그룹화 기준 (선택사항)",
                    group_by_options
                )
                
                # Map selected option back to column name
                if group_by != "없음":
                    # Reverse lookup in grouping_options
                    group_by_col = next(
                        (k for k, v in analyzer.column_types['grouping_options'].items() 
                         if v == group_by), 
                        None
                    )
                else:
                    group_by_col = None
                
                # Calculate and display statistics
                stats_df = analyzer.calculate_descriptive_stats(group_by_col)
                
                if not stats_df.empty:
                    st.dataframe(stats_df)
                    
                    # Download button for stats
                    csv = stats_df.to_csv().encode('utf-8')
                    st.download_button(
                        "통계 데이터 CSV 다운로드",
                        csv,
                        "survey_statistics.csv",
                        "text/csv",
                        key='download-csv'
                    )
            
            elif analysis_type == "분포 분석":
                st.header("점수 분포 분석")
                
                # Question selection for distribution plot
                question_options = [
                    analyzer.mapper.get_display_name(col) 
                    for col in analyzer.column_types['survey']
                ]
                selected_question = st.selectbox(
                    "문항 선택",
                    question_options,
                    key='dist_question_select'
                )
                
                # Get English column name for selected question
                selected_col = next(
                    col for col in analyzer.column_types['survey']
                    if analyzer.mapper.get_display_name(col) == selected_question
                )
                
                # Create and display distribution plot
                dist_fig = analyzer.create_distribution_plot(selected_col)
                if dist_fig:
                    st.plotly_chart(dist_fig, use_container_width=True)
                    
                    # Display basic statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("응답 수", f"{len(analyzer.data[selected_col].dropna()):,}")
                    with col2:
                        st.metric("평균", f"{analyzer.data[selected_col].mean():.2f}")
                    with col3:
                        st.metric("중앙값", f"{analyzer.data[selected_col].median():.2f}")
                    with col4:
                        st.metric("표준편차", f"{analyzer.data[selected_col].std():.2f}")

if __name__ == "__main__":
    main()