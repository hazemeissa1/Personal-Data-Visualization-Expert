import streamlit as st
import seaborn as sns
import logging
from llm_handler import check_ollama_connection, DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL, openai_api_key

logger = logging.getLogger(__name__)

def render_header():
    st.title("Personal Data Visualization Expert")
    st.markdown("""
    Upload a CSV file and ask questions about your data in plain English. 
    I'll generate visualizations and summaries to help you understand your data better.

    **Example queries:**
    - "Show a histogram of sales"
    - "Create a bar chart of categories by revenue"
    - "Make a scatter plot of price vs. rating"
    - "Plot monthly sales over time"
    - "Summarize the dataset"
    """)
    logger.info("Rendered header")

def render_sidebar():
    global openai_api_key
    st.sidebar.title("Configuration")
    llm_provider = st.sidebar.radio(
        "LLM Provider", ["manual", "openai", "ollama"], index=0,
        help="Select which mode to use for creating visualizations (Manual mode doesn't require LLM)"
    )
    if llm_provider == "openai":
        openai_api_key = st.sidebar.text_input(
            "OpenAI API Key", type="password", value=openai_api_key if openai_api_key else "",
            help="Enter your OpenAI API key to enable natural language processing."
        )
        if openai_api_key:
            st.sidebar.success("API key set!")
        else:
            st.sidebar.warning("Please enter an OpenAI API key to use this mode.")
        ollama_model, ollama_host = DEFAULT_OLLAMA_MODEL, DEFAULT_OLLAMA_HOST

    elif llm_provider == "ollama":
        st.sidebar.markdown("### Ollama Configuration")
        ollama_host = st.sidebar.text_input("Ollama Host URL", value=DEFAULT_OLLAMA_HOST, help="The URL where your Ollama server is running")
        if check_ollama_connection(ollama_host):
            try:
                models_response = requests.get(f"{ollama_host}/api/tags")
                if models_response.status_code == 200:
                    available_models = [model["name"] for model in models_response.json().get("models", [])]
                    if available_models:
                        default_index = available_models.index(DEFAULT_OLLAMA_MODEL) if DEFAULT_OLLAMA_MODEL in available_models else 0
                        ollama_model = st.sidebar.selectbox("Ollama Model", options=available_models, index=default_index, help="Select which Ollama model to use")
                        st.sidebar.success(f"Connected to Ollama, found {len(available_models)} models")
                    else:
                        ollama_model = st.sidebar.text_input("Ollama Model", value=DEFAULT_OLLAMA_MODEL, help="Name of the Ollama model to use")
                        st.sidebar.warning("Connected to Ollama but no models found. Please make sure you have models pulled.")
                else:
                    ollama_model = st.sidebar.text_input("Ollama Model", value=DEFAULT_OLLAMA_MODEL, help="Name of the Ollama model to use")
                    st.sidebar.error("Could not retrieve models from Ollama server.")
            except Exception as e:
                logger.error(f"Ollama connection error: {str(e)}")
                ollama_model = st.sidebar.text_input("Ollama Model", value=DEFAULT_OLLAMA_MODEL, help="Name of the Ollama model to use")
                st.sidebar.error("Could not connect to Ollama server. Please check the host URL.")
        else:
            ollama_model = st.sidebar.text_input("Ollama Model", value=DEFAULT_OLLAMA_MODEL, help="Name of the Ollama model to use")
            st.sidebar.error("Could not connect to Ollama server. Please make sure Ollama is running.")
    else:
        ollama_model, ollama_host, openai_api_key = DEFAULT_OLLAMA_MODEL, DEFAULT_OLLAMA_HOST, None
        st.sidebar.success("Running in manual mode. No LLM connection required.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ## About
    This app helps you analyze and visualize your data with ease.
    Upload a CSV file and either:
    - Use the manual selector to create visualizations directly
    - Ask questions in plain English (requires OpenAI or Ollama)
    ### Visualization Modes
    - **Manual**: Use the interface to select what to visualize
    - **OpenAI**: Uses OpenAI's API (requires API key)
    - **Ollama**: Uses a local Ollama instance (must be running)
    """)
    logger.info(f"Sidebar rendered with LLM provider: {llm_provider}")
    return {
        "llm_provider": llm_provider,
        "ollama_model": ollama_model,
        "ollama_host": ollama_host,
        "openai_api_key": openai_api_key
    }

def render_file_uploader():
    return st.file_uploader("Upload a CSV file", type=["csv"])

def render_dataset_preview(df):
    with st.expander("Dataset Preview", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown(f"**Dataset Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
        st.markdown("**Column Data Types:**")
        for col, dtype in df.dtypes.astype(str).items():
            st.markdown(f"- **{col}**: {dtype}")
    logger.info("Rendered dataset preview")

def render_query_input():
    return st.text_input(
        "Ask a question about your data",
        placeholder="e.g., Show a bar chart of category vs sales",
        key="query_input"
    )

def render_visualization_result(fig, description):
    st.markdown("## Result")
    st.markdown(f"**{description}**")
    st.plotly_chart(fig, use_container_width=True)
    logger.info("Rendered visualization result")

def render_summary_result(summary_df, description):
    st.markdown("## Summary Statistics")
    st.markdown(f"**{description}**")
    st.dataframe(summary_df, use_container_width=True)
    logger.info("Rendered summary result")

def render_example_queries():
    st.markdown("### Example Queries")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Basic Queries**")
        st.markdown("- Show a summary of the dataset")
        st.markdown("- Create a histogram of [column]")
        st.markdown("- Make a bar chart of [column]")
    with cols[1]:
        st.markdown("**Comparison Queries**")
        st.markdown("- Plot [column1] vs [column2]")
        st.markdown("- Compare [column1] across [column2]")
        st.markdown("- Scatter plot of [column1] and [column2]")
    with cols[2]:
        st.markdown("**Time Series Queries**")
        st.markdown("- Show trend of [column] over time")
        st.markdown("- Line chart of [column] by [date column]")
        st.markdown("- Monthly [column] values")
    logger.info("Rendered example queries")

def render_sample_data_option():
    st.markdown("### Don't have a CSV file? Try sample data:")
    sample_datasets = {
        "Titanic Dataset": "titanic",
        "Iris Dataset": "iris",
        "Tips Dataset": "tips"
    }
    sample_choice = st.selectbox("Select a sample dataset", options=["None"] + list(sample_datasets.keys()))
    if sample_choice != "None":
        dataset_name = sample_datasets[sample_choice]
        try:
            df = sns.load_dataset(dataset_name)
            return df
        except Exception as e:
            st.error(f"Error loading sample dataset: {str(e)}")
            logger.error(f"Sample data loading error: {str(e)}")
            return None
    return None