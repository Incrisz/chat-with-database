import os
import openai
import streamlit as st
import pymysql
import psycopg2
from dotenv import load_dotenv, set_key
from pygments import highlight
from pygments.lexers import SqlLexer
from pygments.formatters.html import HtmlFormatter
import google.generativeai as genai

st.set_page_config(page_title="DB Chat Assistant", layout="wide")
load_dotenv()

if "config_expanded" not in st.session_state:
    st.session_state.config_expanded = True  # start expanded

with st.sidebar.expander("🛠️ Configuration Panel", expanded=st.session_state.config_expanded):

    st.title("Database Configuration")
    config_mode = st.radio("Configuration Mode", ["Manual Entry"])

    if config_mode == "Manual Entry":
        db_type = st.selectbox("Database Type", ["mysql", "postgresql"], index=0)
        db_host = st.text_input("Host", os.getenv("DB_HOST", "localhost"))
        db_port = st.number_input("Port", value=int(os.getenv("DB_PORT", 3306 if db_type == "mysql" else 5432)))
        db_user = st.text_input("User", os.getenv("DB_USER", "root"))
        db_password = st.text_input("Password", type="password", value=os.getenv("DB_PASSWORD", ""))
        db_name = st.text_input("Database Name", os.getenv("DB_NAME", "testdb"))
    else:
        db_type = os.getenv("DB_TYPE", "mysql").lower()
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", 3306))
        db_user = os.getenv("DB_USER", "root")
        db_password = os.getenv("DB_PASSWORD", "")
        db_name = os.getenv("DB_NAME", "testdb")

    st.header("AI Configuration")
    ai_provider = st.selectbox("Choose AI Provider", ["OPENAI", "GEMINI"], index=0 if os.getenv("AI_PROVIDER", "OPENAI").upper() == "OPENAI" else 1)

    if ai_provider == "OPENAI":
        openai_api_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
        openai_model = st.text_input("OpenAI Model", value=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"))
        gemini_api_key = ""
        gemini_model = ""
    else:
        gemini_api_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
        gemini_model = st.text_input("Gemini Model", value=os.getenv("GEMINI_MODEL", "gemini-1.5-pro"))
        openai_api_key = ""
        openai_model = ""

    if st.button("💾 Save Configuration"):
        dotenv_path = ".env"
        set_key(dotenv_path, "DB_TYPE", db_type)
        set_key(dotenv_path, "DB_HOST", db_host)
        set_key(dotenv_path, "DB_PORT", str(db_port))
        set_key(dotenv_path, "DB_USER", db_user)
        set_key(dotenv_path, "DB_PASSWORD", db_password)
        set_key(dotenv_path, "DB_NAME", db_name)
        set_key(dotenv_path, "AI_PROVIDER", ai_provider)
        if ai_provider == "OPENAI":
            set_key(dotenv_path, "OPENAI_API_KEY", openai_api_key)
            set_key(dotenv_path, "OPENAI_MODEL", openai_model)
            set_key(dotenv_path, "GEMINI_API_KEY", "")
            set_key(dotenv_path, "GEMINI_MODEL", "")
        else:
            set_key(dotenv_path, "GEMINI_API_KEY", gemini_api_key)
            set_key(dotenv_path, "GEMINI_MODEL", gemini_model)
            set_key(dotenv_path, "OPENAI_API_KEY", "")
            set_key(dotenv_path, "OPENAI_MODEL", "")
        st.success("Configuration saved to .env file!")
        st.session_state.config_expanded = False
        st.experimental_rerun()

if not st.session_state.config_expanded:
    if st.sidebar.button("⚙️ Edit Configuration"):
        st.session_state.config_expanded = True
        st.experimental_rerun()

# -- rest of your app code below (SQL generation, execution, etc.) --


# Set API keys for use in code
openai.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
genai.configure(api_key=gemini_api_key or os.getenv("GEMINI_API_KEY"))

openai_model = openai_model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
gemini_model = gemini_model or os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
ai_provider = ai_provider or os.getenv("AI_PROVIDER", "OPENAI").upper()

# SQL syntax highlighting function
def highlight_sql(code, theme="monokai"):
    formatter = HtmlFormatter(style=theme, noclasses=True)
    return highlight(code, SqlLexer(), formatter)

# Connect to the database
def connect_to_db():
    if db_type == "postgresql":
        return psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name
        )
    elif db_type == "mysql":
        return pymysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
    else:
        raise ValueError("Unsupported DB_TYPE")

# Generate SQL query using AI
def generate_sql(prompt):
    system_prompt = f"You are an expert SQL assistant for a {db_type} database. Generate only the SQL query, nothing else."

    if ai_provider == "GEMINI":
        model = genai.GenerativeModel(gemini_model)
        response = model.generate_content(f"{system_prompt}\nQuery: {prompt}")
        try:
            return response.text.strip()
        except AttributeError:
            return response.candidates[0].content.parts[0].text.strip()
    elif ai_provider == "OPENAI":
        response = openai.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    else:
        raise ValueError("Unsupported AI_PROVIDER. Use 'OPENAI' or 'GEMINI'.")

# Execute SQL query and fetch results
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


# Chat Display
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

# Input area
user_prompt = st.text_area("Ask something about your database:", placeholder="E.g. Show me all users who signed up in the last 7 days.")

# Generate and Execute
if st.button("Generate & Execute SQL"):
    if not user_prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner(f"Generating SQL with {ai_provider}..."):
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

