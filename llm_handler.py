import streamlit as st
import json
import openai
import re
import requests
import logging

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_HOST = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3"

openai_api_key = None

def safe_json_parse(text):
    json_match = re.search(r"```json\s*([\s\S]*?)\s*```|{[\s\S]*}", text)
    if json_match:
        json_str = json_match.group(1) if json_match.group(1) else json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    try:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        pass
    return None

def construct_prompt(schema, time_columns, query):
    schema_text = "\n".join([f"- {col}: {dtype}" for col, dtype in schema.items()])
    time_cols_text = "None detected" if not time_columns else ", ".join(time_columns)
    return f"""You are a data visualization and analysis expert. Help me interpret the following query about a dataset.

Dataset Schema:
{schema_text}

Time-based columns: {time_cols_text}

User Query: "{query}"

Based on the query and dataset schema, determine the most appropriate visualization or analysis. 
Respond with JSON in the following format:

```json
{{
  "action": {{
    "type": "[visualization or analysis type]",
    "parameters": "[column names and settings]"
  }},
  "description": "[explanation of what the visualization or analysis shows]"
}}
```

For the action type, choose one of:
- "histogram": For distribution of a single numeric column. Parameters MUST include "column" (a single column name from the schema). If the query is ambiguous (e.g., "adult male"), infer the most relevant numeric column (e.g., "age") and explain your choice in the description.
- "bar": For comparison across categories. Parameters MUST include "x" (category column) and optionally "y" (value column, otherwise count will be used).
- "scatter": For relationship between two numeric columns. Parameters MUST include "x" and "y".
- "line": For time series data. Parameters MUST include "x" (time column) and "y" (value column).
- "summarize": For statistical summary. Parameters should include "columns" (list of column names to summarize, or empty for all).

- If the query implies filtering the dataset (e.g., "histogram of adult male" where "sex" is "male"), include a "filter" key in the action with conditions in the format:
  "filter": [
    {{"column": "[column name]", "value": "[value to filter by]"}},
    {{"column": "[column name]", "operator": ">=", "value": [number]}}
  ]
  For example, for "adult male", you might include:
  "filter": [
    {{"column": "sex", "value": "male"}},
    {{"column": "age", "operator": ">=", "value": 18}}
  ]

**Important Instructions**:
- You MUST include all required parameters for the chosen action type. For example, a "histogram" action MUST have a "column" parameter.
- If the query is ambiguous or doesn’t directly specify a column (e.g., "histogram of adult male"), infer the most relevant column based on the schema. For example, if the query mentions "adult male" and the schema has a "sex" column (with values like "male") and an "age" column, assume the user wants a histogram of "age" for males and note this in the description.
- Only choose columns that exist in the schema. Do not invent column names.
- Ensure the JSON is valid and well-formed. Do not include any additional text outside the JSON.

Return only the JSON response.
"""

def query_openai(prompt, api_key):
    if not api_key:
        st.error("Please enter an OpenAI API key in the sidebar.")
        return None
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI query error: {str(e)}")
        st.error(f"Error communicating with OpenAI: {str(e)}")
        return None

def query_ollama(prompt, model="llama3", host="http://localhost:11434"):
    try:
        response = requests.post(
            f"{host}/api/generate",
            headers={"Content-Type": "application/json"},
            json={"model": model, "prompt": prompt, "stream": False}
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        logger.error(f"Ollama API error: Status {response.status_code}")
        st.error(f"Ollama API error: Status {response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Ollama query error: {str(e)}")
        st.error(f"Error communicating with Ollama: {str(e)}")
        return None

def query_llm(prompt, llm_provider, ollama_model=None, ollama_host=None, openai_api_key=None):
    if llm_provider == "openai":
        return query_openai(prompt, openai_api_key)
    elif llm_provider == "ollama":
        return query_ollama(prompt, model=ollama_model, host=ollama_host)
    st.error(f"Unknown LLM provider: {llm_provider}")
    return None

def parse_llm_response(response_text):
    if not response_text:
        return None, None, None, "No response received from the LLM."
    try:
        parsed = safe_json_parse(response_text)
        if not parsed:
            return None, None, None, "Could not parse LLM response as JSON."
        action = parsed.get("action", {})
        description = parsed.get("description", "No description provided.")
        if not isinstance(action, dict) or "type" not in action:
            return None, None, None, "Invalid action structure in LLM response."
        action_type = action.get("type", "").lower()

        filter_conditions = action.get("filter", None)
        if filter_conditions:
            if not isinstance(filter_conditions, list):
                return None, None, None, "Filter must be a list of condition dictionaries."
            for condition in filter_conditions:
                if not isinstance(condition, dict):
                    return None, None, None, "Each filter condition must be a dictionary."
                if "column" not in condition or "value" not in condition:
                    return None, None, None, "Filter condition missing 'column' or 'value' parameter."
                operator = condition.get("operator", "==")
                if operator not in ["==", ">=", "<=", ">", "<"]:
                    return None, None, None, f"Invalid filter operator: {operator}"

        if action_type == "histogram" and "column" not in action:
            return None, None, None, "Histogram action missing 'column' parameter."
        elif action_type == "bar" and "x" not in action:
            return None, None, None, "Bar chart action missing 'x' parameter."
        elif action_type == "scatter" and ("x" not in action or "y" not in action):
            return None, None, None, "Scatter plot action missing 'x' or 'y' parameter."
        elif action_type == "line" and ("x" not in action or "y" not in action):
            return None, None, None, "Line chart action missing 'x' or 'y' parameter."
        elif action_type == "summarize":
            pass
        else:
            return None, None, None, f"Unknown action type: {action_type}"
        return action, description, filter_conditions, None
    except Exception as e:
        logger.error(f"Error parsing LLM response: {str(e)}")
        return None, None, None, f"Error parsing LLM response: {str(e)}"

def check_ollama_connection(host):
    try:
        response = requests.get(f"{host}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False