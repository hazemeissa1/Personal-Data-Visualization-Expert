import streamlit as st
from data_processor import load_data, validate_data, extract_schema, detect_time_columns, prepare_data_for_visualization
from llm_handler import construct_prompt, query_llm, parse_llm_response
from visualizer import generate_visualization, generate_summary_statistics, create_action_from_ui
from ui_components import render_header, render_sidebar, render_file_uploader, render_dataset_preview, render_query_input, render_visualization_result, render_summary_result, render_example_queries, render_sample_data_option
import logging

# Configuration
st.set_page_config(page_title="Personal Data Visualization Expert", page_icon="📊", layout="wide")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.info("Starting Streamlit app...")

def main():
    logger.info("Entered main function")
    st.write("Debug: App is running!")
    render_header()
    config = render_sidebar()
    llm_provider = config["llm_provider"]
    ollama_model = config["ollama_model"]
    ollama_host = config["ollama_host"]
    openai_api_key = config["openai_api_key"]
    uploaded_file = render_file_uploader()
    df = None

    if uploaded_file is not None:
        df = load_data(uploaded_file)
        is_valid, message = validate_data(df)
        if not is_valid:
            st.error(message)
            logger.error(f"Data validation failed: {message}")
            return
        render_dataset_preview(df)
        schema = extract_schema(df)
        time_columns = detect_time_columns(df)
        render_example_queries()
    else:
        sample_df = render_sample_data_option()
        if sample_df is not None:
            df = sample_df
            if "sex" in df.columns and "age" in df.columns:
                df = df[(df["sex"] == "male") & (df["age"] >= 18)].copy()
                st.markdown("**Filtered Dataset:** Showing only adult males (age ≥ 18).")
            render_dataset_preview(df)
            schema = extract_schema(df)
            time_columns = detect_time_columns(df)
            render_example_queries()
        else:
            st.info("Please upload a CSV file or select a sample dataset to get started.")
            st.markdown("""
            ### Getting Started
            1. Upload a CSV file using the file uploader above
            2. Select visualization mode:
               - **Manual**: Use the interface to select visualizations without LLM
               - **OpenAI**: Use OpenAI to interpret natural language queries (requires API key)
               - **Ollama**: Use local Ollama instance (must be running)
            3. Ask questions or use the manual visualization builder
            """)
            logger.info("No file uploaded, showing startup instructions")
            return

    query = render_query_input()
    if query:
        with st.spinner("Analyzing your query..."):
            prompt = construct_prompt(schema, time_columns, query)
            response_text = query_llm(prompt, llm_provider, ollama_model, ollama_host, openai_api_key)
            if response_text:
                action, description, filter_conditions, error = parse_llm_response(response_text)
                if error:
                    st.error(f"Error: {error}")
                    st.markdown("### Fallback to manual mode")
                    st.info("The LLM couldn't process your query. Please use the manual visualization builder instead.")
                    logger.error(f"LLM response error: {error}")
                    action, description = create_action_from_ui(df)
                    if not action:
                        logger.info("No action selected in fallback mode")
                        return
                filtered_df = df.copy()
                if filter_conditions:
                    for condition in filter_conditions:
                        filter_col = condition["column"]
                        filter_val = condition["value"]
                        operator = condition.get("operator", "==")
                        if filter_col not in filtered_df.columns:
                            st.error(f"Filter column '{filter_col}' not found in dataset.")
                            logger.error(f"Filter error: Column '{filter_col}' not found")
                            return
                        try:
                            if operator == "==":
                                filtered_df = filtered_df[filtered_df[filter_col] == filter_val]
                            elif operator == ">=":
                                filtered_df = filtered_df[filtered_df[filter_col] >= filter_val]
                            elif operator == "<=":
                                filtered_df = filtered_df[filtered_df[filter_col] <= filter_val]
                            elif operator == ">":
                                filtered_df = filtered_df[filtered_df[filter_col] > filter_val]
                            elif operator == "<":
                                filtered_df = filtered_df[filtered_df[filter_col] < filter_val]
                            st.markdown(f"**Applied Filter:** {filter_col} {operator} {filter_val}")
                        except Exception as e:
                            st.error(f"Error applying filter: {str(e)}")
                            logger.error(f"Filter error: {str(e)}")
                            return
                if action["type"] == "summarize":
                    summary_df, error = generate_summary_statistics(filtered_df, action)
                    if error:
                        st.error(error)
                        logger.error(f"Summary error: {error}")
                    else:
                        render_summary_result(summary_df, description)
                else:
                    prepared_df, error = prepare_data_for_visualization(filtered_df, action)
                    if error:
                        st.error(error)
                        logger.error(f"Data prep error: {error}")
                    else:
                        fig, error = generate_visualization(prepared_df, action, description)
                        if error:
                            st.error(error)
                            logger.error(f"Visualization error: {error}")
                        else:
                            render_visualization_result(fig, description)
            else:
                st.error("Could not connect to LLM. Falling back to manual mode.")
                st.markdown("### Manual Visualization Builder")
                logger.warning("LLM connection failed, falling back to manual mode")
                action, description = create_action_from_ui(df)
                if not action:
                    logger.info("No action selected in fallback mode")
                    return
                filtered_df = df.copy()
                if action["type"] == "summarize":
                    summary_df, error = generate_summary_statistics(filtered_df, action)
                    if error:
                        st.error(error)
                        logger.error(f"Summary error: {error}")
                    else:
                        render_summary_result(summary_df, description)
                else:
                    prepared_df, error = prepare_data_for_visualization(filtered_df, action)
                    if error:
                        st.error(error)
                        logger.error(f"Data prep error: {error}")
                    else:
                        fig, error = generate_visualization(prepared_df, action, description)
                        if error:
                            st.error(error)
                            logger.error(f"Visualization error: {error}")
                        else:
                            render_visualization_result(fig, description)
    else:
        if llm_provider == "manual":
            st.markdown("## Manual Visualization Builder")
            st.markdown("Select the type of visualization and parameters below:")
            action, description = create_action_from_ui(df)
            if action:
                filtered_df = df.copy()
                if action["type"] == "summarize":
                    summary_df, error = generate_summary_statistics(filtered_df, action)
                    if error:
                        st.error(error)
                        logger.error(f"Summary error: {error}")
                    else:
                        render_summary_result(summary_df, description)
                else:
                    prepared_df, error = prepare_data_for_visualization(filtered_df, action)
                    if error:
                        st.error(error)
                        logger.error(f"Data prep error: {error}")
                    else:
                        fig, error = generate_visualization(prepared_df, action, description)
                        if error:
                            st.error(error)
                            logger.error(f"Visualization error: {error}")
                        else:
                            render_visualization_result(fig, description)

if __name__ == "__main__":
    logger.info("Executing main")
    main()