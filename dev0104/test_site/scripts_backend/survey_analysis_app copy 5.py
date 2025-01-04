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

# [Previous ColumnMapper class remains the same]
# [Previous SurveyDataAnalyzer class remains mostly the same, with these additions:]

class SurveyDataAnalyzer:
    def __init__(self):
        self.data = None
        self.mapper = ColumnMapper()
        self.column_types = None
        self.size_analyzer = SizeRangeAnalyzer()

    def load_data(self, file) -> bool:
        try:
            df = pd.read_csv(file)
            
            # Convert survey columns to numeric
            survey_cols = [col for col in df.columns if col.startswith('설문')]
            for col in survey_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calculate average score
            df['평균 점수'] = df[survey_cols].mean(axis=1)
            
            # Calculate response count
            df['응답자 수'] = df[survey_cols].notna().sum(axis=1)
            
            # Store processed data
            self.data = df
            
            # Process size-based analysis
            self.size_analyzer.process_data(df)
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            st.error("Error loading data. Please check the file format.")
            return False

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
            ["규모별 분석", "기술통계", "분포 분석"]
        )
        
        if analysis_type == "규모별 분석":
            st.header("규모별 강좌 분석")
            
            # Display visualizations for each size range
            for size_range in analyzer.size_analyzer.size_ranges:
                st.subheader(size_range.title)
                st.caption(size_range.format_subtitle())
                
                fig = analyzer.size_analyzer.create_size_range_chart(size_range)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display analysis points
                    st.subheader("분석")
                    analysis_points = analyzer.size_analyzer.analyze_top_courses(size_range)
                    for point in analysis_points:
                        st.markdown(f"- {point}")
                else:
                    st.warning("이 규모의 강좌가 없습니다.")
        
        elif analysis_type == "기술통계":
            # [Previous statistical analysis code]
            pass
        
        elif analysis_type == "분포 분석":
            # [Previous distribution analysis code]
            pass

if __name__ == "__main__":
    main()