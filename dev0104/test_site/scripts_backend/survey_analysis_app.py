#!/usr/bin/env python3
"""
File: survey_analysis_app.py
Version: 2.0.0
Created: 2024-01-01
Author: Claude 3.5 Sonnet (2024-01)

A Streamlit application for analyzing and visualizing course evaluation data.
Provides statistical analysis, distribution visualization, and size-based analysis
of course evaluation results.

Usage:
1. Ensure all required files are in place:
   your_project_directory/
   ├── survey_analysis_app.py
   └── size_range_analyzer.py

2. Install required packages:
   pip install streamlit pandas plotly numpy

3. Run the application:
   streamlit run survey_analysis_app.py

4. Access the application through your web browser at the provided URL
   (typically http://localhost:8501)

Dependencies:
- streamlit
- pandas
- plotly
- numpy
- size_range_analyzer (local module)

Data Requirements:
- CSV file containing course evaluation data
- Required columns: 년도, 학기, 캠퍼스, 개설단과대학, 교과목명, 설문1-7
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import logging
from typing import Dict, List, Optional, Union
from size_range_analyzer import SizeRangeAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColumnMapper:
    """Handle column name mapping between Korean and English."""
    
    def __init__(self):
        self.kr_to_en = {
            '년도': 'year',
            '학기': 'semester',
            '캠퍼스': 'campus',
            '개설단과대학': 'college',
            '교과목명': 'course_name',
            '설문1': 'q1',
            '설문2': 'q2',
            '설문3': 'q3',
            '설문4': 'q4',
            '설문5': 'q5',
            '설문6': 'q6',
            '설문7': 'q7'
        }
        self.en_to_kr = {v: k for k, v in self.kr_to_en.items()}
    
    def to_english(self, korean_cols: Union[str, List[str]]) -> Union[str, List[str]]:
        """Convert Korean column names to English."""
        if isinstance(korean_cols, str):
            return self.kr_to_en.get(korean_cols, korean_cols)
        return [self.kr_to_en.get(col, col) for col in korean_cols]
    
    def to_korean(self, english_cols: Union[str, List[str]]) -> Union[str, List[str]]:
        """Convert English column names to Korean."""
        if isinstance(english_cols, str):
            return self.en_to_kr.get(english_cols, english_cols)
        return [self.en_to_kr.get(col, col) for col in english_cols]

class SurveyDataAnalyzer:
    """Class to handle survey data analysis and visualization."""
    
    def __init__(self):
        self.data = None
        self.mapper = ColumnMapper()
        self.column_types = None
        self.size_analyzer = SizeRangeAnalyzer()

    def load_data(self, file) -> bool:
        """Load and validate survey data from uploaded file."""
        try:
            # Read raw data
            df = pd.read_csv(file)
            logger.info(f"Loaded raw data: {df.shape}")
            logger.info(f"Columns: {df.columns.tolist()}")
            
            # Verify required columns exist
            required_cols = ['교과목명', '강좌번호', '개설단과대학']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Get survey columns
            survey_cols = [col for col in df.columns if col.startswith('설문') and col != '설문8']
            if not survey_cols:
                raise ValueError("No survey questions found in the data")
            
            # Convert survey columns to numeric
            for col in survey_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Create course identifier before grouping
            df['course_id'] = df['교과목명'].astype(str) + ' (' + df['강좌번호'].astype(str) + ')'
            
            # Group by course to get course-level metrics
            course_stats = df.groupby(['course_id', '개설단과대학']).agg({
                **{col: ['count', 'mean'] for col in survey_cols}  # Get count and mean for each survey question
            }).reset_index()
            
            # Flatten multi-level columns
            course_stats.columns = [f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col 
                                  for col in course_stats.columns]
            
            # Calculate total responses (using count from first question)
            course_stats['응답자 수'] = course_stats[f'설문1_count']
            
            # Calculate average score across all questions
            mean_cols = [col for col in course_stats.columns if col.endswith('_mean')]
            course_stats['평균 점수'] = course_stats[mean_cols].mean(axis=1)
            
            # Rename course_id column to maintain compatibility
            course_stats = course_stats.rename(columns={'course_id': '교과목명'})
            
            # Log summary statistics
            logger.info(f"Processed {len(course_stats)} unique courses")
            logger.info("\nResponse count distribution:")
            logger.info(course_stats['응답자 수'].describe())
            
            # Store processed data
            self.data = course_stats
            
            # Process size-based analysis
            self.size_analyzer.process_data(course_stats)
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
            return False
            
            # Store processed data
            self.data = df
            
            # Process size-based analysis
            self.size_analyzer.process_data(df)
            
            logger.info(f"Successfully loaded data with shape: {df.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            st.error("Error loading data. Please check the file format.")
            return False

    def create_distribution_plot(self, column: str) -> Optional[go.Figure]:
        """Create distribution plot for a survey question."""
        if self.data is None:
            return None
            
        try:
            fig = px.histogram(
                self.data,
                x=column,
                title=f"{column} 점수 분포",
                labels={column: "점수", "count": "빈도"},
                nbins=20,
                text_auto=True
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
            return None

def main():
    st.set_page_config(
        page_title="강의평가 분석 대시보드",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("강의평가 분석 대시보드")
    
    analyzer = SurveyDataAnalyzer()
    uploaded_file = st.file_uploader("CSV 파일 선택", type="csv")
    
    if uploaded_file is not None and analyzer.load_data(uploaded_file):
        st.success("데이터를 성공적으로 불러왔습니다!")
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "분석 유형 선택",
            ["규모별 분석", "분포 분석"]
        )
        
            def display_size_range_analysis(st, analyzer):
        """Display size range analysis with detailed debugging."""
        st.header("규모별 강좌 분석")
        
        # Display debug information
        st.write("데이터 요약:")
        if analyzer.data is not None:
            st.write(f"- 총 강좌 수: {len(analyzer.data)}")
            st.write(f"- 응답자 수 범위: {analyzer.data['응답자 수'].min()} - {analyzer.data['응답자 수'].max()}")
            
            # Show response count distribution
            st.write("응답자 수 분포:")
            response_dist = analyzer.data['응답자 수'].value_counts().sort_index()
            st.write(response_dist)
        
        # Display each size range
        for size_range in analyzer.size_analyzer.size_ranges:
            st.subheader(size_range.title)
            st.caption(size_range.format_subtitle())
            
            if size_range.count > 0:
                if size_range.data is not None and not size_range.data.empty:
                    # Show raw data for debugging
                    st.write("상위 강좌 데이터:")
                    st.dataframe(size_range.data[['교과목명', '평균 점수', '응답자 수', '개설단과대학']])
                    
                    # Create and display chart
                    fig = analyzer.size_analyzer.create_size_range_chart(size_range)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display analysis points
                        st.subheader("분석")
                        analysis_points = analyzer.size_analyzer.analyze_top_courses(size_range)
                        for point in analysis_points:
                            st.markdown(f"- {point}")
                    else:
                        st.warning("차트 생성 중 오류가 발생했습니다.")
                else:
                    st.warning("데이터가 비어 있습니다.")
            else:
                st.warning("이 규모의 강좌가 없습니다.")
        
        elif analysis_type == "분포 분석":
            st.header("점수 분포 분석")
            
            # Select survey question
            survey_cols = [col for col in analyzer.data.columns if col.startswith('설문')]
            selected_col = st.selectbox("문항 선택", survey_cols)
            
            # Create and display distribution plot
            if selected_col:
                fig = analyzer.create_distribution_plot(selected_col)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display summary statistics
                    stats = analyzer.data[selected_col].describe().round(2)
                    st.write(f"**{selected_col} 통계 요약**")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("평균", f"{stats['mean']:.2f}")
                    with col2:
                        st.metric("표준편차", f"{stats['std']:.2f}")
                    with col3:
                        st.metric("최소값", f"{stats['min']:.2f}")
                    with col4:
                        st.metric("최대값", f"{stats['max']:.2f}")

if __name__ == "__main__":
    main()