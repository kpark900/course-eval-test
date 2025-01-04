# File: survey_score_analyzer.py
# Version: 1.0.0
# Created: 2024-01-04
# Author: Claude 3.5 Sonnet (2024-01-04)

"""
Enhanced Survey Score Analysis Script
-----------------------------------

This script performs detailed analysis of survey scores from course evaluation data,
including breakdowns by individual questions and aggregated scores across various
dimensions (course, college, campus).

Usage:
1. Place this script in the same directory as your input CSV file
2. Ensure required packages are installed:
   pip install pandas numpy openpyxl

3. Run the script:
   python survey_score_analyzer.py

Required files:
- anon-course-eval-24_1Data-cp.csv in the ../data_input/ directory

Output:
- survey_analysis.xlsx with multiple sheets for different analyses
- Detailed console output with summary statistics
"""

import pandas as pd
import numpy as np
from pathlib import Path

class SurveyScoreAnalyzer:
    def __init__(self, input_file='../data_input/anon-course-eval-24_1Data-cp.csv'):
        """Initialize the analyzer with input file path."""
        self.input_file = input_file
        self.data = None
        self.survey_cols = [f'Survey{i}' for i in range(1, 8)]
        self.results = {}
        
    def load_data(self):
        """Load and perform initial data validation."""
        try:
            self.data = pd.read_csv(self.input_file)
            # Convert survey columns to numeric, handling any non-numeric values
            for col in self.survey_cols:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
            print(f"Successfully loaded {len(self.data):,} records")
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False

    def calculate_survey_averages(self):
        """Calculate average scores for individual and combined surveys."""
        if self.data is None:
            return False

        # Add combined survey score
        self.data['SurveyCombined'] = self.data[self.survey_cols].mean(axis=1)

        # Initialize results dictionary
        analysis_levels = {
            'course': 'CourseName',
            'college': 'College',
            'campus': 'Campus'
        }

        for level, column in analysis_levels.items():
            # Individual survey questions
            for survey_col in self.survey_cols:
                key = f'{level}_{survey_col}'
                self.results[key] = (
                    self.data.groupby(column)[survey_col]
                    .agg(['count', 'mean', 'std'])
                    .round(3)
                    .reset_index()
                )

            # Combined survey score
            key = f'{level}_combined'
            self.results[key] = (
                self.data.groupby(column)['SurveyCombined']
                .agg(['count', 'mean', 'std'])
                .round(3)
                .reset_index()
            )

        return True

    def save_results(self, output_file='survey_analysis.xlsx'):
        """Save all results to an Excel file with multiple sheets."""
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Save each analysis to a separate sheet
                for key, df in self.results.items():
                    sheet_name = key[:31]  # Excel sheet names limited to 31 chars
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Create summary sheet
                self._create_summary_sheet(writer)

            print(f"\nResults saved to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            return False

    def _create_summary_sheet(self, writer):
        """Create a summary sheet with key statistics."""
        summary = []

        # Overall statistics
        overall_stats = {
            'Total Records': len(self.data),
            'Unique Courses': self.data['CourseName'].nunique(),
            'Unique Colleges': self.data['College'].nunique(),
            'Campus Count': self.data['Campus'].nunique()
        }

        # Add overall survey statistics
        for col in self.survey_cols + ['SurveyCombined']:
            stats = self.data[col].agg(['mean', 'std']).round(3)
            overall_stats.update({
                f'{col} Mean': stats['mean'],
                f'{col} Std': stats['std']
            })

        # Convert to DataFrame and save
        summary_df = pd.DataFrame.from_dict(overall_stats, orient='index', 
                                          columns=['Value'])
        summary_df.to_excel(writer, sheet_name='Summary')

    def print_summary(self):
        """Print summary statistics to console."""
        print("\nSurvey Analysis Summary")
        print("======================")
        
        print("\nOverall Statistics:")
        print(f"Total Records: {len(self.data):,}")
        print(f"Unique Courses: {self.data['CourseName'].nunique():,}")
        print(f"Unique Colleges: {self.data['College'].nunique():,}")
        
        print("\nSurvey Score Averages:")
        for col in self.survey_cols + ['SurveyCombined']:
            mean = self.data[col].mean()
            std = self.data[col].std()
            print(f"{col}: Mean = {mean:.3f} (±{std:.3f})")

        print("\nTop Performing Colleges (Combined Score):")
        top_colleges = (
            self.results['college_combined']
            .nlargest(5, 'mean')
            [['College', 'count', 'mean']]
        )
        print(top_colleges.to_string(index=False))

def main():
    """Main function to run the analysis."""
    analyzer = SurveyScoreAnalyzer()
    
    if analyzer.load_data():
        analyzer.calculate_survey_averages()
        analyzer.save_results()
        analyzer.print_summary()

if __name__ == "__main__":
    main()
