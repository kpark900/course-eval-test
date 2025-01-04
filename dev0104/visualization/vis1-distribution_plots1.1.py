#!/usr/bin/env python3
"""
File: survey_distribution_plots.py
Version: 1.1
Created: 2024-01-04
AI: Claude 3.5 Sonnet (2024-01)

Usage:
1. Place this script in the same directory as:
   - survey_statistics_report_Distribution Stats.csv
2. Install required packages:
   pip install pandas plotly
3. Run the script:
   python survey_distribution_plots.py

The script will generate interactive distribution plots in HTML format
in a 'visualizations' subdirectory.
"""

import pandas as pd
import numpy as np  # Add explicit numpy import
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SurveyDistributionPlots:
    def __init__(self, data_file='survey_statistics_report_Distribution Stats.csv'):
        """Initialize the visualization class."""
        self.data_dir = Path('./csv_data')
        self.data_file = self.data_dir / data_file
        self.output_dir = Path('visualizations')
        self.output_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load and prepare the dataset."""
        try:
            logger.info(f"Loading data from {self.data_file}")
            if not self.data_file.exists():
                raise FileNotFoundError(f"Data file not found: {self.data_file}")
                
            self.df = pd.read_csv(self.data_file)
            
            # Clean up index if needed
            if 'Unnamed: 0' in self.df.columns:
                self.df.set_index('Unnamed: 0', inplace=True)
            
            # Filter for Survey1-7 rows
            self.df = self.df[self.df.index.str.contains('Survey')]
            logger.info(f"Data loaded successfully with {len(self.df)} survey questions")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def create_distribution_plot(self):
        """Create distribution plot for all survey questions."""
        try:
            # Create subplot figure
            fig = make_subplots(
                rows=4, cols=2,
                subplot_titles=[f"Survey Question {i}" for i in range(1, 8)],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # Add distribution for each survey question
            for i, row in enumerate(range(1, 8), 1):
                # Calculate subplot position
                plot_row = (i-1) // 2 + 1
                plot_col = (i-1) % 2 + 1
                
                # Get statistics for this survey
                survey_stats = self.df.iloc[i-1]
                
                # Fix numpy reference
                x = pd.Series(np.linspace(  # Changed from pd.np to np
                    survey_stats['mean'] - 3*survey_stats['std'],
                    survey_stats['mean'] + 3*survey_stats['std'],
                    100
                ))
                
                # Add main distribution curve
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=np.exp(-(x - survey_stats['mean'])**2 / (2 * survey_stats['std']**2)),  # Changed from pd.np to np
                        name=f'Survey {i}',
                        mode='lines',
                        line=dict(width=2),
                        showlegend=True
                    ),
                    row=plot_row, col=plot_col
                )
                
                # Add mean line
                fig.add_vline(
                    x=survey_stats['mean'],
                    line_dash="dash",
                    line_color="red",
                    row=plot_row,
                    col=plot_col,
                    annotation_text=f"Mean: {survey_stats['mean']:.2f}"
                )
                
                # Add quartile lines
                fig.add_vline(
                    x=survey_stats['q25'],
                    line_dash="dot",
                    line_color="gray",
                    row=plot_row,
                    col=plot_col,
                    annotation_text="Q1"
                )
                fig.add_vline(
                    x=survey_stats['median'],
                    line_dash="dot",
                    line_color="green",
                    row=plot_row,
                    col=plot_col,
                    annotation_text="Median"
                )
                fig.add_vline(
                    x=survey_stats['q75'],
                    line_dash="dot",
                    line_color="gray",
                    row=plot_row,
                    col=plot_col,
                    annotation_text="Q3"
                )

            # Update layout
            fig.update_layout(
                title='Distribution of Survey Responses',
                height=1200,
                width=1000,
                showlegend=True,
                template='plotly_white'
            )
            
            # Update all x and y axes
            fig.update_xaxes(title_text="Score")
            fig.update_yaxes(title_text="Density")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating distribution plot: {str(e)}")
            raise
            
    def add_statistical_annotations(self, fig):
        """Add statistical annotations to the plot."""
        try:
            for i, row in enumerate(range(1, 8), 1):
                # Calculate subplot position
                plot_row = (i-1) // 2 + 1
                plot_col = (i-1) % 2 + 1
                
                stats = self.df.iloc[i-1]
                
                # Add annotations
                annotation_text = (
                    f"Mean: {stats['mean']:.2f}<br>"
                    f"SD: {stats['std']:.2f}<br>"
                    f"Skewness: {stats['skewness']:.2f}<br>"
                    f"Kurtosis: {stats['kurtosis']:.2f}"
                )
                
                fig.add_annotation(
                    xref=f"x{i}", yref=f"y{i}",
                    x=0.95, y=0.95,
                    text=annotation_text,
                    showarrow=False,
                    align='left',
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='rgba(0, 0, 0, 0.3)',
                    borderwidth=1,
                    row=plot_row, col=plot_col
                )
                
            return fig
            
        except Exception as e:
            logger.error(f"Error adding statistical annotations: {str(e)}")
            raise

    def generate_visualizations(self):
        """Generate and save all visualizations."""
        try:
            # Create basic distribution plot
            fig = self.create_distribution_plot()
            
            # Add statistical annotations
            fig = self.add_statistical_annotations(fig)
            
            # Save visualization
            output_file = self.output_dir / "survey_distributions.html"
            fig.write_html(output_file)
            logger.info(f"Saved visualization to {output_file}")
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {str(e)}")
            raise

def main():
    """Main execution function."""
    try:
        # Create visualization instance
        viz = SurveyDistributionPlots()
        
        # Generate visualizations
        viz.generate_visualizations()
        
        logger.info("All visualizations generated successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
