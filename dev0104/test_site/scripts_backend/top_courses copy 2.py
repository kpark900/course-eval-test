import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Top Courses Analysis",
    page_icon="📚",
    layout="wide"
)

# Add title and description
st.title("Top Courses Analysis by Class Size")
st.write("Analysis of highly rated courses across different class size categories")

# Read the data
@st.cache_data
def load_data():
    df = pd.read_csv('TopCourses.csv')
    # If CourseName exists in the data, use it; otherwise use GroupCode
    df['DisplayName'] = df['CourseName'] if 'CourseName' in df.columns else df['GroupCode']
    return df

# Load the data
df = load_data()

# Create columns for the layout
col1, col2 = st.columns(2)

# Function to create table and chart for each class size
def create_category_analysis(data, class_size, container):
    with container:
        st.subheader(f"Top Courses - {class_size}")
        
        # Filter data for the specific class size
        category_data = data[data['Class Size'] == class_size].sort_values('Average Score', ascending=False)
        
        # Display the table
        st.dataframe(
            category_data[['DisplayName', 'Average Score']],
            column_config={
                "DisplayName": "Course Name",
                "Average Score": st.column_config.NumberColumn(
                    "Average Score",
                    format="%.2f"
                )
            },
            hide_index=True
        )
        
        # Create bar chart
        fig = px.bar(
            category_data,
            x='DisplayName',
            y='Average Score',
            title=f'Course Ratings - {class_size}',
            color='Average Score',
            color_continuous_scale='Viridis'
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title="Course Name",
            yaxis_title="Average Score",
            showlegend=False,
            height=400,
            # Rotate x-axis labels if they're too long
            xaxis_tickangle=-45
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

# Get unique class sizes
class_sizes = sorted(df['Class Size'].unique())

# Display analysis for each class size
for i, class_size in enumerate(class_sizes):
    container = col1 if i % 2 == 0 else col2
    create_category_analysis(df, class_size, container)

# Add summary statistics at the bottom
st.markdown("---")
st.subheader("Summary Statistics")

# Create summary metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Courses", len(df))
    
with col2:
    avg_score = df['Average Score'].mean()
    st.metric("Overall Average Score", f"{avg_score:.2f}")
    
with col3:
    max_score = df['Average Score'].max()
    st.metric("Highest Score", f"{max_score:.2f}")
    
with col4:
    min_score = df['Average Score'].min()
    st.metric("Lowest Score", f"{min_score:.2f}")

# Add footer
st.markdown("---")
st.markdown("*Data analysis of top-performing courses across different class sizes*")