#!/usr/bin/env python3
"""
File: college_comparison_viz.py
Version: 1.0
Created: 2024-01-04
AI: Claude 3.5 Sonnet (2024-01)

Usage:
1. Place this script in the same directory as:
   - survey_statistics_report_College_Survey*_Stats.csv files
   - survey_statistics_report_College_SurveyCombined_Stats.csv
2. Install required packages:
   pip install pandas plotly numpy
3. Run the script:
   python college_comparison_viz.py

The script will generate interactive college comparison visualizations
in HTML format in a 'visualizations' subdirectory.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import logging
from pathlib import Path
import plotly.express as px

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CollegeComparisonViz:
    def __init__(self):
        """Initialize the visualization class."""
        self.base_dir = Path('/Users/kpro/projects/1_course-eval--git/dev0104/visualization')
        self.data_dir = self.base_dir / 'csv_data'
        self.output_dir = self.base_dir / 'visualizations'
        self.output_dir.mkdir(exist_ok=True)
        
        # Color scheme for colleges
        self.colors = px.colors.qualitative.Set3
        
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load and prepare all college statistics data."""
        try:
            logger.info("Loading college statistics data")
            
            # Load combined stats from absolute path
            combined_file = self.data_dir / 'survey_statistics_report_College_SurveyCombined_Stats.csv'
            logger.info(f"Loading combined stats from: {combined_file}")
            
            if not combined_file.exists():
                raise FileNotFoundError(f"Combined stats file not found: {combined_file}")
            self.combined_stats = pd.read_csv(combined_file)
            
            # Load individual survey stats with absolute paths
            self.survey_stats = {}
            for i in range(1, 8):
                filename = self.data_dir / f'survey_statistics_report_College_Survey{i}_Stats.csv'
                logger.info(f"Loading survey {i} stats from: {filename}")
                
                if not filename.exists():
                    raise FileNotFoundError(f"Survey stats file not found: {filename}")
                self.survey_stats[i] = pd.read_csv(filename)
                
            logger.info("Data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def create_boxplot_comparison(self):
        """Create college comparison boxplot visualization."""
        try:
            fig = go.Figure()
            
            # Sort colleges by mean score
            sorted_colleges = self.combined_stats.sort_values('mean', ascending=False)
            
            # Add box plots for each college
            for idx, row in sorted_colleges.iterrows():
                fig.add_trace(go.Box(
                    name=row['College'],
                    y=[row['q25'], row['median'], row['q75']],
                    boxpoints=False,
                    marker_color=self.colors[idx % len(self.colors)],
                    hovertext=[
                        f"College: {row['College']}<br>"
                        f"Mean: {row['mean']:.2f}<br>"
                        f"Std Dev: {row['std']:.2f}<br>"
                        f"Sample Size: {row['count']}"
                    ]
                ))
                
                # Add error bars
                fig.add_trace(go.Scatter(
                    name=row['College'] + ' CI',
                    x=[row['College'], row['College']],
                    y=[row['mean'] - 1.96*row['std']/np.sqrt(row['count']),
                       row['mean'] + 1.96*row['std']/np.sqrt(row['count'])],
                    mode='lines',
                    line=dict(color='rgba(0,0,0,0.3)', width=1),
                    showlegend=False
                ))

            # Update layout
            fig.update_layout(
                title='Survey Score Distribution by College',
                yaxis_title='Survey Score',
                boxmode='group',
                template='plotly_white',
                height=800,
                showlegend=False,
                hovermode='closest'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating boxplot comparison: {str(e)}")
            raise
            
    def create_mean_comparison(self):
        """Create mean score comparison visualization."""
        try:
            # Create subplot figure for mean comparisons
            fig = make_subplots(
                rows=4, cols=2,
                subplot_titles=['Survey ' + str(i) for i in range(1, 8)] + ['Combined'],
                vertical_spacing=0.12
            )
            
            # Process each survey
            for i in range(1, 8):
                row = (i-1) // 2 + 1
                col = (i-1) % 2 + 1
                
                stats = self.survey_stats[i].sort_values('mean', ascending=False)
                
                # Add bar chart
                fig.add_trace(
                    go.Bar(
                        x=stats['College'],
                        y=stats['mean'],
                        error_y=dict(
                            type='data',
                            array=1.96*stats['std']/np.sqrt(stats['count']),
                            visible=True
                        ),
                        marker_color=self.colors,
                        hovertemplate=(
                            "College: %{x}<br>"
                            "Mean: %{y:.2f}<br>"
                            "Sample size: %{customdata}<br>"
                            "<extra></extra>"
                        ),
                        customdata=stats['count']
                    ),
                    row=row, col=col
                )
                
                # Update axes
                fig.update_xaxes(tickangle=45, row=row, col=col)
                fig.update_yaxes(title_text='Score', row=row, col=col)

            # Add combined stats in last subplot
            stats = self.combined_stats.sort_values('mean', ascending=False)
            fig.add_trace(
                go.Bar(
                    x=stats['College'],
                    y=stats['mean'],
                    error_y=dict(
                        type='data',
                        array=1.96*stats['std']/np.sqrt(stats['count']),
                        visible=True
                    ),
                    marker_color=self.colors,
                    hovertemplate=(
                        "College: %{x}<br>"
                        "Mean: %{y:.2f}<br>"
                        "Sample size: %{customdata}<br>"
                        "<extra></extra>"
                    ),
                    customdata=stats['count']
                ),
                row=4, col=2
            )

            # Update layout
            fig.update_layout(
                title='Mean Survey Scores by College',
                showlegend=False,
                height=1200,
                width=1200,
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating mean comparison: {str(e)}")
            raise
            
    def create_heatmap_comparison(self):
        """Create heatmap comparison of colleges across surveys."""
        try:
            # Prepare data for heatmap
            colleges = self.combined_stats['College'].unique()
            surveys = list(range(1, 8)) + ['Combined']
            
            # Create data matrix
            matrix = np.zeros((len(colleges), len(surveys)))
            
            # Fill matrix with mean values
            for i, college in enumerate(colleges):
                for j in range(7):
                    matrix[i, j] = self.survey_stats[j+1].loc[
                        self.survey_stats[j+1]['College'] == college, 'mean'
                    ].values[0]
                matrix[i, -1] = self.combined_stats.loc[
                    self.combined_stats['College'] == college, 'mean'
                ].values[0]
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=['Survey ' + str(i) for i in range(1, 8)] + ['Combined'],
                y=colleges,
                colorscale='RdBu',
                text=np.round(matrix, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False,
                hovertemplate=(
                    "College: %{y}<br>"
                    "Survey: %{x}<br>"
                    "Score: %{z:.2f}<br>"
                    "<extra></extra>"
                )
            ))

            # Update layout
            fig.update_layout(
                title='Heatmap of Survey Scores Across Colleges',
                height=800,
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating heatmap comparison: {str(e)}")
            raise

    def generate_visualizations(self):
        """Generate and save all visualizations."""
        try:
            visualizations = {
                'college_boxplot': self.create_boxplot_comparison(),
                'college_mean_comparison': self.create_mean_comparison(),
                'college_heatmap': self.create_heatmap_comparison()
            }
            
            # Save all visualizations
            for name, fig in visualizations.items():
                output_file = self.output_dir / f"{name}.html"
                fig.write_html(output_file)
                logger.info(f"Saved visualization to {output_file}")
                
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            raise

def main():
    """Main execution function."""
    try:
        # Create visualization instance
        viz = CollegeComparisonViz()
        
        # Generate visualizations
        viz.generate_visualizations()
        
        logger.info("All visualizations generated successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
