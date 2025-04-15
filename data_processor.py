import streamlit as st
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def load_data(uploaded_file):
    try:
        return pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logger.error(f"Data loading error: {str(e)}")
        return None

def validate_data(df):
    if df is None:
        return False, "No data loaded."
    if df.empty:
        return False, "The uploaded file contains no data."
    if df.shape[1] < 1:
        return False, "The uploaded file contains no columns."
    return True, "Data validation successful."

def extract_schema(df):
    return {col: str(df[col].dtype) for col in df.columns}

def detect_time_columns(df):
    time_columns = []
    for col in df.columns:
        if df[col].dtype != "object" and not pd.api.types.is_string_dtype(df[col].dtype):
            continue
        sample = df[col].dropna().head(10)
        if len(sample) == 0:
            continue
        try:
            pd.to_datetime(sample, errors="raise")
            time_columns.append(col)
        except:
            pass
    return time_columns

def prepare_data_for_visualization(df, action):
    action_type = action.get("type", "").lower()
    try:
        if action_type == "histogram":
            column = action.get("column")
            if column not in df.columns:
                return None, f"Column '{column}' not found in the dataset."
            if not pd.api.types.is_numeric_dtype(df[column]):
                try:
                    df[column] = pd.to_numeric(df[column], errors="coerce")
                    return df, None
                except:
                    return None, f"Column '{column}' is not numeric and could not be converted."
            return df, None

        elif action_type == "bar":
            x, y = action.get("x"), action.get("y")
            if x not in df.columns:
                return None, f"Column '{x}' not found in the dataset."
            if y and y not in df.columns:
                return None, f"Column '{y}' not found in the dataset."
            if y and not pd.api.types.is_numeric_dtype(df[y]):
                try:
                    df[y] = pd.to_numeric(df[y], errors="coerce")
                except:
                    return None, f"Column '{y}' is not numeric and could not be converted."
            return df, None

        elif action_type == "scatter":
            x, y = action.get("x"), action.get("y")
            if x not in df.columns or y not in df.columns:
                missing = [f"'{x}'" if x not in df.columns else "", f"'{y}'" if y not in df.columns else ""]
                return None, f"Columns {' and '.join(filter(None, missing))} not found in the dataset."
            for col, name in [(x, "x"), (y, "y")]:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    except:
                        return None, f"{name}-axis column '{col}' is not numeric and could not be converted."
            return df, None

        elif action_type == "line":
            x, y = action.get("x"), action.get("y")
            if x not in df.columns or y not in df.columns:
                missing = [f"'{x}'" if x not in df.columns else "", f"'{y}'" if y not in df.columns else ""]
                return None, f"Columns {' and '.join(filter(None, missing))} not found in the dataset."
            if not pd.api.types.is_datetime64_dtype(df[x]):
                try:
                    df[x] = pd.to_datetime(df[x], errors="coerce")
                except:
                    return None, f"Column '{x}' could not be converted to datetime for time series."
            if not pd.api.types.is_numeric_dtype(df[y]):
                try:
                    df[y] = pd.to_numeric(df[y], errors="coerce")
                except:
                    return None, f"Column '{y}' is not numeric and could not be converted."
            return df, None

        elif action_type == "summarize":
            columns = action.get("columns", df.columns.tolist())
            for col in columns:
                if col not in df.columns:
                    return None, f"Column '{col}' specified for summary not found in the dataset."
            return df, None

        return None, f"Unknown action type: {action_type}"
    except Exception as e:
        logger.error(f"Error preparing data: {str(e)}")
        return None, f"Error preparing data: {str(e)}"