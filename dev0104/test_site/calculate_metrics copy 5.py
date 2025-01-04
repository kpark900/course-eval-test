#!/usr/bin/env python3
# File: calculate_metrics.py
# Version: 1.0
# Created by: Claude 3.5 Sonnet (2024-01-03)
# Usage: Place in root directory alongside ProcessedData500-sample-anon.csv
#        Run: python3 calculate_metrics.py

import pandas as pd
import numpy as np
from typing import Dict, List
import os

class MetricsCalculator:
    def __init__(self, data_file: str):
        self.df = pd.read_csv(data_file)
        self.survey_cols = [f'Survey{i}' for i in range(1, 8)]

    def calculate_evaluation_metrics(self) -> Dict:
        """Calculate metrics for evaluation.html"""
        metrics = {
            'overall': {
                'mean': self.df[self.survey_cols].mean().mean(),
                'response_rate': (self.df[self.survey_cols].notna().mean() * 100).round(2)
            },
            'per_question': {
                col: {
                    'mean': self.df[col].mean(),
                    'median': self.df[col].median(),
                    'std': self.df[col].std(),
                    'response_rate': (self.df[col].notna().mean() * 100).round(2)
                } for col in self.survey_cols
            },
            'score_distribution': {
                'high': (self.df[self.survey_cols].ge(9).mean() * 100).round(2),
                'medium': (self.df[self.survey_cols].between(7, 8).mean() * 100).round(2),
                'low': (self.df[self.survey_cols].le(6).mean() * 100).round(2)
            },
            'college_scores': self.df.groupby('College')[self.survey_cols].mean().round(2)
        }
        return metrics

    def calculate_performance_metrics(self) -> Dict:
        """Calculate metrics for performance.html"""
        # Convert survey scores to GPA scale (assuming 10-point to 4.5 scale)
        gpa_scale = 4.5 / 10
        self.df['gpa_equiv'] = self.df[self.survey_cols].mean(axis=1) * gpa_scale
        
        metrics = {
            'overall': {
                'mean_gpa': self.df['gpa_equiv'].mean(),
                'std_gpa': self.df['gpa_equiv'].std()
            },
            'college_performance': self.df.groupby('College').agg({
                'gpa_equiv': ['mean', 'std', 'count']
            }).round(3),
            'course_performance': self.df.groupby('GroupCode').agg({
                'gpa_equiv': ['mean', 'std', 'count']
            }).round(3)
        }
        return metrics

    def calculate_demographic_metrics(self) -> Dict:
        """Calculate metrics for demographics.html"""
        metrics = {
            'college_distribution': self.df.groupby('College').agg({
                'GroupCode': 'nunique',
                'CourseCode': 'nunique'
            }).rename(columns={
                'GroupCode': 'section_count',
                'CourseCode': 'course_count'
            }),
            'campus_distribution': self.df.groupby('Campus').size().to_dict(),
            'course_size': self.df.groupby('GroupCode').size().describe().round(2)
        }
        return metrics

    def generate_summary_report(self) -> str:
        """Generate a text summary of key metrics"""
        eval_metrics = self.calculate_evaluation_metrics()
        perf_metrics = self.calculate_performance_metrics()
        demo_metrics = self.calculate_demographic_metrics()
        
        summary = [
            "Summary Report",
            "=============",
            f"Total Students: {len(self.df)}",
            f"Unique Courses: {self.df['CourseCode'].nunique()}",
            f"Course Sections: {self.df['GroupCode'].nunique()}",
            f"Overall Satisfaction: {eval_metrics['overall']['mean']:.2f}/10",
            f"Average GPA Equivalent: {perf_metrics['overall']['mean_gpa']:.2f}/4.5",
            "\nCollege Distribution",
            "-------------------"
        ]
        
        for college, stats in demo_metrics['college_distribution'].iterrows():
            summary.append(f"{college}: {stats['section_count']} sections")
            
        return '\n'.join(summary)

def main():
    calculator = MetricsCalculator('ProcessedData500-sample-anon.csv')
    
    # Generate all metrics
    evaluation_metrics = calculator.calculate_evaluation_metrics()
    performance_metrics = calculator.calculate_performance_metrics()
    demographic_metrics = calculator.calculate_demographic_metrics()
    
    # Save metrics to files
    os.makedirs('computed_metrics', exist_ok=True)
    
    # Save as CSV files
    for name, metrics in {
        'evaluation': evaluation_metrics,
        'performance': performance_metrics,
        'demographics': demographic_metrics
    }.items():
        pd.DataFrame(metrics).to_csv(f'computed_metrics/{name}_metrics.csv')
    
    # Generate and save summary report
    with open('computed_metrics/summary_report.txt', 'w') as f:
        f.write(calculator.generate_summary_report())

if __name__ == "__main__":
    main()
