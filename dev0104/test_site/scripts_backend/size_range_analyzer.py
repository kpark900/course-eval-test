#!/usr/bin/env python3
"""
File: size_range_analyzer.py
Version: 1.0.0
Created: 2024-01-01
Author: Claude 3.5 Sonnet (2024-01)

A module for analyzing course evaluation data based on class sizes.
Part of the Course Evaluation Analysis Dashboard.

Usage:
1. Save this file as 'size_range_analyzer.py' in your project directory
2. Install required packages:
   pip install pandas plotly

3. This module is imported by survey_analysis_app.py
   Do not run this file directly.

4. Directory structure should be:
   your_project_directory/
   ├── survey_analysis_app.py
   └── size_range_analyzer.py

Dependencies:
- pandas
- plotly.graph_objects
- logging
- typing

For more information, see the accompanying survey_analysis_app.py
"""

import pandas as pd
import plotly.graph_objects as go
import logging
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

class SizeRange:
    """Class to handle course size range definitions and analysis."""
    
    def __init__(self, min_size: int, max_size: int, title: str, color: str):
        self.min_size = min_size
        self.max_size = max_size
        self.title = title
        self.color = color
        self.data = None
        self.percentage = None
        self.count = None

    def format_subtitle(self) -> str:
        """Format the subtitle with course count and percentage."""
        if self.count is None or self.percentage is None:
            return ""
        return f"{self.count}개 강좌 ({self.percentage:.1f}%)"

class SizeRangeAnalyzer:
    """Analyzer for course size-based analysis."""

    def __init__(self):
        self.size_ranges = [
            SizeRange(10, 21, "소규모 강좌 (10-20명)", "#2563eb"),
            SizeRange(21, 51, "중소규모 강좌 (21-50명)", "#059669"),
            SizeRange(51, 101, "중대규모 강좌 (51-100명)", "#7c3aed"),
            SizeRange(101, None, "대규모 강좌 (100명 이상)", "#dc2626")
        ]

    def process_data(self, df: pd.DataFrame) -> None:
        """Process dataframe and categorize courses by size."""
        try:
            # Calculate total number of courses
            total_courses = len(df)
            logger.info(f"Processing {total_courses} total courses")
            
            # Log response count distribution
            logger.info("Response count distribution:")
            logger.info(df['응답자 수'].value_counts().sort_index())
            
            # Process each size range
            for size_range in self.size_ranges:
                logger.info(f"\nProcessing {size_range.title}")
                
                # Create mask for the current size range
                mask = (df['응답자 수'] >= size_range.min_size)
                if size_range.max_size is not None:
                    mask &= (df['응답자 수'] < size_range.max_size)
                
                # Filter courses for this range
                filtered_df = df[mask].copy()
                
                # Store basic statistics
                size_range.count = len(filtered_df)
                size_range.percentage = (size_range.count / total_courses) * 100 if total_courses > 0 else 0
                
                # Get top courses if any exist in this range
                if not filtered_df.empty:
                    # Sort by average score and get top 10
                    size_range.data = (filtered_df.sort_values('평균 점수', ascending=False)
                                     .head(10)
                                     .copy())  # Create a copy to avoid SettingWithCopyWarning
                    
                    # Log the data for debugging
                    logger.info(f"Filtered data shape: {filtered_df.shape}")
                    logger.info(f"Top courses:")
                    logger.info(size_range.data[['교과목명', '평균 점수', '응답자 수']].head())
                else:
                    size_range.data = None
                    logger.info("No courses found in this range")
                
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise

    def create_size_range_chart(self, size_range: SizeRange) -> Optional[go.Figure]:
        """Create a bar chart for a specific size range."""
        if size_range.data is None or len(size_range.data) == 0:
            return None

        try:
            fig = go.Figure()

            # Add main bar trace
            fig.add_trace(go.Bar(
                x=size_range.data['교과목명'],
                y=size_range.data['평균 점수'],
                marker_color=size_range.color,
                text=size_range.data['평균 점수'].round(2),
                textposition='outside',
            ))

            # Update layout with Korean labels and formatting
            fig.update_layout(
                title={
                    'text': f"{size_range.title}<br><sup>{size_range.format_subtitle()}</sup>",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': dict(size=20)
                },
                xaxis_tickangle=-45,
                xaxis_title="교과목명",
                yaxis_title="평균 점수",
                yaxis_range=[3, 5],  # Fixed range for consistency
                yaxis_dtick=0.5,     # Tick every 0.5
                height=600,
                showlegend=False,
                margin=dict(b=150),   # Bottom margin for rotated labels
                font=dict(size=12)    # Base font size
            )

            # Add hover template
            fig.update_traces(
                hovertemplate="<b>%{x}</b><br>" +
                             "평균 점수: %{y:.2f}<br>" +
                             "응답자 수: %{customdata[0]}<br>" +
                             "단과대학: %{customdata[1]}<extra></extra>",
                customdata=list(zip(
                    size_range.data['응답자 수'],
                    size_range.data['개설단과대학']
                ))
            )

            return fig

        except Exception as e:
            logger.error(f"Error creating chart for {size_range.title}: {str(e)}")
            return None

    def analyze_top_courses(self, size_range: SizeRange) -> List[str]:
        """Generate analysis points for top courses in a size range."""
        if size_range.data is None or len(size_range.data) == 0:
            return []

        try:
            analysis = []

            # Score range analysis
            min_score = size_range.data['평균 점수'].min()
            max_score = size_range.data['평균 점수'].max()
            analysis.append(f"점수 범위: {min_score:.2f}-{max_score:.2f}")

            # College distribution analysis
            college_counts = size_range.data['개설단과대학'].value_counts()
            top_college = college_counts.index[0]
            college_count = college_counts[top_college]
            analysis.append(f"가장 많은 단과대학: {top_college} ({college_count}개 강좌)")

            # Course type analysis
            course_types = self._analyze_course_types(size_range.data['교과목명'].tolist())
            if course_types:
                analysis.append(f"주요 강좌 유형: {course_types}")

            # Course characteristics
            characteristics = self._analyze_course_characteristics(size_range.data)
            if characteristics:
                analysis.append(characteristics)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing top courses: {str(e)}")
            return []

    def _analyze_course_types(self, course_names: List[str]) -> str:
        """Analyze common patterns in course names."""
        keywords = {
            '전공': 0, '교양': 0, '실습': 0, '이론': 0,
            '기초': 0, '심화': 0, '특강': 0
        }
        
        for course in course_names:
            for keyword in keywords:
                if keyword in course:
                    keywords[keyword] += 1
        
        # Filter keywords that appear at least once
        relevant_types = [k for k, v in keywords.items() if v > 0]
        
        if relevant_types:
            return ', '.join(relevant_types)
        return "다양한 유형의 강좌"

    def _analyze_course_characteristics(self, data: pd.DataFrame) -> str:
        """Analyze general characteristics of the courses."""
        try:
            avg_responses = data['응답자 수'].mean()
            max_responses = data['응답자 수'].max()
            
            return f"평균 응답자 수: {avg_responses:.1f}명, 최대 응답자 수: {max_responses:.0f}명"
            
        except Exception as e:
            logger.error(f"Error analyzing course characteristics: {str(e)}")
            return ""