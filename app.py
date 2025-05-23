import os
import openai
import streamlit as st
import mysql.connector
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

DB_TYPE = os.getenv("DB_TYPE", "mysql")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "testdb")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

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
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    else:
        raise ValueError("Unsupported DB_TYPE")

def generate_sql(prompt):
    response = openai.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": f"You are an expert SQL assistant for a {DB_TYPE} database."},
            {"role": "user", "content": f"Generate an SQL query for: {prompt}"}
        ],
        temperature=0
    )
    return response.choices[0].message['content'].strip()

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
            return None, f"Query executed successfully.", None
    except Exception as e:
        return None, None, str(e)
    finally:
        cursor.close()
        conn.close()

# Streamlit UI setup
st.set_page_config(page_title="DB Chat Assistant", layout="wide")
st.title("💬 Natural Language to SQL - DB Chat Assistant")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar - Chat history
with st.sidebar:
    st.header("📝 Chat History")
    if st.session_state.chat_history:
        for i, record in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"Query #{len(st.session_state.chat_history) - i}"):
                st.markdown(f"**Prompt:** {record['prompt']}")
                st.code(record['sql'], language="sql")
                if record['error']:
                    st.error(f"Error: {record['error']}")
                elif record['data']:
                    st.write(f"Result: {len(record['data'])} rows")
                else:
                    st.info("No results or non-select query.")
    else:
        st.info("No chat history yet.")

# Main UI for input
user_prompt = st.text_area("Ask something about your database:", placeholder="E.g. Show me all users who signed up in the last 7 days.")

if st.button("Generate & Execute SQL"):
    if not user_prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Generating SQL..."):
            sql_query = generate_sql(user_prompt)
        
        st.code(sql_query, language='sql')

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

        # Save to chat history
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
