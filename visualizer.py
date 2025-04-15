import streamlit as st
import plotly.express as px
import pandas as pd
import logging
from data_processor import detect_time_columns

logger = logging.getLogger(__name__)

def generate_visualization(df, action, description):
    action_type = action.get("type", "").lower()
    try:
        if action_type == "histogram":
            column = action.get("column")
            return px.histogram(
                df, x=column, title=f"Histogram of {column}",
                labels={column: column.capitalize()}, template="plotly_white"
            ), None

        elif action_type == "bar":
            x, y = action.get("x"), action.get("y")
            if y:
                return px.bar(
                    df, x=x, y=y, title=f"Bar Chart of {x} vs {y}",
                    labels={x: x.capitalize(), y: y.capitalize()}, template="plotly_white"
                ), None
            value_counts = df[x].value_counts().reset_index()
            value_counts.columns = [x, "count"]
            return px.bar(
                value_counts, x=x, y="count", title=f"Count of {x}",
                labels={x: x.capitalize(), "count": "Count"}, template="plotly_white"
            ), None

        elif action_type == "scatter":
            x, y = action.get("x"), action.get("y")
            return px.scatter(
                df, x=x, y=y, title=f"Scatter Plot of {x} vs {y}",
                labels={x: x.capitalize(), y: y.capitalize()}, template="plotly_white"
            ), None

        elif action_type == "line":
            x, y = action.get("x"), action.get("y")
            df_sorted = df.sort_values(by=x) if pd.api.types.is_datetime64_dtype(df[x]) else df
            return px.line(
                df_sorted, x=x, y=y, title=f"Line Chart of {y} {'over' if pd.api.types.is_datetime64_dtype(df[x]) else 'vs'} {x}",
                labels={x: x.capitalize(), y: y.capitalize()}, template="plotly_white"
            ), None

        return None, f"Visualization type '{action_type}' not supported."
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        return None, f"Error generating visualization: {str(e)}"

def generate_summary_statistics(df, action):
    try:
        columns = action.get("columns", df.columns.tolist())
        summary_data = []
        for col in columns:
            if col not in df.columns:
                continue
            stats = {"Column": col, "Type": str(df[col].dtype)}
            if pd.api.types.is_numeric_dtype(df[col]):
                stats.update({
                    "Count": df[col].count(), "Missing": df[col].isna().sum(),
                    "Mean": df[col].mean(), "Median": df[col].median(),
                    "Min": df[col].min(), "Max": df[col].max(), "Std Dev": df[col].std()
                })
            else:
                stats.update({
                    "Count": df[col].count(), "Missing": df[col].isna().sum(),
                    "Unique Values": df[col].nunique()
                })
                if df[col].nunique() < 50:
                    top_value = df[col].value_counts().idxmax() if not df[col].value_counts().empty else None
                    top_count = df[col].value_counts().max() if not df[col].value_counts().empty else 0
                    top_pct = (top_count / df[col].count()) * 100 if df[col].count() > 0 else 0
                    stats.update({
                        "Most Frequent": str(top_value), "Frequency": top_count,
                        "Percentage": f"{top_pct:.2f}%"
                    })
            summary_data.append(stats)
        return pd.DataFrame(summary_data), None
    except Exception as e:
        logger.error(f"Error generating summary statistics: {str(e)}")
        return None, f"Error generating summary statistics: {str(e)}"

def create_action_from_ui(df):
    st.markdown("### Select Visualization Type")
    viz_type = st.selectbox(
        "Visualization Type", ["histogram", "bar", "scatter", "line", "summarize"],
        index=0, help="Select the type of visualization to create"
    )
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    all_cols = df.columns.tolist()
    action = {"type": viz_type}
    description = ""

    if viz_type == "histogram":
        column = st.selectbox("Select Column", options=numeric_cols) if numeric_cols else st.selectbox("Select Column", options=all_cols)
        action["column"] = column
        description = f"Distribution of {column}"

    elif viz_type == "bar":
        x = st.selectbox("Select X (Category) Column", options=all_cols)
        action["x"] = x
        use_y = st.checkbox("Use Y Value (instead of count)", value=False)
        if use_y and numeric_cols:
            y = st.selectbox("Select Y (Value) Column", options=numeric_cols)
            action["y"] = y
            description = f"Bar chart showing {y} by {x}"
        else:
            description = f"Bar chart showing count of {x}"

    elif viz_type == "scatter":
        if len(numeric_cols) >= 2:
            x = st.selectbox("Select X Column", options=numeric_cols, index=0)
            remaining_cols = [col for col in numeric_cols if col != x]
            y = st.selectbox("Select Y Column", options=remaining_cols, index=0)
            action["x"], action["y"] = x, y
            description = f"Scatter plot showing relationship between {x} and {y}"
        else:
            st.warning("You need at least 2 numeric columns for a scatter plot")
            return None, None

    elif viz_type == "line":
        time_cols = detect_time_columns(df)
        x_options = time_cols if time_cols else all_cols
        x = st.selectbox("Select X (Time) Column", options=x_options)
        if numeric_cols:
            y = st.selectbox("Select Y (Value) Column", options=numeric_cols)
            action["x"], action["y"] = x, y
            description = f"Line chart showing {y} over {x}"
        else:
            st.warning("You need at least 1 numeric column for the Y axis")
            return None, None

    elif viz_type == "summarize":
        use_all_cols = st.checkbox("Summarize all columns", value=True)
        if not use_all_cols:
            selected_cols = st.multiselect("Select columns to summarize", options=all_cols, default=all_cols[:min(5, len(all_cols))])
            action["columns"] = selected_cols
            description = f"Summary statistics for columns: {', '.join(selected_cols)}"
        else:
            action["columns"] = all_cols
            description = "Summary statistics for all columns"

    return action, description