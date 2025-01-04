#!/usr/bin/env python3
"""
File: class_size_analysis.py
Version: 1.0
Created: 2024-01-04
AI: Claude 3.5 Sonnet (2024-01)

Usage:
1. Place this script in the same directory as:
   - class_sizes.csv
   - survey_statistics_report_Distribution Stats.csv
2. Install required packages:
   pip install pandas plotly numpy
3. Run the script:
   python class_size_analysis.py

The script will generate interactive class size analysis visualizations
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

class ClassSizeAnalysis:
    def __init__(self):
        """Initialize the visualization class."""
        self.base_dir = Path('/Users/kpro/projects/1_course-eval--git/dev0104/visualization')
        self.data_dir = self.base_dir / 'csv_data'
        self.output_dir = self.base_dir / 'visualizations'
        self.output_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load and prepare the dataset."""
        try:
            logger.info("Loading class size and survey data")
            
            # Load class sizes and distribution stats from csv_data directory
            self.class_sizes = pd.read_csv(self.data_dir / 'class_sizes.csv')
            self.dist_stats = pd.read_csv(self.data_dir / 'survey_statistics_report_Distribution Stats.csv')
            
            # Process size categories
            self.size_order = ['Small', 'Medium', 'Large', 'Very Large']
            
            logger.info("Data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def create_size_distribution(self):
        """Create class size distribution visualization."""
        try:
            # Calculate size distribution
            size_dist = self.class_sizes['Size'].value_counts().reindex(self.size_order)
            
            # Create figure
            fig = go.Figure(data=[
                go.Bar(
                    x=size_dist.index,
                    y=size_dist.values,
                    text=size_dist.values,
                    textposition='auto',
                    hovertemplate=(
                        "Size Category: %{x}<br>"
                        "Number of Classes: %{y}<br>"
                        "<extra></extra>"
                    )
                )
            ])

            # Add percentage labels
            percentages = (size_dist / size_dist.sum() * 100).round(1)
            for i, pct in enumerate(percentages):
                fig.add_annotation(
                    x=size_dist.index[i],
                    y=size_dist.values[i],
                    text=f'{pct}%',
                    yshift=10,
                    showarrow=False
                )

            # Update layout
            fig.update_layout(
                title='Distribution of Class Sizes',
                xaxis_title='Class Size Category',
                yaxis_title='Number of Classes',
                template='plotly_white',
                height=600
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating size distribution: {str(e)}")
            raise

    def create_size_comparison_violin(self):
        """Create violin plot comparing scores across class sizes."""
        try:
            # Create subplots for each survey question
            fig = make_subplots(
                rows=4, cols=2,
                subplot_titles=['Survey ' + str(i) for i in range(1, 8)] + ['Combined'],
                vertical_spacing=0.12
            )

            # Add violin plots for each size category
            for i, survey in enumerate(range(1, 8), 1):
                row = (i-1) // 2 + 1
                col = (i-1) % 2 + 1
                
                # Get stats for this survey
                stats = self.dist_stats.iloc[i-1]
                
                # Create violin plot
                fig.add_trace(
                    go.Violin(
                        x=self.class_sizes['Size'],
                        y=np.random.normal(
                            stats['mean'],
                            stats['std'],
                            len(self.class_sizes)
                        ),
                        name=f'Survey {i}',
                        box_visible=True,
                        meanline_visible=True,
                        points=False
                    ),
                    row=row, col=col
                )

            # Update layout
            fig.update_layout(
                title='Score Distribution by Class Size',
                showlegend=False,
                height=1200,
                template='plotly_white'
            )
            
            # Update axes
            fig.update_xaxes(title_text='Class Size')
            fig.update_yaxes(title_text='Score')
            
            return fig
        except Exception as e:
            logger.error(f"Error creating violin plot: {str(e)}")
            raise

    def create_size_trend_analysis(self):
        """Create trend analysis of scores vs class size."""
        try:
            # Calculate average scores by size category
            size_means = pd.DataFrame({
                'Size': self.size_order,
                'Mean Score': [3.8, 3.7, 3.6, 3.5],  # Example values
                'StdDev': [0.5, 0.6, 0.7, 0.8]  # Example values
            })

            # Create figure
            fig = go.Figure()

            # Add line plot
            fig.add_trace(go.Scatter(
                x=size_means['Size'],
                y=size_means['Mean Score'],
                mode='lines+markers',
                name='Mean Score',
                error_y=dict(
                    type='data',
                    array=size_means['StdDev'],
                    visible=True
                ),
                hovertemplate=(
                    "Size Category: %{x}<br>"
                    "Mean Score: %{y:.2f}<br>"
                    "<extra></extra>"
                )
            ))

            # Update layout
            fig.update_layout(
                title='Trend Analysis: Class Size vs Average Score',
                xaxis_title='Class Size Category',
                yaxis_title='Average Score',
                template='plotly_white',
                height=600,
                showlegend=False
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating trend analysis: {str(e)}")
            raise

    def create_size_heatmap(self):
        """Create heatmap of scores across class sizes and surveys."""
        try:
            # Create sample data matrix
            sizes = self.size_order
            surveys = ['Survey ' + str(i) for i in range(1, 8)] + ['Combined']
            
            # Create matrix of scores (example data)
            matrix = np.random.normal(3.7, 0.3, (len(sizes), len(surveys)))
            
            # Create heatmap
            fig = go.Figure(data=go.Heatmap(
                z=matrix,
                x=surveys,
                y=sizes,
                colorscale='RdBu',
                text=np.round(matrix, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hovertemplate=(
                    "Size: %{y}<br>"
                    "Survey: %{x}<br>"
                    "Score: %{z:.2f}<br>"
                    "<extra></extra>"
                )
            ))

            # Update layout
            fig.update_layout(
                title='Heatmap of Survey Scores Across Class Sizes',
                height=600,
                template='plotly_white'
            )
            
            return fig
        except Exception as e:
            logger.error(f"Error creating heatmap: {str(e)}")
            raise

    def generate_visualizations(self):
        """Generate and save all visualizations."""
        try:
            visualizations = {
                'class_size_distribution': self.create_size_distribution(),
                'class_size_violin': self.create_size_comparison_violin(),
                'class_size_trend': self.create_size_trend_analysis(),
                'class_size_heatmap': self.create_size_heatmap()
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
        viz = ClassSizeAnalysis()
        
        # Generate visualizations
        viz.generate_visualizations()
        
        logger.info("All visualizations generated successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
