# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas",
#   "seaborn",
#   "matplotlib",
#   "numpy",
#   "scipy",
#   "openai",
#   "scikit-learn",
#   "requests",
#   "python-dotenv",
#   "ipykernel", 
# ]
# ///
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
    Reads a CSV file and generates a summary including:
    - Column names and data types
    - Missing values per column
    - Basic descriptive statistics

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        tuple: DataFrame and summary dictionary.
    """
    try:
        df = pd.read_csv(file_path, encoding="ISO-8859-1")
        summary = {
            "columns": list(df.columns),
            "data_types": df.dtypes.apply(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "basic_statistics": df.describe(include="all").to_dict(),
        }
        return df, summary
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

def create_visualizations(df):
    """
    Creates visualizations from the data:
    - Correlation matrix heatmap
    - Distribution plot of numeric columns
    - Missing values heatmap

    Args:
        df (DataFrame): Input data.

    Returns:
        list: Filenames of generated charts.
    """
    charts = []
    try:
        numeric_df = df.select_dtypes(include=["float64", "int64"])

        # Correlation Heatmap
        if not numeric_df.empty:
            correlation_file = "correlation_matrix.png"
            plt.figure(figsize=(10, 8))
            sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Matrix")
            plt.savefig(correlation_file)
            charts.append(correlation_file)

        # Distribution of First Numeric Column
        numeric_cols = numeric_df.columns
        if len(numeric_cols) > 0:
            dist_file = "distribution_plot.png"
            plt.figure(figsize=(8, 6))
            sns.histplot(df[numeric_cols[0]], kde=True, bins=30)
            plt.title(f"Distribution of {numeric_cols[0]}")
            plt.xlabel(numeric_cols[0])
            plt.legend([f"Column: {numeric_cols[0]}"])
            plt.savefig(dist_file)
            charts.append(dist_file)

        # Missing Values Heatmap
        if df.isnull().values.any():
            missing_file = "missing_values_heatmap.png"
            plt.figure(figsize=(10, 6))
            sns.heatmap(df.isnull(), cbar=False, cmap="viridis")
            plt.title("Missing Values Heatmap")
            plt.savefig(missing_file)
            charts.append(missing_file)

    except Exception as e:
        print(f"Error generating visualizations: {e}")
    return charts

def perform_regression_analysis(df):
    """
    Performs a simple regression analysis if suitable columns exist.

    Args:
        df (DataFrame): Input data.

    Returns:
        dict: Regression analysis results.
    """
    try:
        numeric_df = df.select_dtypes(include=["float64", "int64"])
        if len(numeric_df.columns) < 2:
            return None  # Not enough data for regression

        X = numeric_df.iloc[:, :-1]
        y = numeric_df.iloc[:, -1]
        model = LinearRegression()
        model.fit(X, y)
        return {"coefficients": model.coef_.tolist(), "intercept": model.intercept_}
    except Exception as e:
        print(f"Error performing regression analysis: {e}")
        return None

def query_llm(prompt, timeout=90):
    """
    Queries the LLM with a given prompt and returns the response.

    Args:
        prompt (str): The prompt for the LLM.
        timeout (int): Timeout in seconds.

    Returns:
        str: LLM response.
    """
    try:
        start_time = time.time()
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[{"role": "system", "content": "You are a professional data analyst."},
                      {"role": "user", "content": prompt}],
            timeout=timeout
        )
        elapsed_time = time.time() - start_time
        print(f"LLM query completed in {elapsed_time:.2f} seconds.")
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error communicating with LLM: {e}")
        return "An error occurred while generating the report."

def generate_analysis_report(summary, charts, regression_results):
    """
    Generates an analysis report using the LLM.

    Args:
        summary (dict): Dataset summary.
        charts (list): Filenames of generated charts.
        regression_results (dict): Regression analysis results.

    Returns:
        str: LLM-generated report.
    """
    prompt = (
        f"Analyze the following dataset summary and visualizations, and generate a detailed Markdown report. "
        f"Include insights and their implications for actionable recommendations.\n\n"
        f"Dataset Summary: {summary}\n\n"
        f"Regression Results: {regression_results}\n\n"
        f"Charts: {', '.join(charts)}\n\n"
    )
    return query_llm(prompt)

def main():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py dataset.csv")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)

    df, summary = analyze_csv(file_path)
    charts = create_visualizations(df)
    regression_results = perform_regression_analysis(df)

    report = generate_analysis_report(summary, charts, regression_results)

    # Save results
    with open("README.md", "w") as f:
        f.write("# Automated Data Analysis Report\n\n")
        f.write(f"## Analysis Report\n\n{report}\n\n")
        for chart in charts:
            f.write(f"![{chart}]({chart})\n")

    print("Analysis complete. Results saved to README.md and charts as PNG files.")

if __name__ == "__main__":
    main()
