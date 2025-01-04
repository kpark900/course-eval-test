# File: advanced_survey_analyzer.py
# Version: 1.0.0
# Created: 2024-01-04
# Author: Claude 3.5 Sonnet (2024-01-04)

"""
Advanced Survey Statistics Analysis Script
----------------------------------------

This script extends the basic survey statistics analysis with advanced measures
including reliability analysis, response patterns, and advanced statistical tests.
Works in conjunction with survey_statistics_analyzer.py.

Usage:
1. Ensure script is in the project root directory
2. Required packages:
   pip install pandas numpy scipy statsmodels scikit-learn

3. Run the script:
   python advanced_survey_analyzer.py

Required files:
- anon-course-eval-24_1Data-cp.csv in the ../data_input/ directory
- survey_statistics_analyzer.py in the same directory

Output:
- advanced_survey_analysis.xlsx with detailed statistical analysis
- Descriptive console output with key findings
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.integrate import IntegrationWarning  # Add this import
from statsmodels.stats.multicomp import pairwise_tukeyhsd  # Changed from pairwise_tukey
from sklearn.cluster import KMeans
from pathlib import Path
import warnings
from typing import Dict, List, Tuple, Optional
from survey_statistics_analyzer import SurveyStatisticsAnalyzer

# Add warning filter at the top of the file
warnings.filterwarnings('ignore', category=IntegrationWarning)

class AdvancedSurveyAnalyzer(SurveyStatisticsAnalyzer):
    def __init__(self, input_file: str = '../data_input/anon-course-eval-24_1Data-cp.csv'):
        """Initialize the advanced analyzer."""
        super().__init__(input_file)
        self.advanced_results: Dict = {}
        
    def calculate_reliability_metrics(self) -> None:
        """Calculate survey reliability and consistency measures."""
        survey_data = self.data[self.survey_cols].dropna()
        
        # Cronbach's alpha
        n_items = len(self.survey_cols)
        item_covs = survey_data.cov().values
        alpha = (n_items / (n_items - 1)) * (1 - np.trace(item_covs) / np.sum(item_covs))
        
        # Inter-item correlations
        correlations = survey_data.corr()
        
        # Item-total correlations
        item_total_corr = {}
        for col in self.survey_cols:
            other_cols = [c for c in self.survey_cols if c != col]
            item_total_corr[col] = survey_data[col].corr(survey_data[other_cols].mean(axis=1))
        
        # Split-half reliability
        half_size = len(self.survey_cols) // 2
        first_half = survey_data.iloc[:, :half_size].mean(axis=1)
        second_half = survey_data.iloc[:, half_size:].mean(axis=1)
        split_half_corr = first_half.corr(second_half)
        
        self.advanced_results['reliability'] = {
            'cronbach_alpha': alpha,
            'correlations': correlations,
            'item_total_correlations': item_total_corr,
            'split_half_reliability': split_half_corr
        }

    def analyze_response_patterns(self) -> None:
        """Analyze response patterns and variability."""
        survey_data = self.data[self.survey_cols]
        
        # Response entropy
        def calculate_entropy(series):
            value_counts = series.value_counts(normalize=True)
            return -np.sum(value_counts * np.log2(value_counts))
        
        entropy = {col: calculate_entropy(survey_data[col]) for col in self.survey_cols}
        
        # Response clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(survey_data)
        cluster_stats = pd.DataFrame({
            'cluster': range(3),
            'size': pd.Series(clusters).value_counts().sort_index(),
            'mean_score': [survey_data[clusters == i].mean().mean() for i in range(3)]
        })
        
        # Missing data patterns
        missing_patterns = survey_data.isnull().sum()
        missing_combinations = survey_data.isnull().sum(axis=1).value_counts()
        
        self.advanced_results['response_patterns'] = {
            'entropy': entropy,
            'clusters': cluster_stats,
            'missing_patterns': missing_patterns,
            'missing_combinations': missing_combinations
        }

    def perform_advanced_tests(self) -> None:
        """Perform advanced statistical tests."""
        # Normality tests
        normality_tests = {}
        for col in self.survey_cols + ['SurveyCombined']:
            data = self.data[col].dropna()
            
            # Fix Anderson-Darling test handling
            anderson_result = stats.anderson(data, dist='norm')
            # Use the test statistic and compare with critical values
            ad_significant = anderson_result.statistic > anderson_result.critical_values[2]  # Using 5% significance level
            
            # Kolmogorov-Smirnov test remains the same
            _, ks_pval = stats.kstest(data, 'norm')
            
            normality_tests[col] = {
                'anderson_statistic': anderson_result.statistic,
                'anderson_critical_value': anderson_result.critical_values[2],
                'anderson_significant': ad_significant,
                'kolmogorov_smirnov_pval': ks_pval
            }
        
        # ANOVA with post-hoc tests
        anova_results = {}
        for col in self.survey_cols + ['SurveyCombined']:
            # Prepare data for ANOVA
            groups = [group for _, group in self.data.groupby('College')[col]]
            f_stat, anova_pval = stats.f_oneway(*groups)
            
            # Prepare data for Tukey's test
            data_clean = self.data.dropna(subset=[col, 'College'])
            tukey = pairwise_tukeyhsd(endog=data_clean[col], 
                                     groups=data_clean['College'],
                                     alpha=0.05)
            
            anova_results[col] = {
                'f_statistic': f_stat,
                'p_value': anova_pval,
                'tukey_results': tukey
            }
        
        self.advanced_results['statistical_tests'] = {
            'normality': normality_tests,
            'anova': anova_results
        }

    def factor_analysis(self) -> None:
        """Perform principal component analysis using numpy."""
        survey_data = self.data[self.survey_cols].dropna()
        
        # Standardize the data
        standardized_data = (survey_data - survey_data.mean()) / survey_data.std()
        
        # Calculate correlation matrix and eigendecomposition
        corr_matrix = np.corrcoef(standardized_data.T)
        eigenvalues, eigenvectors = np.linalg.eigh(corr_matrix)
        
        # Sort eigenvalues and eigenvectors in descending order
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        
        # Create loadings DataFrame with top 3 components
        loadings = pd.DataFrame(
            eigenvectors[:, :3],
            columns=[f'Component{i+1}' for i in range(3)],
            index=self.survey_cols
        )
        
        # Calculate variance explained percentages
        total_variance = eigenvalues.sum()
        variance = pd.Series(
            [ev/total_variance * 100 for ev in eigenvalues[:3]],
            index=[f'Component{i+1}' for i in range(3)]
        )
        
        self.advanced_results['factor_analysis'] = {
            'loadings': loadings,
            'variance_explained': variance
        }

    def save_advanced_results(self, output_file: str = 'advanced_survey_analysis.xlsx') -> bool:
        """Save advanced analysis results to Excel file."""
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Reliability metrics
                pd.DataFrame({
                    'Metric': ['Cronbach\'s Alpha', 'Split-Half Reliability'],
                    'Value': [
                        self.advanced_results['reliability']['cronbach_alpha'],
                        self.advanced_results['reliability']['split_half_reliability']
                    ]
                }).to_excel(writer, sheet_name='Reliability', index=False)
                
                # Inter-item correlations
                self.advanced_results['reliability']['correlations'].to_excel(
                    writer, sheet_name='Correlations'
                )
                
                # Response patterns
                pd.DataFrame(self.advanced_results['response_patterns']['entropy'].items(),
                           columns=['Item', 'Entropy']).to_excel(
                    writer, sheet_name='Response_Patterns', index=False
                )
                
                # Cluster analysis
                self.advanced_results['response_patterns']['clusters'].to_excel(
                    writer, sheet_name='Response_Clusters'
                )
                
                # Factor analysis
                self.advanced_results['factor_analysis']['loadings'].to_excel(
                    writer, sheet_name='Factor_Analysis'
                )
                
                # Statistical tests
                normality_df = pd.DataFrame.from_dict(
                    self.advanced_results['statistical_tests']['normality'],
                    orient='index'
                )
                normality_df.to_excel(writer, sheet_name='Normality_Tests')
            
            print(f"\nAdvanced results saved to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving advanced results: {str(e)}")
            return False

    def print_advanced_summary(self) -> None:
        """Print summary of advanced analysis findings."""
        print("\nAdvanced Statistical Analysis Summary")
        print("===================================")
        
        # Reliability summary
        print("\nReliability Metrics:")
        print(f"Cronbach's Alpha: {self.advanced_results['reliability']['cronbach_alpha']:.3f}")
        print(f"Split-Half Reliability: {self.advanced_results['reliability']['split_half_reliability']:.3f}")
        
        # Response patterns summary
        print("\nResponse Patterns:")
        entropy_mean = np.mean(list(self.advanced_results['response_patterns']['entropy'].values()))
        print(f"Mean Response Entropy: {entropy_mean:.3f}")
        
        # Factor analysis summary
        print("\nFactor Analysis:")
        variance = self.advanced_results['factor_analysis']['variance_explained']
        total_var = variance.sum()
        print(f"Total Variance Explained: {total_var:.1f}%")
        
        # Update normality tests section with correct keys
        print("\nNormality Tests (Combined Score):")
        norm_tests = self.advanced_results['statistical_tests']['normality']['SurveyCombined']
        print(f"Anderson-Darling statistic: {norm_tests['anderson_statistic']:.3f}")
        print(f"Anderson-Darling critical value (5%): {norm_tests['anderson_critical_value']:.3f}")
        print(f"Normality rejected: {norm_tests['anderson_significant']}")
        print(f"Kolmogorov-Smirnov p-value: {norm_tests['kolmogorov_smirnov_pval']:.3f}")

def main():
    """Main function to run the advanced analysis."""
    analyzer = AdvancedSurveyAnalyzer()
    
    if analyzer.load_data():
        # Calculate basic statistics first
        analyzer.calculate_distribution_statistics()
        analyzer.calculate_comparative_statistics()
        
        # Calculate advanced statistics
        analyzer.calculate_reliability_metrics()
        analyzer.analyze_response_patterns()
        analyzer.perform_advanced_tests()
        analyzer.factor_analysis()
        
        # Save results and print summary
        analyzer.save_advanced_results()
        analyzer.print_advanced_summary()

if __name__ == "__main__":
    main()
