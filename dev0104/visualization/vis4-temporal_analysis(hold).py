#!/usr/bin/env python3
"""
File: vis4-temporal_analysis.py
Version: 1.0
Created: 2024-01-04
AI: Claude 3.5 Sonnet (2024-01)

Usage:
1. Ensure input files are in './csv_data' directory:
   - anoncourseeval24_1Datacp_processed.csv
2. Create output directory:
   mkdir -p ./visualizations
3. Install required packages:
   pip install pandas plotly numpy
4. Run the script:
   python vis4-temporal_analysis.py

The script will generate interactive temporal analysis visualizations
in HTML format in the './visualizations' directory.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import logging
from pathlib import Path
import plotly.express as px
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TemporalAnalysis:
    def __init__(self, input_dir='./csv_data', output_dir='./visualizations'):
        """Initialize the visualization class."""
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load and prepare the dataset."""
        try:
            logger.info("Loading evaluation data")
            
            # Load processed data
            self.df = pd.read_csv(
                self.input_dir / 'anoncourseeval24_1Datacp_processed.csv'
            )
            
            # Create time period field
            self.df['Period'] = self.df['Year'].astype(str) + '-' + self.df['Semester']
            
            # Calculate average scores
            survey_cols = [f'Survey{i}' for i in range(1, 8)]
            self.df['AvgScore'] = self.df[survey_cols].mean(axis=1)
            
            logger.info("Data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def create_temporal_trend(self):
        """Create overall temporal trend visualization."""
        try:
            # Calculate period statistics
            period_stats = self.df.groupby('Period').agg({
                'AvgScore': ['mean', 'std', 'count']
            }).reset_index()
            period_stats.columns = ['Period', 'Mean', 'Std', 'Count']
            
            # Create figure
            fig = go.Figure()

            # Add main trend line
            fig.add_trace(go.Scatter(
                x=period_stats['Period'],
                y=period_stats['Mean'],
                mode='lines+markers',
                name='Mean Score',
                line=dict(width=2),
                error_y=dict(
                    type='data',
                    array=1.96 * period_stats['Std'] / np.sqrt(period_stats['Count']),
                    visible=True
                ),
                hovertemplate=(
                    "Period: %{x}<br>"
                    "Mean Score: %{y:.2f}<br>"
                    "Sample Size: %{customdata}<br>"
                    "<extra></extra>"
                ),
                customdata=period_stats['Count']
            ))

            # Update layout
            fig.update_layout(
                title='Temporal Trend in Evaluation Scores',
                xaxis_title='Academic Period',
                yaxis_title='Average Score',
                template='plotly_white',
                height=600,
                showlegend=True
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating temporal trend: {str(e)}")
            raise

    def create_survey_temporal_comparison(self):
        """Create temporal comparison across survey questions."""
        try:
            # Create subplots
            fig = make_subplots(
                rows=4, cols=2,
                subplot_titles=['Survey ' + str(i) for i in range(1, 8)] + ['Combined'],
                vertical_spacing=0.12
            )
            
            # Process each survey question
            survey_cols = [f'Survey{i}' for i in range(1, 8)] + ['AvgScore']
            for i, col in enumerate(survey_cols, 1):
                # Calculate statistics
                stats = self.df.groupby('Period')[col].agg([
                    'mean', 'std', 'count'
                ]).reset_index()
                
                # Calculate confidence intervals
                stats['ci'] = 1.96 * stats['std'] / np.sqrt(stats['count'])
                
                # Add to subplot
                row = (i-1) // 2 + 1
                col_pos = (i-1) % 2 + 1
                
                fig.add_trace(
                    go.Scatter(
                        x=stats['Period'],
                        y=stats['mean'],
                        mode='lines+markers',
                        error_y=dict(
                            type='data',
                            array=stats['ci'],
                            visible=True
                        ),
                        hovertemplate=(
                            "Period: %{x}<br>"
                            "Mean: %{y:.2f}<br>"
                            "Sample Size: %{customdata}<br>"
                            "<extra></extra>"
                        ),
                        customdata=stats['count']
                    ),
                    row=row, col=col_pos
                )

            # Update layout
            fig.update_layout(
                height=1200,
                title_text="Temporal Trends by Survey Question",
                showlegend=False,
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating survey temporal comparison: {str(e)}")
            raise

    def create_college_temporal_heatmap(self):
        """Create heatmap showing college performance over time."""
        try:
            # Calculate average scores by college and period
            temporal_college = self.df.pivot_table(
                values='AvgScore',
                index='College',
                columns='Period',
                aggfunc='mean'
            )
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=temporal_college.values,
                x=temporal_college.columns,
                y=temporal_college.index,
                colorscale='RdBu',
                text=np.round(temporal_college.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hovertemplate=(
                    "College: %{y}<br>"
                    "Period: %{x}<br>"
                    "Score: %{z:.2f}<br>"
                    "<extra></extra>"
                )
            ))

            # Update layout
            fig.update_layout(
                title='College Performance Over Time',
                height=800,
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating college temporal heatmap: {str(e)}")
            raise

    def create_seasonal_analysis(self):
        """Create seasonal pattern analysis."""
        try:
            # Calculate statistics by semester
            semester_stats = self.df.groupby('Semester').agg({
                'AvgScore': ['mean', 'std', 'count']
            }).reset_index()
            semester_stats.columns = ['Semester', 'Mean', 'Std', 'Count']
            
            # Create figure
            fig = go.Figure()

            # Add bar chart
            fig.add_trace(go.Bar(
                x=semester_stats['Semester'],
                y=semester_stats['Mean'],
                error_y=dict(
                    type='data',
                    array=1.96 * semester_stats['Std'] / np.sqrt(semester_stats['Count']),
                    visible=True
                ),
                hovertemplate=(
                    "Semester: %{x}<br>"
                    "Mean Score: %{y:.2f}<br>"
                    "Sample Size: %{customdata}<br>"
                    "<extra></extra>"
                ),
                customdata=semester_stats['Count']
            ))

            # Update layout
            fig.update_layout(
                title='Seasonal Patterns in Evaluation Scores',
                xaxis_title='Semester',
                yaxis_title='Average Score',
                template='plotly_white',
                height=600,
                showlegend=False
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating seasonal analysis: {str(e)}")
            raise

    def generate_visualizations(self):
        """Generate and save all visualizations."""
        try:
            visualizations = {
                'temporal_trend': self.create_temporal_trend(),
                'survey_temporal': self.create_survey_temporal_comparison(),
                'college_temporal_heatmap': self.create_college_temporal_heatmap(),
                'seasonal_analysis': self.create_seasonal_analysis()
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
        viz = TemporalAnalysis()
        
        # Generate visualizations
        viz.generate_visualizations()
        
        logger.info("All visualizations generated successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
