# Automated Data Analysis Pipeline

This project provides an automated data analysis pipeline for CSV datasets. The script leverages modern Python libraries and OpenAI's LLMs to generate insights, visualizations, and a detailed report based on input data. It supports exploratory data analysis (EDA), regression analysis, and AI-powered insights.

---

## Features

1. **Dataset Analysis:**
   - Summarizes the dataset, including column names, data types, missing values, and descriptive statistics.

2. **Data Visualizations:**
   - Correlation matrix heatmap.
   - Distribution plot for numeric columns.
   - Missing values heatmap.

3. **Regression Analysis:**
   - Performs linear regression on numeric data (if suitable columns exist) and provides coefficients and intercepts.

4. **AI-Powered Insights:**
   - Uses OpenAI's GPT model to analyze dataset summaries, visualizations, and regression results to generate actionable insights.

5. **Report Generation:**
   - Creates a Markdown report summarizing the analysis, including visualizations and insights.

---

## Dependencies

Ensure the following Python libraries are installed before running the script:

- `pandas >= 1.3.0` - For data manipulation and analysis.
- `seaborn >= 0.11.2` - For statistical data visualizations.
- `matplotlib >= 3.4.0` - For plotting and saving images.
- `python-dotenv >= 0.19.0` - For loading environment variables.
- `openai >= 0.27.0` - For interacting with OpenAI's LLMs.
- `scikit-learn >= 0.24.0` - For regression analysis.
- `numpy >= 1.21.0` - For numerical computations.

---

## Setup

1. Clone this repository and navigate to its directory.

2. Create a `.env` file to store your OpenAI proxy API token:

```env
AIPROXY_TOKEN=your_api_token_here
```

3. Ensure the OpenAI proxy base URL and token are set correctly in the script:

```python
openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"
openai.api_key = API_TOKEN
```

---

## Usage

### Run the Script

Use the following command to analyze a CSV file:

```bash
uv run autolysis.py dataset.csv
```

### Output

- **README.md**: Contains the analysis report in Markdown format.
- **Charts**: Generated visualizations are saved as PNG files in the current directory.

### Example Workflow

1. Provide a valid CSV file (e.g., `dataset.csv`) containing your data.
2. Run the script.
3. Review the generated `README.md` and visualizations for insights.

---

## Key Components

### Functions

1. **`analyze_csv(file_path)`**
   - Reads the CSV file and generates a dataset summary.
   - Outputs:
     - Column names and data types.
     - Missing values per column.
     - Descriptive statistics.

2. **`create_visualizations(df)`**
   - Generates the following visualizations:
     - Correlation heatmap.
     - Distribution plot for numeric data.
     - Missing values heatmap.
   - Saves visualizations as PNG files.

3. **`perform_regression_analysis(df)`**
   - Performs linear regression if the dataset has sufficient numeric columns.
   - Outputs coefficients and intercept values.

4. **`query_llm(prompt, timeout=90)`**
   - Sends a query to the OpenAI LLM to generate insights and recommendations.

5. **`generate_analysis_report(summary, charts, regression_results)`**
   - Combines dataset summary, visualizations, and regression results to produce a Markdown report using LLM.

---


