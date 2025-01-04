# File: survey_statistics_analyzer.py -> by Claude kp90
# Version: 1.0.0
# Created: 2024-01-04
# Author: Claude 3.5 Sonnet (2024-01-04)

"""
Advanced Survey Statistics Analysis Script
----------------------------------------

This script performs detailed statistical analysis of survey scores, including
distribution statistics and comparative analysis across different groups.

Usage:
1. Ensure script is in the project root directory
2. Required packages:
   pip install pandas numpy scipy statsmodels

3. Run the script:
   python survey_statistics_analyzer.py

Required files:
- anon-course-eval-24_1Data-cp.csv in the ../data_input/ directory

Output:
- survey_statistics_report.xlsx with detailed statistical analysis
- Descriptive console output with key findings
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import warnings
from typing import Dict, List, Tuple

class SurveyStatisticsAnalyzer:
    def __init__(self, input_file: str = '../data_input/anon-course-eval-24_1Data-cp.csv'):
        """Initialize the analyzer with input file path."""
        self.input_file = input_file
        self.data = None
        self.survey_cols = [f'Survey{i}' for i in range(1, 8)]
        self.results: Dict = {}
        
    def load_data(self) -> bool:
        """Load and validate input data."""
        try:
            self.data = pd.read_csv(self.input_file)
            # Convert survey columns to numeric
            for col in self.survey_cols:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
            # Add combined score
            self.data['SurveyCombined'] = self.data[self.survey_cols].mean(axis=1)
            
            print(f"Successfully loaded {len(self.data):,} records")
            return True
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False

    def calculate_distribution_statistics(self) -> None:
        """Calculate comprehensive distribution statistics."""
        analysis_cols = self.survey_cols + ['SurveyCombined']
        
        for col in analysis_cols:
            stats_dict = {
                # Basic statistics
                'count': len(self.data[col].dropna()),
                'mean': self.data[col].mean(),
                'std': self.data[col].std(),
                
                # Quartiles
                'q25': self.data[col].quantile(0.25),
                'median': self.data[col].median(),
                'q75': self.data[col].quantile(0.75),
                
                # Shape statistics
                'skewness': self.data[col].skew(),
                'kurtosis': self.data[col].kurtosis(),
                
                # Mode and frequency
                'mode': self.data[col].mode().iloc[0],
                'mode_freq': self.data[col].value_counts().iloc[0],
                'mode_pct': (self.data[col].value_counts().iloc[0] / len(self.data)) * 100,
                
                # IQR
                'iqr': self.data[col].quantile(0.75) - self.data[col].quantile(0.25),
                
                # Coefficient of variation
                'cv': (self.data[col].std() / self.data[col].mean()) * 100
            }
            
            # Calculate 95% confidence interval
            ci = stats.t.interval(
                alpha=0.95,
                df=len(self.data[col].dropna())-1,
                loc=self.data[col].mean(),
                scale=stats.sem(self.data[col].dropna())
            )
            stats_dict['ci_lower'] = ci[0]
            stats_dict['ci_upper'] = ci[1]
            
            self.results[f'distribution_{col}'] = stats_dict

    def calculate_comparative_statistics(self) -> None:
        """Calculate comparative statistics across groups."""
        group_cols = ['College', 'Campus']
        
        for group_col in group_cols:
            for survey_col in self.survey_cols + ['SurveyCombined']:
                # Group statistics
                group_stats = self.data.groupby(group_col)[survey_col].agg([
                    'count', 'mean', 'std',
                    lambda x: x.quantile(0.25),
                    'median',
                    lambda x: x.quantile(0.75),
                    'skew', 'kurtosis'
                ]).round(3)
                
                # Add IQR and CV
                group_stats['iqr'] = group_stats['<lambda>_1'] - group_stats['<lambda>_0']
                group_stats['cv'] = (group_stats['std'] / group_stats['mean']) * 100
                
                # Calculate z-scores for each group
                overall_mean = self.data[survey_col].mean()
                overall_std = self.data[survey_col].std()
                group_stats['z_score'] = (group_stats['mean'] - overall_mean) / overall_std
                
                # Effect sizes (Cohen's d) between groups
                group_means = self.data.groupby(group_col)[survey_col].mean()
                group_stds = self.data.groupby(group_col)[survey_col].std()
                
                effect_sizes = pd.DataFrame(index=group_means.index, columns=group_means.index)
                for g1 in group_means.index:
                    for g2 in group_means.index:
                        if g1 < g2:  # Calculate only for unique pairs
                            pooled_std = np.sqrt((group_stds[g1]**2 + group_stds[g2]**2) / 2)
                            d = (group_means[g1] - group_means[g2]) / pooled_std
                            effect_sizes.loc[g1, g2] = d
                            effect_sizes.loc[g2, g1] = -d
                
                self.results[f'comparative_{group_col}_{survey_col}'] = {
                    'group_stats': group_stats,
                    'effect_sizes': effect_sizes
                }

    def identify_outliers(self) -> pd.DataFrame:
        """Identify statistical outliers in survey responses."""
        outliers = pd.DataFrame()
        
        for col in self.survey_cols + ['SurveyCombined']:
            # Calculate z-scores for each value
            z_scores = np.abs(stats.zscore(self.data[col].dropna()))
            
            # Identify outliers (|z| > 3)
            outlier_mask = z_scores > 3
            
            if outlier_mask.any():
                outlier_data = self.data[outlier_mask][['College', 'CourseName', col]]
                outlier_data['z_score'] = z_scores[outlier_mask]
                outliers = pd.concat([outliers, outlier_data])
        
        return outliers

    def save_results(self, output_file: str = 'survey_statistics_report.xlsx') -> bool:
        """Save all results to an Excel file with multiple sheets."""
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Distribution statistics
                dist_stats = pd.DataFrame.from_dict(
                    {k: v for k, v in self.results.items() 
                     if k.startswith('distribution_')},
                    orient='index'
                )
                dist_stats.to_excel(writer, sheet_name='Distribution Stats')
                
                # Comparative statistics
                for key, value in self.results.items():
                    if key.startswith('comparative_'):
                        sheet_name = key.replace('comparative_', '')[:31]
                        value['group_stats'].to_excel(writer, sheet_name=f'{sheet_name}_Stats')
                        value['effect_sizes'].to_excel(writer, sheet_name=f'{sheet_name}_Effect')
                
                # Outliers
                outliers = self.identify_outliers()
                outliers.to_excel(writer, sheet_name='Outliers', index=False)
                
            print(f"\nResults saved to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving results: {str(e)}")
            return False

    def print_summary(self) -> None:
        """Print key findings to console."""
        print("\nKey Statistical Findings")
        print("=======================")
        
        # Distribution summary
        print("\nDistribution Statistics (Combined Score):")
        dist_stats = self.results['distribution_SurveyCombined']
        print(f"Mean: {dist_stats['mean']:.3f} (95% CI: {dist_stats['ci_lower']:.3f} - {dist_stats['ci_upper']:.3f})")
        print(f"Median: {dist_stats['median']:.3f}")
        print(f"IQR: {dist_stats['iqr']:.3f}")
        print(f"Skewness: {dist_stats['skewness']:.3f}")
        print(f"Kurtosis: {dist_stats['kurtosis']:.3f}")
        
        # Group comparisons
        print("\nGroup Comparisons:")
        for group in ['College', 'Campus']:
            stats = self.results[f'comparative_{group}_SurveyCombined']['group_stats']
            print(f"\n{group} Performance (top 3 by mean):")
            print(stats.nlargest(3, 'mean')[['mean', 'std', 'cv']])

def main():
    """Main function to run the analysis."""
    analyzer = SurveyStatisticsAnalyzer()
    
    if analyzer.load_data():
        analyzer.calculate_distribution_statistics()
        analyzer.calculate_comparative_statistics()
        analyzer.save_results()
        analyzer.print_summary()

if __name__ == "__main__":
    main()
