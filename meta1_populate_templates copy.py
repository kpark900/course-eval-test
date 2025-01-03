# populate_templates.py Version 0.01 by chatGPT-4o

import os
import pandas as pd

# Directories
input_dir = './input_dir_metadata'
output_dir = './output_metadata'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Input files
input_files = {
    "core_metrics": os.path.join(input_dir, "1_standardized-core-metrics.csv"),
    "groupcode_metrics": os.path.join(input_dir, "2_standardized-groupcode-metrics.csv"),
    "course_rankings": os.path.join(input_dir, "3_standardized-course-rankings.csv"),
    "size_distribution": os.path.join(input_dir, "4_standardized-size-distribution.csv"),
    "detailed_stats": os.path.join(input_dir, "5_standardized-detailed-stats.csv"),
    "processed_data": os.path.join(input_dir, "course-eval-24_1 - ProcessedData.csv"),
    "column_mapping": os.path.join(input_dir, "course-eval-24_1 - ColumnMapping.csv"),
    "coursenames": os.path.join(input_dir, "coursenamesProcessedData.csv")
}

# Load input files into dataframes
dataframes = {}
for key, file_path in input_files.items():
    try:
        dataframes[key] = pd.read_csv(file_path)
        print(f"Loaded {key} successfully.")
    except Exception as e:
        print(f"Error loading {key}: {e}")

# Display column mapping for review
column_mapping = dataframes.get("column_mapping")
if column_mapping is not None:
    print("\nColumn Mapping:")
    print(column_mapping.head())

# Function to normalize column names using the mapping
def normalize_columns(df, mapping_df):
    mapping = dict(zip(mapping_df["Original Column"], mapping_df["Mapped Column"]))
    return df.rename(columns=mapping)

# Normalize processed data columns
processed_data = dataframes.get("processed_data")
if processed_data is not None and column_mapping is not None:
    processed_data = normalize_columns(processed_data, column_mapping)
    print("\nProcessed Data after Normalization:")
    print(processed_data.head())

    # Calculate Core Metrics (Template 1)
    core_metrics = processed_data.groupby(["College", "Campus"]).mean(numeric_only=True).reset_index()
    core_metrics = core_metrics[["College", "Campus", "Survey1", "Survey2", "Survey3", "Survey4", "Survey5", "Survey6", "Survey7"]]
    core_metrics.rename(columns={
        "Survey1": "Survey1_Avg",
        "Survey2": "Survey2_Avg",
        "Survey3": "Survey3_Avg",
        "Survey4": "Survey4_Avg",
        "Survey5": "Survey5_Avg",
        "Survey6": "Survey6_Avg",
        "Survey7": "Survey7_Avg"
    }, inplace=True)

    # Save Core Metrics template
    core_metrics.to_csv(os.path.join(output_dir, "1_standardized-core-metrics-populated.csv"), index=False)
    print("Core Metrics template populated and saved.")

# Save cleaned and normalized processed data for verification
processed_data.to_csv(os.path.join(output_dir, "processed_data_normalized.csv"), index=False)

print("Setup, preprocessing, and Template 1 processing completed. Normalized data and Core Metrics template saved.")
