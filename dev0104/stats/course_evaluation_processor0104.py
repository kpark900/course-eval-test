# File: course_evaluation_processor.py
# Version: 1.0.0
# Created: 2024-01-04
# Author: Claude 3.5 Sonnet (2024-01-04)

"""
Course Evaluation Data Processing Script
--------------------------------------

This script processes the course evaluation data from CSV files and generates
analysis results. It handles data cleaning, transformation, and basic statistical
analysis of course evaluation responses.

Usage:
1. Place this script in the same directory as your input CSV file
2. Ensure required packages are installed:
   pip install pandas numpy scipy matplotlib seaborn

3. Run the script:
   python course_evaluation_processor.py

Required files:
- courseeval24_1 ProcessedDataanon.csv in the same directory

Output:
- Processed CSV file with computed metrics
- Summary statistics in console output
- Basic visualizations (if display available)
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

infile = '../data_input/anon-course-eval-24_1Data-cp.csv'

class CourseEvalProcessor:
    def __init__(self, file_path=infile):
        """Initialize the processor with file path."""
        self.file_path = file_path
        self.data = None
        self.summary_stats = {}
        
    def load_data(self):
        """Load and perform initial data validation."""
        try:
            self.data = pd.read_csv(self.file_path)
            print(f"Successfully loaded {len(self.data)} records")
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
            
    def clean_data(self):
        """Clean and prepare data for analysis."""
        if self.data is None:
            print("No data loaded. Please load data first.")
            return False
            
        # Remove any leading/trailing whitespace
        string_columns = self.data.select_dtypes(include=['object']).columns
        for col in string_columns:
            self.data[col] = self.data[col].str.strip()
            
        # Convert survey responses to numeric
        survey_cols = [f'Survey{i}' for i in range(1, 8)]
        for col in survey_cols:
            self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
        # Add computed columns
        self.data['AvgSurveyScore'] = self.data[survey_cols].mean(axis=1)
        self.data['ResponseCompleteness'] = self.data[survey_cols].notna().mean(axis=1)
        
        print("Data cleaning completed")
        return True
        
    def compute_statistics(self):
        """Compute key statistics for the dataset."""
        if self.data is None:
            print("No data loaded. Please load data first.")
            return False
            
        # Basic statistics
        self.summary_stats['total_records'] = len(self.data)
        self.summary_stats['unique_courses'] = self.data['CourseCode'].nunique()
        self.summary_stats['unique_professors'] = self.data['ProfessorID'].nunique()
        
        # Survey statistics
        survey_cols = [f'Survey{i}' for i in range(1, 8)]
        self.summary_stats['survey_means'] = self.data[survey_cols].mean().to_dict()
        self.summary_stats['survey_medians'] = self.data[survey_cols].median().to_dict()
        
        # College-wise statistics
        self.summary_stats['college_stats'] = (
            self.data.groupby('College')['AvgSurveyScore']
            .agg(['count', 'mean', 'std'])
            .round(2)
            .to_dict('index')
        )
        
        print("Statistics computation completed")
        return True
        
    def generate_summary_report(self):
        """Generate a text summary of the analysis."""
        if not self.summary_stats:
            print("No statistics computed. Please compute statistics first.")
            return False
            
        report = [
            "Course Evaluation Analysis Summary",
            "================================",
            f"Total Records: {self.summary_stats['total_records']:,}",
            f"Unique Courses: {self.summary_stats['unique_courses']:,}",
            f"Unique Professors: {self.summary_stats['unique_professors']:,}",
            "",
            "Survey Score Statistics",
            "---------------------"
        ]
        
        for q, score in self.summary_stats['survey_means'].items():
            report.append(f"{q}: Mean = {score:.2f}, Median = {self.summary_stats['survey_medians'][q]:.2f}")
            
        report.extend([
            "",
            "College-wise Statistics",
            "---------------------"
        ])
        
        for college, stats in self.summary_stats['college_stats'].items():
            report.append(
                f"{college}: n={stats['count']:,}, Mean={stats['mean']:.2f}, SD={stats['std']:.2f}"
            )
            
        return "\n".join(report)
        
    def save_processed_data(self, output_path=None):
        """Save processed data to CSV."""
        if self.data is None:
            print("No data to save. Please load and process data first.")
            return False
            
        if output_path is None:
            output_path = Path(self.file_path).stem + "_processed.csv"
            
        try:
            self.data.to_csv(output_path, index=False)
            print(f"Processed data saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving data: {str(e)}")
            return False

def main():
    """Main function to demonstrate usage."""
    processor = CourseEvalProcessor()
    
    if processor.load_data():
        processor.clean_data()
        processor.compute_statistics()
        
        # Generate and print summary report
        print("\n" + processor.generate_summary_report())
        
        # Save processed data
        processor.save_processed_data()
        
if __name__ == "__main__":
    main()
