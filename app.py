import os
import openai
import streamlit as st
import pymysql
import psycopg2
from dotenv import load_dotenv
from pygments import highlight
from pygments.lexers import SqlLexer
from pygments.formatters import HtmlFormatter
import google.generativeai as genai
import re


# Load .env configuration
load_dotenv()

# Set API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load DB config
DB_TYPE = os.getenv("DB_TYPE", "mysql").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "testdb")
AI_PROVIDER = os.getenv("AI_PROVIDER", "OPENAI").upper()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# Utility: SQL syntax highlighting
def highlight_sql(code, theme="monokai"):
    formatter = HtmlFormatter(style=theme, noclasses=True)
    return highlight(code, SqlLexer(), formatter)

# Connect to DB
def connect_to_db():
    if DB_TYPE == "postgresql":
        return psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
    elif DB_TYPE == "mysql":
        return pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    else:
        raise ValueError("Unsupported DB_TYPE")

# Generate SQL with AI
def generate_sql(prompt):
    system_prompt = f"You are an expert SQL assistant for a {DB_TYPE} database. Generate only the SQL query, nothing else."

    if AI_PROVIDER == "GEMINI":
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(f"{system_prompt}\nQuery: {prompt}")
        try:
            return response.text.strip()
        except AttributeError:
            return response.candidates[0].content.parts[0].text.strip()

    elif AI_PROVIDER == "OPENAI":
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    else:
        raise ValueError("Unsupported AI_PROVIDER. Use 'OPENAI' or 'GEMINI'.")


# Execute query
def execute_query(sql):
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        if sql.lower().strip().startswith("select"):
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            return columns, data, None
        else:
            conn.commit()
            return None, "Query executed successfully.", None
    except Exception as e:
        return None, None, str(e)
    finally:
        cursor.close()
        conn.close()

# ─────────────────────────────
# Streamlit UI Starts Here
# ─────────────────────────────
st.set_page_config(page_title="DB Chat Assistant", layout="wide")
st.title("💬 Natural Language to SQL - DB Chat Assistant")

theme = st.selectbox("🎨 Choose SQL Highlight Theme", [
    "default", "monokai", "dracula", "friendly", "colorful",
    "murphy", "native", "solarized-dark", "solarized-light", "vs"
], index=1)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar - Chat History
with st.sidebar:
    st.header("📝 Chat History")
    if st.session_state.chat_history:
        for i, record in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Query #{len(st.session_state.chat_history) - i}"):
                st.markdown(f"**Prompt:** {record['prompt']}")
                st.markdown(highlight_sql(record["sql"], theme), unsafe_allow_html=True)
                if record['error']:
                    st.error(f"Error: {record['error']}")
                elif isinstance(record['data'], str):
                    st.success(record['data'])
                elif record['data']:
                    st.write(f"Result: {len(record['data'])} rows")
                else:
                    st.info("No results or non-select query.")
    else:
        st.info("No chat history yet.")


# Chat UI Display
st.subheader("🗨️ Chat with Database")

if st.session_state.chat_history:
    for record in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(record["prompt"])
        with st.chat_message("assistant"):
            st.markdown("**Generated SQL:**")
            st.markdown(highlight_sql(record["sql"], theme), unsafe_allow_html=True)
            if record["error"]:
                st.error(f"Error: {record['error']}")
            elif isinstance(record["data"], str):
                st.success(record["data"])
            elif record["data"]:
                st.dataframe(record["data"], use_container_width=True, hide_index=True)
            else:
                st.info("No results returned.")

# Main Input Area
user_prompt = st.text_area("Ask something about your database:", placeholder="E.g. Show me all users who signed up in the last 7 days.")

# Generate & Execute Button
if st.button("Generate & Execute SQL"):
    if not user_prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner(f"Generating SQL with {AI_PROVIDER}..."):
            sql_query = generate_sql(user_prompt)




        st.markdown(highlight_sql(sql_query, theme), unsafe_allow_html=True)

        execute = st.checkbox("Execute query?", value=True)

        if execute:
            with st.spinner("Executing SQL..."):
                columns, data, error = execute_query(sql_query)

            if error:
                st.error(f"Error: {error}")
            elif isinstance(data, str):
                st.success(data)
            else:
                if data:
                    st.success("Query executed successfully.")
                    st.dataframe(data, use_container_width=True, hide_index=True)
                else:
                    st.info("Query executed, but returned no results.")
        else:
            columns, data, error = None, None, None

        # Save to history
        st.session_state.chat_history.append({
            "prompt": user_prompt,
            "sql": sql_query,
            "columns": columns,
            "data": data,
            "error": error,
        })

# Footer
st.markdown("---")
st.markdown("<center>Created by <b>Incrisz</b></center>", unsafe_allow_html=True)
