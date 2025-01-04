#!/usr/bin/env python3
"""
File: vis1-distribution_plots.py
Version: 1.2.0
Created: 2024-01-04
AI: Claude 3.5 Sonnet (2024-01)

Usage:
1. Ensure input CSV files are in './csv_data' directory
2. Install required packages:
   pip install pandas plotly
3. Run the script:
   python vis1-distribution_plots.py

The script will generate interactive distribution plots in HTML format
in a 'visualizations' subdirectory.
"""

import pandas as pd
import numpy as np  # Add numpy import
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
    def __init__(self, data_file='survey_statistics_report_Distribution_Stats.csv'):  # Fixed filename
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
                # Try alternative filenames if the first one doesn't exist
                alternatives = [
                    'survey_statistics_report_Distribution Stats.csv',
                    'survey_statistics_report_Distribution_Stats.csv'
                ]
                for alt in alternatives:
                    alt_path = self.data_dir / alt
                    if alt_path.exists():
                        self.data_file = alt_path
                        break
                else:
                    raise FileNotFoundError(f"Data file not found in {self.data_dir}")
                
            # Read CSV with first column as index
            self.df = pd.read_csv(self.data_file, index_col=0)
            logger.info(f"Loaded data shape: {self.df.shape}")
            logger.info(f"Column names: {self.df.columns.tolist()}")
            logger.info(f"Index values: {self.df.index.tolist()}")
            
            # Filter for Survey rows and sort them
            mask = (self.df.index.astype(str).str.contains('Survey', case=False, na=False) & 
                   ~self.df.index.astype(str).str.contains('Combined', case=False, na=False))
            self.df = self.df[mask].copy()
            self.df = self.df.sort_index()
            
            logger.info(f"After filtering - shape: {self.df.shape}")
            logger.info(f"After filtering - index: {self.df.index.tolist()}")
            
            # Verify we have exactly 7 survey questions
            if len(self.df) != 7:
                raise ValueError(f"Expected 7 survey questions, found {len(self.df)}\nAvailable indices: {self.df.index.tolist()}")
                
            logger.info(f"Data loaded successfully with {len(self.df)} survey questions")
            logger.info(f"Survey questions found: {self.df.index.tolist()}")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def create_distribution_plot(self):
        """Create distribution plot for all survey questions."""
        try:
            # Verify data is loaded
            if len(self.df) != 7:
                raise ValueError("Data not properly loaded")
            
            # Extract survey numbers for subplot titles
            subplot_titles = [f"Survey Question {idx.split('Survey')[-1]}" 
                            for idx in self.df.index]
            
            # Create subplot figure with extracted titles
            fig = make_subplots(
                rows=4, cols=2,
                subplot_titles=subplot_titles,
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # Add distribution for each survey question
            for i, (idx, row) in enumerate(self.df.iterrows(), 1):
                # Calculate subplot position
                plot_row = (i-1) // 2 + 1
                plot_col = (i-1) % 2 + 1
                
                # Get statistics for this survey
                survey_stats = row  # Use the row directly
                
                # Fix numpy references
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
        """Add comprehensive statistical annotations to the plot."""
        try:
            for i, row in enumerate(range(1, 8), 1):
                # Calculate subplot position
                plot_row = (i-1) // 2 + 1
                plot_col = (i-1) % 2 + 1
                
                stats = self.df.iloc[i-1]
                
                # Create detailed statistical annotations
                basic_stats = (
                    f"Basic Statistics:<br>"
                    f"• Mean: {stats['mean']:.2f}<br>"
                    f"• Median: {stats['median']:.2f}<br>"
                    f"• SD: {stats['std']:.2f}<br>"
                    f"• Sample Size: {int(stats['count']):,}"
                )
                
                distribution_stats = (
                    f"Distribution Characteristics:<br>"
                    f"• Skewness: {stats['skewness']:.2f}<br>"
                    f"• Kurtosis: {stats['kurtosis']:.2f}<br>"
                    f"• CV: {stats['cv']:.2f}<br>"
                    f"• IQR: {stats['iqr']:.2f}"
                )
                
                confidence_stats = (
                    f"Confidence Interval (95%):<br>"
                    f"• Lower: {stats['ci_lower']:.2f}<br>"
                    f"• Upper: {stats['ci_upper']:.2f}"
                )
                
                mode_stats = (
                    f"Mode Statistics:<br>"
                    f"• Mode: {stats['mode']:.0f}<br>"
                    f"• Mode Freq: {stats['mode_freq']:.0f}<br>"
                    f"• Mode %: {stats['mode_pct']:.1f}%"
                )
                
                # Add basic stats annotation
                fig.add_annotation(
                    xref=f"x{i}", yref=f"y{i}",
                    x=0.95, y=0.95,
                    text=basic_stats,
                    showarrow=False,
                    align='left',
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='rgba(0, 0, 0, 0.3)',
                    borderwidth=1,
                    row=plot_row, col=plot_col
                )
                
                # Add distribution stats annotation
                fig.add_annotation(
                    xref=f"x{i}", yref=f"y{i}",
                    x=0.95, y=0.65,
                    text=distribution_stats,
                    showarrow=False,
                    align='left',
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='rgba(0, 0, 0, 0.3)',
                    borderwidth=1,
                    row=plot_row, col=plot_col
                )
                
                # Add confidence interval annotation
                fig.add_annotation(
                    xref=f"x{i}", yref=f"y{i}",
                    x=0.95, y=0.35,
                    text=confidence_stats,
                    showarrow=False,
                    align='left',
                    bgcolor='rgba(255, 255, 255, 0.8)',
                    bordercolor='rgba(0, 0, 0, 0.3)',
                    borderwidth=1,
                    row=plot_row, col=plot_col
                )
                
                # Add mode stats annotation
                fig.add_annotation(
                    xref=f"x{i}", yref=f"y{i}",
                    x=0.95, y=0.15,
                    text=mode_stats,
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