# Personal Data Visualization Assistant

Analyze and visualize your data effortlessly using natural language or manual controls.

## Screenshots
### Dashboard 
![LLM Mode Example](https://github.com/user-attachments/assets/4f05425f-901a-47c1-ac21-23ccfbd3b787)
### Dashboard
![LLM Mode Example](https://github.com/user-attachments/assets/e60670af-affe-489c-be01-9e7a231baaeb)



## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
- [Usage](#usage)
  - [Running the App](#running-the-app)
  - [Using LLM Mode](#using-llm-mode)
  - [Using Manual Mode](#using-manual-mode)
  - [Example: Creating a Histogram of Adult Males](#example-creating-a-histogram-of-adult-males)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
  - [LLM Integration](#llm-integration)
  - [Data Processing](#data-processing)
  - [Visualization](#visualization)
  - [Filtering](#filtering)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Project Overview

The **Personal Data Visualization Expert** is a Streamlit-based web application designed to simplify data analysis and visualization. Users can upload their own CSV files or use built-in sample datasets (e.g., Titanic, Iris, Tips) to generate visualizations and statistical summaries. The app supports two modes of interaction:

- **Natural Language Queries (LLM Mode):** Leverage large language models (LLMs) like OpenAI’s GPT or local Ollama models to interpret queries in plain English, such as "Create a histogram of adult males."
- **Manual Mode:** Use an intuitive interface to select visualization types and parameters without requiring an LLM.

This project was developed to address the need for a user-friendly tool that combines the power of AI-driven data interpretation with manual control, making data analysis accessible to users of all skill levels.

## Features

- **Data Upload:** Upload CSV files for custom data analysis.
- **Sample Datasets:** Built-in datasets (Titanic, Iris, Tips) for quick exploration.
- **Visualization Types:**
  - Histogram: Visualize the distribution of numeric data.
  - Bar Chart: Compare categories, with or without a value column.
  - Scatter Plot: Explore relationships between two numeric variables.
  - Line Chart: Analyze trends over time or other ordered data.
- **Summary Statistics:** Generate detailed statistical summaries of the dataset.
- **LLM-Powered Queries:** Use natural language to create visualizations (e.g., "Create a histogram of adult males").
- **Manual Visualization Builder:** Select visualization types and parameters via a user-friendly interface.
- **Filtering Support:** Apply filters to the data (e.g., filter for adult males in the Titanic dataset) in both LLM and manual modes.
- **Interactive Visualizations:** Powered by Plotly for dynamic, web-based charts.
- **Responsive Design:** Streamlit’s wide layout ensures a clean, professional UI.

## Technologies Used

- **Python 3.8+:** Core programming language.
- **Streamlit:** Framework for building the web application.
- **Pandas:** Data manipulation and analysis.
- **Plotly:** Interactive visualizations.
- **Seaborn:** Access to sample datasets (Titanic, Iris, Tips).
- **OpenAI API:** For natural language query processing (optional).
- **Ollama:** Local LLM support for natural language queries (optional).
- **Requests:** HTTP requests for Ollama API communication.
- **Logging:** For debugging and monitoring app behavior.

## Installation

### Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.8 or higher:** [Download Python](https://www.python.org/downloads/)
- **pip:** Python package manager (comes with Python)
- **Git:** For cloning the repository ([Download Git](https://git-scm.com/downloads))
- **Virtualenv (optional but recommended):** For creating isolated Python environments

Optional dependencies for LLM mode:

- **OpenAI API Key:** Required for OpenAI LLM mode. Sign up at [OpenAI](https://platform.openai.com/signup).
- **Ollama:** Required for local LLM mode. Install Ollama by following the instructions at [Ollama’s official site](https://ollama.com/). Ensure Ollama is running locally with a model like `llama3`.

### Setup Instructions

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/personal-data-visualization-expert.git
   cd personal-data-visualization-expert
   ```

2. **Create a Virtual Environment (recommended):**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies:**

   `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

   
   ```

4. **Set Up Ollama (Optional):**

   If using Ollama for local LLM mode, ensure Ollama is installed and running:

   ```bash
   ollama run llama3
   ```

   Verify Ollama is accessible

  Yes, the content I gave you is **a complete and detailed `README.md`**, but because of the character limit, it was cut off **just at the end of the installation section**, right before the **Usage** and other final sections like License and Contact.

I'll now give you the **remainder of the README** starting from where we left off, so you'll have the *entire thing in full*. Here we go:

---

### Verify Ollama is accessible (continued)

You can test the local LLM API by running this in a Python shell:

```python
import requests
response = requests.post("http://localhost:11434/api/generate", json={"model": "llama3", "prompt": "Say Hello"})
print(response.json())
```

---

## Usage

### Running the App

From your project directory, run:

```bash
streamlit run main.py
```

The app will open in your default web browser at `http://localhost:8501`.

---

### Using LLM Mode

1. Upload a CSV or choose a sample dataset.
2. Type your query in natural language like:
   - "Create a histogram of adult males."
   - "Show a bar chart of survived vs not survived grouped by gender."
3. Choose between OpenAI or Ollama for query processing.
4. The app will interpret the request and render the visualization.

---

### Using Manual Mode

1. Select the chart type (bar, histogram, scatter, etc.).
2. Select relevant columns (x-axis, y-axis).
3. Optionally apply filters like:
   - `sex == "male"`
   - `age >= 18`
4. Click **"Generate Chart"** to view your visualization.

---

### Example: Creating a Histogram of Adult Males

1. Choose **Titanic** dataset.
2. In LLM mode, type:  
   `"Show a histogram of age for male passengers over 18"`
3. Alternatively, in manual mode:
   - Select Histogram
   - Column: `age`
   - Filter: `sex == "male" and age >= 18`
   - Click **Generate Chart**

---

## Project Structure

```bash
├── app.py                # Main Streamlit app
├── data_processor.py     # Data loading, validation, and preparation
├── llm_handler.py        # LLM prompt construction, querying, and parsing
├── visualizer.py         # Visualization and summary statistics generation
├── ui_components.py      # UI rendering functions
├── requirements.txt      # Dependencies
├── README.md             # Basic setup instructions
```

---

## Technical Details

### LLM Integration

- Uses OpenAI (via API key) or Ollama (local endpoint).
- Prompts the model to return structured commands like:
  ```
  {
    "chart_type": "histogram",
    "column": "age",
    "filters": "sex == 'male' and age > 18"
  }
  ```

### Data Processing

- Cleans uploaded CSVs and converts data types.
- Uses `pandas` for filtering and aggregation.

### Visualization

- Built with `plotly.express` for interactive charts.
- Supports hover tooltips, zooming, and pan.

### Filtering

- Python-based syntax supported in manual mode.
- LLM auto-generates filters in LLM mode.

---

## Troubleshooting

- **Ollama errors:** Make sure Ollama is running and your model (e.g., `llama3`) is downloaded.
- **OpenAI key error:** Set your API key in the Streamlit app or use environment variables.
- **CSV not loading:** Ensure the file is valid UTF-8 CSV format.

---

## Contributing

Contributions welcome!  
If you'd like to:

- Add new chart types
- Support additional LLMs
- Enhance filtering logic

Open a PR or raise an issue.

---

## License

This project is licensed under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---

## Contact

Made by Hazem Eissa  
Feel free to reach out on [LinkedIn](https://linkedin.com/in/hazemeissa) or open an issue.

---

