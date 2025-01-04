import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import logging
from typing import Dict, List, Optional, Union
from plotly.graph_objs import Figure

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
        self.data: Optional[pd.DataFrame] = None
        self.mapper = ColumnMapper()
        self.column_types: Optional[Dict] = None
        self.required_columns = {
            'year', 'semester', 'campus', 'college', 'course_name'
        }
        self.survey_questions = {f'q{i}' for i in range(1, 8)}
    
    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        """Validate the input dataframe has required columns and structure."""
        english_columns = set(self.mapper.to_english(df.columns))
        missing_required = self.required_columns - english_columns
        missing_questions = self.survey_questions - english_columns
        
        if missing_required:
            logger.error(f"Missing required columns: {missing_required}")
            return False
        
        if missing_questions:
            logger.error(f"Missing survey questions: {missing_questions}")
            return False
            
        return True
    
    def load_data(self, file) -> bool:
        """Load and validate survey data from uploaded file."""
        try:
            # Read CSV and drop sensitive columns
            df = pd.read_csv(file)
            
            # Drop sensitive columns and anything after q7
            columns_to_keep = [col for col in df.columns 
                             if col in ['년도', '학기', '캠퍼스', '개설단과대학', 
                                      '교과목명', '설문1', '설문2', '설문3', 
                                      '설문4', '설문5', '설문6', '설문7']]
            df = df[columns_to_keep]
            
            if not self.validate_dataframe(df):
                st.error("입력 파일의 형식이 올바르지 않습니다. 필수 열이 누락되었습니다.")
                return False
            
            # Convert column names to English
            df.columns = self.mapper.to_english(df.columns)
            
            # Convert survey questions to numeric
            for col in self.survey_questions:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Format year without comma
            df['year'] = df['year'].astype(int)
            
            # Store processed dataframe
            self.data = df
            self.column_types = self.detect_column_types()
            
            logger.info(f"Successfully loaded data with shape: {df.shape}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            st.error(f"데이터 로드 중 오류가 발생했습니다: {str(e)}")
            return False
    
    def detect_column_types(self) -> Dict:
        """Detect column types from the dataframe."""
        if self.data is None:
            return {}
            
        return {
            'survey': sorted(list(self.survey_questions)),
            'demographic': ['campus', 'college', 'course_name'],
            'grouping_options': {
                'campus': '캠퍼스',
                'college': '개설단과대학',
                'course_name': '교과목명'
            }
        }
    
    def calculate_descriptive_stats(self, group_by: Optional[str] = None) -> pd.DataFrame:
        """Calculate descriptive statistics for survey responses."""
        if self.data is None or self.column_types is None:
            return pd.DataFrame()
            
        try:
            survey_cols = self.column_types['survey']
            
            if group_by and group_by != "없음":
                stats_df = (self.data.groupby(group_by)[survey_cols]
                           .agg(['count', 'mean', 'median', 'std', 'min', 'max'])
                           .round(2)
                           .sort_values((survey_cols[0], 'count'), ascending=False))
            else:
                stats_df = (self.data[survey_cols]
                           .agg(['count', 'mean', 'median', 'std', 'min', 'max'])
                           .round(2))
            
            # Convert column names to Korean
            if isinstance(stats_df.columns, pd.MultiIndex):
                stats_df.columns = pd.MultiIndex.from_tuples(
                    [(self.mapper.to_korean(col[0]), col[1]) 
                     for col in stats_df.columns]
                )
            
            return stats_df
            
        except Exception as e:
            logger.error(f"Error calculating descriptive stats: {str(e)}")
            return pd.DataFrame()
    
    def get_top_courses(self, n: int = 5) -> Optional[pd.DataFrame]:
        """Get top n courses by average survey score."""
        if self.data is None or self.column_types is None:
            return None
            
        try:
            survey_cols = self.column_types['survey']
            
            # Calculate mean scores and response counts
            course_stats = (self.data.groupby('course_name').agg({
                col: ['mean', 'count'] for col in survey_cols
            }))
            
            # Calculate overall average across all questions
            avg_scores = course_stats.xs('mean', axis=1, level=1).mean(axis=1)
            response_counts = course_stats.xs('count', axis=1, level=1).mean(axis=1)
            
            # Combine into final dataframe
            top_courses = pd.DataFrame({
                '평균 점수': avg_scores,
                '응답자 수': response_counts.round().astype(int)  # Round response count to integers
            }).round(2)
            
            return top_courses.sort_values('평균 점수', ascending=False).head(n)
            
        except Exception as e:
            logger.error(f"Error calculating top courses: {str(e)}")
            return None
    
    def create_distribution_plot(self, column: str) -> Optional[Figure]:
        """Create distribution plot for a survey question."""
        if self.data is None:
            return None
            
        try:
            fig = px.histogram(
                self.data,
                x=column,
                title=f"{self.mapper.to_korean(column)} 점수 분포",
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
    st.write("분석할 CSV 파일을 업로드해주세요")
    
    analyzer = SurveyDataAnalyzer()
    uploaded_file = st.file_uploader("CSV 파일 선택", type="csv")
    
    if uploaded_file is not None:
        if analyzer.load_data(uploaded_file):
            st.success("데이터를 성공적으로 불러왔습니다!")
            
            # Data preview
            st.subheader("데이터 미리보기")
            if analyzer.data is not None:
                st.dataframe(analyzer.data.head())
            
            # Top courses analysis
            st.header("최고 평점 강좌 분석")
            top_courses = analyzer.get_top_courses()
            
            if top_courses is not None:
                st.subheader("상위 5개 강좌 상세 정보")
                st.dataframe(top_courses)
            
            # Analysis options
            analysis_type = st.selectbox(
                "분석 유형 선택",
                ["기술통계", "분포 분석"]
            )
            
            if analysis_type == "기술통계":
                st.header("기술통계 분석")
                
                if analyzer.column_types:
                    group_by_options = ["없음"] + list(analyzer.column_types['grouping_options'].values())
                    group_by = st.selectbox(
                        "그룹화 기준 (선택사항)",
                        group_by_options
                    )
                    
                    # Map selected option back to column name
                    if group_by != "없음":
                        group_by_col = next(
                            (k for k, v in analyzer.column_types['grouping_options'].items() 
                             if v == group_by),
                            None
                        )
                    else:
                        group_by_col = None
                    
                    stats_df = analyzer.calculate_descriptive_stats(group_by_col)
                    
                    if not stats_df.empty:
                        st.dataframe(stats_df)
                        
                        csv = stats_df.to_csv(encoding='utf-8-sig').encode('utf-8-sig')
                        st.download_button(
                            "통계 데이터 CSV 다운로드",
                            csv,
                            "survey_statistics.csv",
                            "text/csv",
                            key='download-csv'
                        )
            
            elif analysis_type == "분포 분석":
                st.header("점수 분포 분석")
                
                if analyzer.column_types:
                    question_options = [
                        analyzer.mapper.to_korean(col) 
                        for col in analyzer.column_types['survey']
                    ]
                    selected_question = st.selectbox(
                        "문항 선택",
                        question_options,
                        key='dist_question_select'
                    )
                    
                    selected_col = next(
                        col for col in analyzer.column_types['survey']
                        if analyzer.mapper.to_korean(col) == selected_question
                    )
                    
                    dist_fig = analyzer.create_distribution_plot(selected_col)
                    if dist_fig:
                        st.plotly_chart(dist_fig, use_container_width=True)
                        
                        if analyzer.data is not None:
                            stats = analyzer.data[selected_col].describe().round(2)
                            st.write(f"**{selected_question} 통계 요약**")
                            
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