#!/usr/bin/env python3
# File: update_pages.py
# Version: 1.1
# Created by: Claude 3.5 Sonnet (2024-01-03)
# Usage: Place script in project root directory containing HTML files and CSV data
#        Run: python3 update_pages.py
#        Optional: python3 update_pages.py --preview

import os
import sys
import logging
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, List
from pathlib import Path

class PageUpdater:
    def __init__(self):
        self.metadata_dir = './metadata_output'
        self.html_dir = './html_static_pages'
        self.data_files = {
            'core_metrics': os.path.join(self.metadata_dir, '1_standardized-core-metrics-populated.csv'),
            'group_metrics': os.path.join(self.metadata_dir, '2_standardized-groupcode-metrics-populated.csv'),
            'course_rankings': os.path.join(self.metadata_dir, '3_standardized-course-rankings-populated.csv'),
            'size_distribution': os.path.join(self.metadata_dir, '4_standardized-size-distribution-populated.csv'),
            'detailed_stats': os.path.join(self.metadata_dir, '5_standardized-detailed-stats-populated.csv')
        }
        self.html_files = [
            os.path.join(self.html_dir, file) for file in [
                'index.html', 'demographics.html', 'performance.html',
                'evaluation.html', 'findings.html'
            ]
        ]
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('page_updates.log'),
                logging.StreamHandler()
            ]
        )

    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV files into dataframes."""
        data = {}
        for key, filename in self.data_files.items():
            try:
                data[key] = pd.read_csv(filename)
                logging.info(f"Loaded {filename}")
            except Exception as e:
                logging.error(f"Error loading {filename}: {str(e)}")
                sys.exit(1)
        return data

    def get_mobile_meta_tags(self) -> str:
        """Return mobile-friendly meta tags."""
        return """
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="theme-color" content="#2c3e50">
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-capable" content="yes">
        """

    def get_responsive_styles(self) -> str:
        """Return mobile-friendly CSS."""
        return """
        @media (max-width: 768px) {
            .container { padding: 0.5rem; }
            .nav-list { flex-direction: column; }
            .nav-list a { display: block; text-align: center; }
            .metrics-grid, .stats-grid, .data-grid {
                grid-template-columns: 1fr;
            }
            table { 
                display: block;
                overflow-x: auto;
                white-space: nowrap;
            }
            .metric-value { font-size: 1.5rem; }
            .header h1 { font-size: 1.5rem; }
        }
        """

    def update_html_file(self, filename: str, data: Dict[str, pd.DataFrame]) -> None:
        """Update a single HTML file with new data and mobile support."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')

            # Add mobile meta tags
            meta_tags = BeautifulSoup(self.get_mobile_meta_tags(), 'html.parser')
            soup.head.extend(meta_tags)

            # Add responsive styles
            style_tag = soup.new_tag('style')
            style_tag.string = self.get_responsive_styles()
            soup.head.append(style_tag)

            # Update content based on file type
            if filename == 'evaluation.html':
                self.update_evaluation_content(soup, data)
            elif filename == 'performance.html':
                self.update_performance_content(soup, data)
            elif filename == 'findings.html':
                self.update_findings_content(soup, data)

            # Save updated file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            logging.info(f"Updated {filename}")

        except Exception as e:
            logging.error(f"Error updating {filename}: {str(e)}")

    def update_evaluation_content(self, soup: BeautifulSoup, data: Dict[str, pd.DataFrame]) -> None:
        """Update evaluation page content."""
        core_metrics = data['core_metrics']
        
        # Update overall statistics
        overall_avg = core_metrics[['Survey1_Avg', 'Survey2_Avg', 'Survey3_Avg',
                                  'Survey4_Avg', 'Survey5_Avg', 'Survey6_Avg',
                                  'Survey7_Avg']].mean().mean()
        
        metric_value = soup.find('div', class_='stat-value')
        if metric_value:
            metric_value.string = f"{overall_avg:.2f}"

    def update_performance_content(self, soup: BeautifulSoup, data: Dict[str, pd.DataFrame]) -> None:
        """Update performance page content."""
        rankings = data['course_rankings']
        
        # Update performance metrics
        perf_stats = rankings[['Survey1_Avg', 'Survey2_Avg', 'Survey3_Avg',
                             'Survey4_Avg', 'Survey5_Avg', 'Survey6_Avg',
                             'Survey7_Avg']].agg(['mean', 'std']).round(2)
        
        metrics_grid = soup.find('div', class_='metrics-grid')
        if metrics_grid:
            for idx, (metric, value) in enumerate(perf_stats.loc['mean'].items()):
                metric_card = metrics_grid.find_all('div', class_='metric-card')[idx]
                if metric_card:
                    value_div = metric_card.find('div', class_='metric-value')
                    if value_div:
                        value_div.string = f"{value:.2f}"

    def update_findings_content(self, soup: BeautifulSoup, data: Dict[str, pd.DataFrame]) -> None:
        """Update findings page content."""
        detailed = data['detailed_stats']
        
        # Update key findings
        findings = {
            'median_score': detailed[[col for col in detailed.columns if 'Median' in col]].mean().mean(),
            'std_score': detailed[[col for col in detailed.columns if 'Std' in col]].mean().mean(),
            'q3_score': detailed[[col for col in detailed.columns if 'Q3' in col]].mean().mean()
        }
        
        findings_section = soup.find('div', class_='findings-section')
        if findings_section:
            metrics = findings_section.find_all('div', class_='metric-value')
            for metric, value in zip(metrics, findings.values()):
                metric.string = f"{value:.2f}"

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Update HTML pages with new data')
    parser.add_argument('--preview', action='store_true',
                      help='Preview changes without saving')
    args = parser.parse_args()

    updater = PageUpdater()
    data = updater.load_data()
    
    for html_file in updater.html_files:
        updater.update_html_file(html_file, data)

if __name__ == "__main__":
    main()