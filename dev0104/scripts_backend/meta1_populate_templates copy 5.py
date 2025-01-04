# populate_templates.py Version 0.03 by chatGPT-4o

"""
This script processes Templates 1, 2, 3, and 4 accumulatively. It first calculates and saves the Core Metrics (Template 1), then proceeds to calculate and save the Group Code Metrics (Template 2), followed by the Course Rankings (Template 3), and finally calculates and saves the Size Distribution (Template 4).

Usage:
1. Place all input files in the './input_dir_metadata' directory.
2. Run the script. It will create the './output_metadata' directory if it does not exist.
3. The processed templates will be saved in the './output_metadata' directory as CSV files.

Required Input Files:
- course-eval-24_1 - ProcessedData.csv
- course-eval-24_1 - ColumnMapping.csv
- 1_standardized-core-metrics.csv
- 2_standardized-groupcode-metrics.csv
- 3_standardized-course-rankings.csv
- 4_standardized-size-distribution.csv
- 5_standardized-detailed-stats.csv
"""

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

    # Add Class_Size_Category based on GroupCode
    processed_data['Class_Size_Category'] = processed_data.groupby('GroupCode')['GroupCode'].transform('count')

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

    # Calculate Group Code Metrics (Template 2)
    groupcode_metrics = processed_data.groupby(["GroupCode", "CourseName", "College", "ProfessorID"]).mean(numeric_only=True).reset_index()
    groupcode_metrics = groupcode_metrics[["GroupCode", "CourseName", "College", "ProfessorID", "Survey1", "Survey2", "Survey3", "Survey4", "Survey5", "Survey6", "Survey7"]]
    groupcode_metrics.rename(columns={
        "Survey1": "Survey1_Avg",
        "Survey2": "Survey2_Avg",
        "Survey3": "Survey3_Avg",
        "Survey4": "Survey4_Avg",
        "Survey5": "Survey5_Avg",
        "Survey6": "Survey6_Avg",
        "Survey7": "Survey7_Avg"
    }, inplace=True)

    # Save Group Code Metrics template
    groupcode_metrics.to_csv(os.path.join(output_dir, "2_standardized-groupcode-metrics-populated.csv"), index=False)
    print("Group Code Metrics template populated and saved.")

    # Calculate Course Rankings (Template 3)
    course_rankings = processed_data.groupby(["CourseCode", "CourseName", "College"]).mean(numeric_only=True).reset_index()
    course_rankings = course_rankings[["CourseCode", "CourseName", "College", "Survey1", "Survey2", "Survey3", "Survey4", "Survey5", "Survey6", "Survey7"]]
    course_rankings.rename(columns={
        "Survey1": "Survey1_Avg",
        "Survey2": "Survey2_Avg",
        "Survey3": "Survey3_Avg",
        "Survey4": "Survey4_Avg",
        "Survey5": "Survey5_Avg",
        "Survey6": "Survey6_Avg",
        "Survey7": "Survey7_Avg"
    }, inplace=True)

    # Add Overall Rank based on Survey1_Avg
    course_rankings["Overall_Rank"] = course_rankings["Survey1_Avg"].rank(ascending=False, method="min")

    # Save Course Rankings template
    course_rankings.to_csv(os.path.join(output_dir, "3_standardized-course-rankings-populated.csv"), index=False)
    print("Course Rankings template populated and saved.")

    # Calculate Size Distribution (Template 4)
    size_distribution = processed_data.groupby("Class_Size_Category").agg({
        "CourseCode": "count",
        "Survey1": "mean",
        "Survey2": "mean",
        "Survey3": "mean",
        "Survey4": "mean",
        "Survey5": "mean",
        "Survey6": "mean",
        "Survey7": "mean"
    }).reset_index()

    size_distribution.rename(columns={
        "CourseCode": "Course_Count",
        "Survey1": "Survey1_Avg",
        "Survey2": "Survey2_Avg",
        "Survey3": "Survey3_Avg",
        "Survey4": "Survey4_Avg",
        "Survey5": "Survey5_Avg",
        "Survey6": "Survey6_Avg",
        "Survey7": "Survey7_Avg"
    }, inplace=True)

    # Save Size Distribution template
    size_distribution.to_csv(os.path.join(output_dir, "4_standardized-size-distribution-populated.csv"), index=False)
    print("Size Distribution template populated and saved.")

# Save cleaned and normalized processed data for verification
processed_data.to_csv(os.path.join(output_dir, "processed_data_normalized.csv"), index=False)

print("Setup, preprocessing, and Templates 1, 2, 3 & 4 processing completed. Normalized data and templates saved.")
