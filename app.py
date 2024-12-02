import streamlit as st
import psycopg2
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Function to connect to the PostgreSQL database
def get_connection():
    return psycopg2.connect(
        dbname = os.getenv('DB_NAME'),
        user = os.getenv('DB_USERNAME'),
        password = os.getenv('DB_PASSWORD'),
        host = os.getenv('DB_HOST'),
        port = os.getenv('DB_PORT')
    )

# Function to execute SQL queries
def execute_query(query):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query)
        if query.strip().upper().startswith("SELECT"):
            # Fetch results for SELECT queries
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            return pd.DataFrame(rows, columns=colnames)
        else:
            # Commit changes for INSERT, UPDATE, DELETE
            conn.commit()
            return f"Query executed successfully: {query}"
    except Exception as e:
        return f"Error: {e}"
    finally:
        cur.close()
        conn.close()

# Streamlit UI
st.title("Medical Database Management")

# Query input box
st.subheader("Run SQL Queries")
query = st.text_area("Enter your SQL query:", height=150)

# Execute button
if st.button("Run Query"):
    if query.strip():
        result = execute_query(query)
        if isinstance(result, pd.DataFrame):
            st.write("Query Results:")
            st.dataframe(result)
        else:
            st.write(result)
    else:
        st.warning("Please enter a valid SQL query.")

# Example queries
st.subheader("Example Queries")
st.markdown("""
- **View all patients:** `SELECT * FROM patient;`
- **List all visits with patient and doctor details:** 
```sql
SELECT v.visit_id, p.name AS patient_name, d.doctor AS doctor_name, v.billing_amount 
FROM visits v 
JOIN patient p ON v.patient_id = p.patient_id 
JOIN doctor d ON v.doctor_id = d.doctor_id;
SELECT h.hospital, AVG(v.billing_amount) AS avg_billing 
FROM visits v 
JOIN hospital h ON v.hospital_id = h.hospital_id 
GROUP BY h.hospital;
""")