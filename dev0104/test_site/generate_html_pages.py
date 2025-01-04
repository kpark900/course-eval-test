# generate_html_pages.py

#!/usr/bin/env python3
# File: generate_html_pages.py
# Version: 1.0
# Created by: chatGPT-4o (2025-01-04)

import json
import os
from jinja2 import Template

def load_metrics(json_file):
    """Load metrics from a JSON file."""
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Metrics file {json_file} not found.")
    with open(json_file, 'r') as file:
        return json.load(file)

def create_summary_page(metrics, output_dir):
    """Generate an HTML summary page."""
    summary_template = Template("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Summary</title>
    </head>
    <body>
        <h1>Dataset Summary</h1>
        <h2>Evaluation Metrics</h2>
        <p><strong>Overall Mean:</strong> {{ metrics['evaluation']['overall']['mean'] }}</p>
        <p><strong>Overall Response Rate:</strong> {{ metrics['evaluation']['overall']['response_rate'] }}%</p>

        <h2>Top 10 Courses (Survey 1)</h2>
        <ol>
        {% for course, score in metrics['additional']['top_10_courses']['Survey1'].items() %}
            <li>{{ course }}: {{ score }}</li>
        {% endfor %}
        </ol>

        <h2>Demographic Metrics</h2>
        <p><strong>Colleges:</strong> {{ metrics['demographics']['college_distribution']['section_count'] | length }}</p>
        <p><strong>Campuses:</strong> {{ metrics['demographics']['campus_distribution'] | length }}</p>

        <h2>Class Sizes</h2>
        <p><strong>Small Classes:</strong> {{ metrics['class_sizes'] | selectattr('Size', 'equalto', 'Small') | list | length }}</p>
        <p><strong>Medium Classes:</strong> {{ metrics['class_sizes'] | selectattr('Size', 'equalto', 'Medium') | list | length }}</p>
        <p><strong>Large Classes:</strong> {{ metrics['class_sizes'] | selectattr('Size', 'equalto', 'Large') | list | length }}</p>
        <p><strong>Very Large Classes:</strong> {{ metrics['class_sizes'] | selectattr('Size', 'equalto', 'Very Large') | list | length }}</p>
    </body>
    </html>
    """)

    # Render template and save
    rendered = summary_template.render(metrics=metrics)
    output_path = os.path.join(output_dir, 'summary.html')
    with open(output_path, 'w') as file:
        file.write(rendered)
    print(f"Summary page created at {output_path}")

def generate_html_pages(metrics_file, output_dir):
    """Generate HTML pages based on metrics."""
    metrics = load_metrics(metrics_file)
    os.makedirs(output_dir, exist_ok=True)
    create_summary_page(metrics, output_dir)

def main():
    metrics_file = 'computed_metrics/all_metrics.json'
    output_dir = 'html_pages'

    generate_html_pages(metrics_file, output_dir)
    print("HTML pages generated successfully.")

if __name__ == "__main__":
    main()
