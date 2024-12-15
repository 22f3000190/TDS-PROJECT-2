import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import time
import openai
from sklearn.linear_model import LinearRegression
import numpy as np

# Load environment variables
load_dotenv()

# Constants
API_TOKEN = os.environ.get("AIPROXY_TOKEN")
if not API_TOKEN:
    print("Error: AIPROXY_TOKEN environment variable is not set.")
    sys.exit(1)

# Set OpenAI Proxy API Base URL
openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"
openai.api_key = API_TOKEN
MODEL = "gpt-4o-mini"

def analyze_csv(file_path):
    """
    Reads a CSV file and generates an extensive summary including:
    - Column names and data types
    - Missing values per column
    - Comprehensive descriptive statistics
    """
    try:
        df = pd.read_csv(file_path, encoding="ISO-8859-1")
        
        summary = {
            "columns": list(df.columns),
            "data_types": df.dtypes.apply(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "comprehensive_stats": {}
        }
        
        # Compute comprehensive statistics for numeric columns
        for column in df.select_dtypes(include=['float64', 'int64']).columns:
            column_stats = {
                "count": df[column].count(),
                "mean": round(df[column].mean(), 4),
                "median": round(df[column].median(), 4),
                "mode": round(df[column].mode().iloc[0], 4) if not df[column].mode().empty else None,
                "std_dev": round(df[column].std(), 4),
                "min": round(df[column].min(), 4),
                "max": round(df[column].max(), 4),
                "range": round(df[column].max() - df[column].min(), 4),
                "25th_percentile": round(df[column].quantile(0.25), 4),
                "75th_percentile": round(df[column].quantile(0.75), 4)
            }
            summary["comprehensive_stats"][column] = column_stats
        
        # Compute categorical column statistics
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns
        summary["categorical_stats"] = {}
        for column in categorical_columns:
            categorical_stats = {
                "unique_values": df[column].nunique(),
                "most_common_value": df[column].mode().iloc[0] if not df[column].mode().empty else None,
                "most_common_count": df[column].value_counts().iloc[0] if not df[column].value_counts().empty else 0
            }
            summary["categorical_stats"][column] = categorical_stats
        
        return df, summary
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

def create_visualizations(df):
    """
    Creates visualizations from the data
    """
    charts = []
    try:
        numeric_df = df.select_dtypes(include=["float64", "int64"])

        # Correlation Heatmap
        if not numeric_df.empty and len(numeric_df.columns) > 1:
            correlation_file = "correlation_matrix.png"
            plt.figure(figsize=(10, 8))
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Matrix")
            plt.tight_layout()
            plt.savefig(correlation_file)
            plt.close()
            charts.append(correlation_file)

        # Distribution of First Numeric Column
        numeric_cols = numeric_df.columns
        if len(numeric_cols) > 0:
            dist_file = "distribution_plot.png"
            plt.figure(figsize=(8, 6))
            sns.histplot(df[numeric_cols[0]], kde=True, bins=30)
            plt.title(f"Distribution of {numeric_cols[0]}")
            plt.xlabel(numeric_cols[0])
            plt.tight_layout()
            plt.savefig(dist_file)
            plt.close()
            charts.append(dist_file)

        # Missing Values Heatmap
        if df.isnull().values.any():
            missing_file = "missing_values_heatmap.png"
            plt.figure(figsize=(10, 6))
            sns.heatmap(df.isnull(), cbar=False, cmap="viridis")
            plt.title("Missing Values Heatmap")
            plt.tight_layout()
            plt.savefig(missing_file)
            plt.close()
            charts.append(missing_file)

    except Exception as e:
        print(f"Error generating visualizations: {e}")
    return charts

def query_llm(summary, charts):
    """
    Queries the LLM to generate a comprehensive analysis report
    """
    try:
        prompt = f"""
        Provide a comprehensive data analysis report based on the following dataset summary:

        Dataset Columns: {summary['columns']}
        Data Types: {summary['data_types']}
        Missing Values: {summary['missing_values']}

        Numeric Columns Highlights:
        {chr(10).join([f"- {col}: Mean = {stats['mean']}, Median = {stats['median']}, Std Dev = {stats['std_dev']}" 
                       for col, stats in summary.get('comprehensive_stats', {}).items()])}

        Categorical Columns Highlights:
        {chr(10).join([f"- {col}: Unique Values = {stats['unique_values']}, Most Common = {stats['most_common_value']}" 
                       for col, stats in summary.get('categorical_stats', {}).items()])}

        Generated Visualization Charts: {charts}

        Please provide:
        1. An overview of the dataset
        2. Key insights from the statistical analysis
        3. Potential recommendations or observations
        4. Any notable patterns or anomalies
        """

        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional data analyst providing insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating LLM analysis: {e}")
        return "Unable to generate LLM analysis."

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py dataset.csv")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)

    # Analyze CSV and generate visualizations
    df, summary = analyze_csv(file_path)
    charts = create_visualizations(df)

    # Generate LLM analysis
    llm_analysis = query_llm(summary, charts)

    # Write comprehensive report
    with open("README.md", "w") as f:
        # LLM Analysis
        f.write("# Comprehensive Data Analysis Report\n\n")
        f.write("## AI-Generated Insights\n")
        f.write(llm_analysis + "\n\n")

        # Numeric Statistics
        f.write("## Numeric Columns Statistics\n")
        for column, stats in summary.get('comprehensive_stats', {}).items():
            f.write(f"### {column}\n")
            for stat_name, stat_value in stats.items():
                f.write(f"- *{stat_name.replace('_', ' ').title()}*: {stat_value}\n")
            f.write("\n")

        # Categorical Statistics
        f.write("## Categorical Columns Statistics\n")
        for column, stats in summary.get('categorical_stats', {}).items():
            f.write(f"### {column}\n")
            for stat_name, stat_value in stats.items():
                f.write(f"- *{stat_name.replace('_', ' ').title()}*: {stat_value}\n")
            f.write("\n")

        # Visualizations
        f.write("## Visualizations\n")
        for chart in charts:
            f.write(f"![{chart}]({chart})\n")

    print("Analysis complete. Results saved to README.md")

if __name__ == "__main__":
    main()