#!/usr/bin/env python3
# File: calculate_metrics.py
# Version: 1.2
# Created by: Claude 3.5 Sonnet (2024-01-03)
# Updated by: chatGPT-4o (2025-01-04)
# Usage: Place in root directory alongside the input CSV file (default: ProcessedData500-sample-anon.csv)
#        Run: python3 calculate_metrics.py

import pandas as pd
import numpy as np
import os
import logging
from typing import Dict, List

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

class MetricsCalculator:
    def __init__(self, data_file: str):
        if not os.path.exists(data_file):
            logging.error(f"Data file {data_file} not found.")
            raise FileNotFoundError(f"Data file {data_file} not found.")

        self.df = pd.read_csv(data_file)

        # Expected columns
        self.survey_cols = [f"Survey{i}" for i in range(1, 8)]
        self.required_columns = self.survey_cols + ["College", "Campus", "GroupCode", "CourseCode"]

        missing_cols = [col for col in self.required_columns if col not in self.df.columns]
        if missing_cols:
            logging.error(f"Missing required columns: {missing_cols}")
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Ensure numeric data in survey columns
        self.df[self.survey_cols] = self.df[self.survey_cols].apply(pd.to_numeric, errors='coerce')

    def calculate_evaluation_metrics(self) -> Dict:
        metrics = {
            'overall': {
                'mean': self.df[self.survey_cols].mean().mean(),
                'response_rate': (self.df[self.survey_cols].notna().mean().mean() * 100).round(2)
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
                'high': (self.df[self.survey_cols] >= 4.5).mean().mean() * 100,
                'medium': ((self.df[self.survey_cols] >= 3) & (self.df[self.survey_cols] < 4.5)).mean().mean() * 100,
                'low': (self.df[self.survey_cols] < 3).mean().mean() * 100
            },
            'college_scores': self.df.groupby('College')[self.survey_cols].mean().round(2).to_dict()
        }
        return metrics

    def calculate_performance_metrics(self) -> Dict:
        gpa_scale = 4.5 / 5  # Updated to reflect 0-5 survey scale
        self.df['gpa_equiv'] = self.df[self.survey_cols].mean(axis=1) * gpa_scale

        metrics = {
            'overall': {
                'mean_gpa': self.df['gpa_equiv'].mean(),
                'std_gpa': self.df['gpa_equiv'].std()
            },
            'college_performance': self.df.groupby('College').agg({
                'gpa_equiv': ['mean', 'std', 'count']
            }).round(3).to_dict(),
            'course_performance': self.df.groupby('GroupCode').agg({
                'gpa_equiv': ['mean', 'std', 'count']
            }).round(3).to_dict()
        }
        return metrics

    def calculate_demographic_metrics(self) -> Dict:
        metrics = {
            'college_distribution': self.df.groupby('College').agg({
                'GroupCode': 'nunique',
                'CourseCode': 'nunique'
            }).rename(columns={
                'GroupCode': 'section_count',
                'CourseCode': 'course_count'
            }).to_dict(),
            'campus_distribution': self.df.groupby('Campus').size().to_dict(),
            'course_size': self.df.groupby('GroupCode').size().describe().round(2).to_dict()
        }
        return metrics

    def generate_summary_report(self) -> str:
        eval_metrics = self.calculate_evaluation_metrics()
        perf_metrics = self.calculate_performance_metrics()
        demo_metrics = self.calculate_demographic_metrics()

        summary = [
            "Summary Report",
            "===============",
            f"Total Students: {len(self.df)}",
            f"Unique Courses: {self.df['CourseCode'].nunique()}",
            f"Course Sections: {self.df['GroupCode'].nunique()}",
            f"Overall Satisfaction: {eval_metrics['overall']['mean']:.2f}/5",
            f"Average GPA Equivalent: {perf_metrics['overall']['mean_gpa']:.2f}/4.5",
            "\nCollege Distribution",
            "-------------------"
        ]

        for college, stats in demo_metrics['college_distribution']['section_count'].items():
            summary.append(f"{college}: {stats} sections")

        return '\n'.join(summary)

def save_metrics_to_csv(metrics_dict: Dict, filename: str):
    """Helper function to save metrics to CSV safely."""
    if isinstance(metrics_dict, dict):
        # Check if the values are scalars or dicts/lists
        if all(isinstance(v, (int, float, str)) for v in metrics_dict.values()):
            # Convert scalar dictionary to a DataFrame with keys as the index
            df = pd.DataFrame.from_dict(metrics_dict, orient='index', columns=['Value']).reset_index()
            df.rename(columns={'index': 'Metric'}, inplace=True)
        else:
            df = pd.DataFrame(metrics_dict).T.reset_index()
    else:
        df = pd.DataFrame(metrics_dict)
    df.to_csv(filename, index=False)

def main():
    setup_logging()

    input_file = 'ProcessedData500-sample-anon.csv'
    calculator = MetricsCalculator(input_file)

    # Create output directory
    output_dir = 'computed_metrics'
    os.makedirs(output_dir, exist_ok=True)

    # Calculate and save all metrics
    evaluation_metrics = calculator.calculate_evaluation_metrics()
    performance_metrics = calculator.calculate_performance_metrics()
    demographic_metrics = calculator.calculate_demographic_metrics()

    # Save evaluation metrics
    save_metrics_to_csv(evaluation_metrics['per_question'], f'{output_dir}/evaluation_per_question.csv')
    save_metrics_to_csv(evaluation_metrics['score_distribution'], f'{output_dir}/evaluation_distribution.csv')
    pd.DataFrame(evaluation_metrics['college_scores']).to_csv(f'{output_dir}/evaluation_by_college.csv')

    # Save performance metrics
    save_metrics_to_csv(performance_metrics['overall'], f'{output_dir}/performance_overall.csv')
    pd.DataFrame(performance_metrics['college_performance']).to_csv(f'{output_dir}/performance_by_college.csv')
    pd.DataFrame(performance_metrics['course_performance']).to_csv(f'{output_dir}/performance_by_course.csv')

    # Save demographic metrics
    pd.DataFrame(demographic_metrics['college_distribution']).to_csv(f'{output_dir}/demographics_college.csv')
    save_metrics_to_csv(demographic_metrics['campus_distribution'], f'{output_dir}/demographics_campus.csv')
    save_metrics_to_csv(demographic_metrics['course_size'], f'{output_dir}/demographics_course_size.csv')

    # Generate and save summary report
    with open(f'{output_dir}/summary_report.txt', 'w') as f:
        f.write(calculator.generate_summary_report())

if __name__ == "__main__":
    main()
