#!/usr/bin/env python3
# File: calculate_metrics.py
# Version: 2.1
# Created by: Claude 3.5 Sonnet (2024-01-03)
# Updated by: chatGPT-4o (2025-01-04)
# Usage: Place in root directory alongside the input CSV file (default: ProcessedData500-sample-anon.csv)
#        Run: python3 calculate_metrics.py

import pandas as pd
import numpy as np
import os
import logging
import json
from typing import Dict, List
from collections import Counter

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
        self.required_columns = self.survey_cols + ["College", "Campus", "GroupCode", "CourseCode", "CourseName"]
        self.optional_columns = ["Department"]

        missing_cols = [col for col in self.required_columns if col not in self.df.columns]
        if missing_cols:
            logging.error(f"Missing required columns: {missing_cols}")
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Log missing optional columns
        for col in self.optional_columns:
            if col not in self.df.columns:
                logging.warning(f"Optional column missing: {col}. Some calculations will be skipped.")

        # Ensure numeric data in survey columns
        self.df[self.survey_cols] = self.df[self.survey_cols].apply(pd.to_numeric, errors='coerce')

    def _convert_keys_to_str(self, obj):
        """Recursively convert all dictionary keys to strings."""
        if isinstance(obj, dict):
            return {str(k): self._convert_keys_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_keys_to_str(item) for item in obj]
        return obj

    def _flatten_dict(self, d):
        """Convert multi-level dict to flattened dict with string keys."""
        flat_dict = {}
        for key1, value1 in d.items():
            if isinstance(value1, dict):
                for key2, value2 in value1.items():
                    flat_key = f"{key1}_{key2}" if isinstance(key1, str) else f"{str(key1)}_{key2}"
                    flat_dict[flat_key] = value2
            else:
                flat_dict[str(key1)] = value1
        return flat_dict

    def calculate_and_save_all_metrics(self, output_file: str):
        """Calculate and save all metrics into a single output file."""
        # Metrics storage
        combined_metrics = {}

        # Evaluation metrics
        eval_metrics = self.calculate_evaluation_metrics()
        combined_metrics['evaluation'] = eval_metrics

        # Performance metrics
        perf_metrics = self.calculate_performance_metrics()
        combined_metrics['performance'] = perf_metrics

        # Demographic metrics
        demo_metrics = self.calculate_demographic_metrics()
        combined_metrics['demographics'] = demo_metrics

        # Additional metrics
        additional_metrics = self.calculate_additional_metrics()
        combined_metrics['additional'] = additional_metrics

        # Class size categories
        class_sizes = self.classify_courses_by_size()
        combined_metrics['class_sizes'] = class_sizes.to_dict(orient='records')

        # Recursively convert all keys to strings
        combined_metrics = self._convert_keys_to_str(combined_metrics)

        # Save to a single JSON file using json.dump
        with open(output_file, 'w') as f:
            json.dump(combined_metrics, f, indent=4)
        logging.info(f"Saved all metrics to {output_file}")

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
        gpa_scale = 4.5 / 5
        self.df['gpa_equiv'] = self.df[self.survey_cols].mean(axis=1) * gpa_scale

        # Flatten multi-index results
        college_perf = self.df.groupby('College').agg({
            'gpa_equiv': ['mean', 'std', 'count']
        }).round(3)
        college_perf.columns = [f'gpa_{col[1]}' for col in college_perf.columns]
        
        course_perf = self.df.groupby('GroupCode').agg({
            'gpa_equiv': ['mean', 'std', 'count']
        }).round(3)
        course_perf.columns = [f'gpa_{col[1]}' for col in course_perf.columns]

        metrics = {
            'overall': {
                'mean_gpa': float(self.df['gpa_equiv'].mean()),
                'std_gpa': float(self.df['gpa_equiv'].std())
            },
            'college_performance': college_perf.to_dict('index'),
            'course_performance': course_perf.to_dict('index')
        }
        return metrics

    def calculate_demographic_metrics(self) -> Dict:
        college_dist = self.df.groupby('College').agg({
            'GroupCode': 'nunique',
            'CourseCode': 'nunique'
        })
        college_dist.columns = ['section_count', 'course_count']
        
        metrics = {
            'college_distribution': college_dist.to_dict('index'),
            'campus_distribution': self.df.groupby('Campus').size().to_dict(),
            'course_size': {str(k): v for k, v in 
                          self.df.groupby('GroupCode').size().describe().round(2).to_dict().items()}
        }
        return metrics

    def classify_courses_by_size(self) -> pd.DataFrame:
        """Classify courses into size categories based on the number of rows (students)."""
        course_sizes = self.df.groupby('GroupCode').size()
        result = pd.DataFrame({
            'GroupCode': course_sizes.index,
            'Students': course_sizes.values,
            'Size': pd.cut(course_sizes.values,
                          bins=[0, 15, 30, 75, float('inf')],
                          labels=['Small', 'Medium', 'Large', 'Very Large'])
        })
        return result

    def calculate_additional_metrics(self) -> Dict:
        metrics = {
            'average_scores': {
                col: {
                    'by_department': self.df.groupby('Department')[col].mean().round(2).to_dict() if 'Department' in self.df.columns else {},
                    'by_college': self.df.groupby('College')[col].mean().round(2).to_dict(),
                    'by_humanities_sciences': self.df.groupby('Campus')[col].mean().round(2).to_dict()
                } for col in self.survey_cols
            },
            'top_10_colleges': {
                col: self.df.groupby('College')[col].mean().sort_values(ascending=False).head(10).round(2).to_dict()
                for col in self.survey_cols
            },
            'top_10_courses': {
                col: self.df.groupby('CourseCode')[col].mean().sort_values(ascending=False).head(10).round(2).to_dict()
                for col in self.survey_cols
            },
            'course_name_keywords': Counter(
                word.lower()
                for name in self.df['CourseName']
                for word in str(name).split()
            ).most_common(10)
        }
        return metrics

def main():
    setup_logging()

    input_file = 'ProcessedData500-sample-anon.csv'
    output_file = 'computed_metrics/all_metrics.json'

    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Initialize calculator and calculate all metrics
    calculator = MetricsCalculator(input_file)
    calculator.calculate_and_save_all_metrics(output_file)

    # Completion message
    logging.info("All metrics have been calculated and saved successfully.")

if __name__ == "__main__":
    main()
