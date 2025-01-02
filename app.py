"""
File: course_evaluation_dashboard.py
Version: 1.0.0
Created: 2025-01-02
AI: Claude 3.5 Sonnet (2024-10-22)

Description:
    Interactive Streamlit dashboard for analyzing course evaluations data.
    Creates visualizations for overall satisfaction, college comparisons,
    professor performance, and temporal trends.

Usage:
    1. Place this script in your project directory along with your CSV data file
    2. Install required packages:
       pip install streamlit pandas plotly seaborn matplotlib
    
    3. Run the dashboard:
       streamlit run course_evaluation_dashboard.py
    
    4. Access the dashboard in your web browser (typically http://localhost:8501)

Directory Structure:
    your_project_folder/
    ├── course_evaluation_dashboard.py
    └── ProcessedData500_sample_rowsUTF8BOM.csv

Notes:
    - Ensure your CSV file matches the expected structure with columns:
      Year, Semester, Campus, College, CourseNumber, CourseCode, CourseName,
      ProfessorName, ProfessorID, Survey1-8, GroupCode
    - The dashboard uses caching for performance optimization
    - All visualizations are interactive and responsive to sidebar filters
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(page_title="Course Evaluation Dashboard", layout="wide")
st.title("Course Evaluation Analysis Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("ProcessedData500_sample_rowsUTF8BOM.csv")
    return df

df = load_data()

# Sidebar for filtering
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox("Select Year", sorted(df["Year"].unique()))
selected_semester = st.sidebar.selectbox("Select Semester", sorted(df["Semester"].unique()))
selected_college = st.sidebar.selectbox("Select College", ["All"] + sorted(df["College"].unique()))

# Filter data based on selections
filtered_df = df[df["Year"] == selected_year]
filtered_df = filtered_df[filtered_df["Semester"] == selected_semester]
if selected_college != "All":
    filtered_df = filtered_df[filtered_df["College"] == selected_college]

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["Overall Satisfaction", "College Comparison", "Professor Analysis", "Temporal Trends"])

with tab1:
    st.header("Overall Satisfaction Analysis")
    
    # Average ratings across survey questions
    col1, col2 = st.columns(2)
    
    with col1:
        # Heatmap of average ratings by college
        survey_cols = [f"Survey{i}" for i in range(1, 8)]
        heatmap_data = df.groupby("College")[survey_cols].mean()
        fig = px.imshow(heatmap_data,
                       labels=dict(x="Survey Question", y="College", color="Average Rating"),
                       aspect="auto",
                       title="Average Ratings Heatmap by College")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Box plot of survey responses
        box_data = pd.melt(filtered_df[survey_cols])
        fig = px.box(box_data, x="variable", y="value",
                    title="Distribution of Survey Responses",
                    labels={"variable": "Survey Question", "value": "Rating"})
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("College Comparison")
    
    # Average satisfaction by college
    col1, col2 = st.columns(2)
    
    with col1:
        college_avg = df.groupby("College")[survey_cols].mean().mean(axis=1).sort_values(ascending=True)
        fig = px.bar(college_avg,
                    orientation='h',
                    title="Average Satisfaction by College",
                    labels={"value": "Average Rating", "index": "College"})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Radar chart for selected college
        if selected_college != "All":
            college_data = filtered_df[survey_cols].mean()
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=college_data.values,
                theta=survey_cols,
                fill='toself',
                name=selected_college
            ))
            fig.update_layout(title=f"Survey Metrics for {selected_college}")
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("Professor Performance Analysis")
    
    # Scatter plot of survey correlations
    col1, col2 = st.columns(2)
    
    with col1:
        x_metric = st.selectbox("Select X-axis metric", survey_cols, key="scatter_x")
        y_metric = st.selectbox("Select Y-axis metric", survey_cols, key="scatter_y")
        
        fig = px.scatter(filtered_df,
                        x=x_metric,
                        y=y_metric,
                        color="College",
                        hover_data=["ProfessorName", "CourseName"],
                        title=f"Correlation between {x_metric} and {y_metric}")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top professors table
        prof_avg = filtered_df.groupby("ProfessorName")[survey_cols].mean()
        prof_avg["Overall Score"] = prof_avg.mean(axis=1)
        top_profs = prof_avg.nlargest(10, "Overall Score")
        st.write("Top 10 Rated Professors")
        st.dataframe(top_profs)

with tab4:
    st.header("Temporal Analysis")
    
    # Time series of average ratings
    yearly_avg = df.groupby(["Year", "Semester"])[survey_cols].mean().reset_index()
    fig = px.line(yearly_avg.melt(id_vars=["Year", "Semester"]),
                  x="Year",
                  y="value",
                  color="variable",
                  title="Rating Trends Over Time",
                  labels={"value": "Average Rating"})
    st.plotly_chart(fig, use_container_width=True)

# Footer with summary statistics
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Courses", len(filtered_df))
with col2:
    st.metric("Average Overall Rating", 
              round(filtered_df[survey_cols].mean().mean(), 2))
with col3:
    st.metric("Number of Professors", 
              filtered_df["ProfessorName"].nunique())