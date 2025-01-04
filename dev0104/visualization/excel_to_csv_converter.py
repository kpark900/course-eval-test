import pandas as pd
import os
from pathlib import Path

def convert_excel_to_csv(excel_file: str, output_dir: str, verbose: bool = True) -> None:
    """Convert each sheet in Excel file to a separate CSV file."""
    try:
        if verbose:
            print(f"Reading file: {excel_file}")
        
        # Read Excel file
        excel = pd.ExcelFile(excel_file)
        base_name = Path(excel_file).stem
        
        if verbose:
            print(f"Found sheets: {excel.sheet_names}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert each sheet
        for sheet_name in excel.sheet_names:
            if verbose:
                print(f"Processing sheet: {sheet_name}")
            
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Create CSV filename
            csv_filename = f"{base_name}_{sheet_name}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            
            # Save to CSV
            df.to_csv(csv_path, index=False)
            if verbose:
                print(f"Created: {csv_path}")
                print(f"Row count: {len(df)}")
    
    except Exception as e:
        print(f"Error processing {excel_file}: {str(e)}")
        raise

def main():
    # Setup absolute paths
    project_root = Path('/Users/kpro/projects/1_course-eval--git/dev0104/visualization')
    input_dir = project_root / 'base_data'
    output_dir = project_root / 'csv_data'
    
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Excel files to process
    excel_files = [
        'advanced_survey_analysis.xlsx',
        'survey_analysis.xlsx',
        'survey_statistics_report.xlsx'
    ]
    
    # Process each Excel file
    for excel_file in excel_files:
        input_path = input_dir / excel_file
        if input_path.exists():
            print(f"\nProcessing: {excel_file}")
            try:
                convert_excel_to_csv(str(input_path), str(output_dir))
            except Exception as e:
                print(f"Failed to process {excel_file}: {str(e)}")
        else:
            print(f"File not found: {input_path}")

if __name__ == "__main__":
    main()
