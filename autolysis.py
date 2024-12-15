import os
import sys
import pandas as pd
!pip install seaborn
import seaborn as sns
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import time
import openai

load_dotenv()

# Check for openai module
try:
    import openai
except ImportError:
    print("Error: The 'openai' module is not installed. Please install it using 'pip install openai'.")
    sys.exit(1)

# Constants
API_TOKEN = os.environ.get("AIPROXY_TOKEN")
if not API_TOKEN:
    print("Error: AIPROXY_TOKEN environment variable is not set.")
    sys.exit(1)

# Set the proxy API base URL
openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"  # Proxy URL

# Authentication headers
openai.api_key = API_TOKEN

# Model to use
MODEL = "gpt-4o-mini"

# Functions for data analysis
def analyze_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
        summary = {
            "columns": list(df.columns),
            "data_types": df.dtypes.apply(str).to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "basic_statistics": df.describe(include='all').to_dict()
        }
        return df, summary
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

def create_visualizations(df):
    charts = []
    try:
        # Correlation heatmap
        correlation_file = "correlation_matrix.png"
        plt.figure(figsize=(10, 8))
        numeric_df = df.select_dtypes(include=['float64', 'int64'])
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
        plt.title("Correlation Matrix")
        plt.savefig(correlation_file)
        charts.append(correlation_file)

        # Distribution of a numeric column (first numeric column)
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            dist_file = "distribution_plot.png"
            plt.figure(figsize=(8, 6))
            sns.histplot(df[numeric_cols[0]], kde=True, bins=30)
            plt.title(f"Distribution of {numeric_cols[0]}")
            plt.savefig(dist_file)
            charts.append(dist_file)

        # Missing values heatmap
        missing_file = "missing_values_heatmap.png"
        plt.figure(figsize=(10, 6))
        sns.heatmap(df.isnull(), cbar=False, cmap="viridis")
        plt.title("Missing Values Heatmap")
        plt.savefig(missing_file)
        charts.append(missing_file)
    except Exception as e:
        print(f"Error generating visualizations: {e}")
    return charts

# Function for LLM interaction
def query_llm(prompt, timeout=90):
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
        return "An error occurred while generating the story."

def generate_analysis_report(summary, charts):
    prompt = (
        f"Analyze the following dataset summary and visualizations, and generate a detailed report as a data analyst. "
        f"Do not generate random fiction stories. Focus on summarizing the analysis, insights, and their implications.\n\n"
        f"Dataset Summary: {summary}\n\nCharts: {', '.join(charts)}\n\n"
        f"Please describe:\n"
        f"1. The data you received, briefly\n"
        f"2. The analysis you carried out\n"
        f"3. The insights you discovered\n"
        f"4. The implications of your findings (i.e., what to do with the insights)"
    )
    return query_llm(prompt, timeout=90)

# Main script logic
def main():
    if len(sys.argv) != 2:
        print("Usage: python autolysis.py dataset.csv")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist.")
        sys.exit(1)

    df, summary = analyze_csv(file_path)
    charts = create_visualizations(df)

    report = generate_analysis_report(summary, charts)

    # Write results to README.md
    with open("README.md", "w") as f:
        f.write("# Automated Data Analysis Report\n\n")
        f.write(f"## Analysis Report\n\n{report}\n\n")
        for chart in charts:
            f.write(f"![{chart}]({chart})\n")

    print("Analysis complete. Results saved to README.md and charts as PNG files.")

if __name__ == "__main__":
    main()
