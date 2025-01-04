# File: class_size_analyzer.py
# Version: 1.0.0
# Created: 2024-01-04
# Author: Claude 3.5 Sonnet (2024-01-04)

"""
Class Size Analysis Script
-------------------------

This script analyzes class sizes from course evaluation data and categorizes
them into size groups (Small, Medium, Large, Very Large).

Usage:
1. Place this script in the same directory as your input CSV file
2. Ensure required packages are installed:
   pip install pandas

3. Run the script:
   python class_size_analyzer.py

Required files:
- courseeval24_1 ProcessedDataanon.csv in the same directory

Output:
- class_sizes.csv containing GroupCode, Students count, and Size category
"""

import pandas as pd
from pathlib import Path

def categorize_size(count):
    """Categorize class size based on student count."""
    if count <= 15:
        return 'Small'
    elif count <= 30:
        return 'Medium'
    elif count <= 75:
        return 'Large'
    else:
        return 'Very Large'

infile = '../data_input/anon-course-eval-24_1Data-cp.csv'
def analyze_class_sizes(input_file=infile, 
                       output_file='class_sizes.csv'):
    """
    Analyze class sizes and create categorized output file.
    
    Parameters:
    -----------
    input_file : str
        Path to input CSV file
    output_file : str
        Path to output CSV file
    
    Returns:
    --------
    bool
        True if analysis and file creation successful, False otherwise
    """
    try:
        # Read input file
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df):,} records from {input_file}")
        
        # Group by GroupCode and count students
        class_sizes = df.groupby('GroupCode').size().reset_index(name='Students')
        
        # Add size category
        class_sizes['Size'] = class_sizes['Students'].apply(categorize_size)
        
        # Sort by student count descending
        class_sizes = class_sizes.sort_values('Students', ascending=False)
        
        # Save to CSV
        class_sizes.to_csv(output_file, index=False)
        
        # Generate summary statistics
        size_distribution = class_sizes['Size'].value_counts()
        total_classes = len(class_sizes)
        
        # Print summary report
        print("\nClass Size Analysis Summary")
        print("==========================")
        print(f"Total number of classes: {total_classes:,}")
        print("\nSize Distribution:")
        for size_category in ['Small', 'Medium', 'Large', 'Very Large']:
            count = size_distribution.get(size_category, 0)
            percentage = (count / total_classes) * 100
            print(f"{size_category}: {count:,} classes ({percentage:.1f}%)")
            
        print(f"\nResults saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return False

def main():
    """Main function to run the analysis."""
    analyze_class_sizes()

if __name__ == "__main__":
    main()
