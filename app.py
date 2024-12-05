import streamlit as st
import psycopg2
from psycopg2 import sql
import pandas as pd
import plotly.express as px

# Database connection function
def get_connection():
    try:
        # Fetch credentials from Streamlit's secrets
        secrets = st.secrets["heroku"]
        return psycopg2.connect(
            host=secrets["host"],
            port=secrets["port"],
            dbname=secrets["dbname"],
            user=secrets["user"],
            password=secrets["password"],
            sslmode="require"
        )
    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None

# Execute a query
def execute_query(query, params=None):
    try:
        conn = get_connection()
        if conn is None:
            return "Database connection error."
        cursor = conn.cursor()
        cursor.execute(query, params)
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = "Query executed successfully!"
        cursor.close()
        conn.close()
        return result
    except Exception as e:
        return str(e)

# Home page
def home():
    st.title("Medical Records Database")
    st.write("Welcome to the Medical Records Database app!")
    st.write("Use the sidebar to navigate through the application.")

# Query page
def query_page():
    st.title("Run Queries")
    st.write("Enter your SQL query below to execute it on the database.")
    query = st.text_area("Enter your SQL query:")
    if st.button("Execute Query"):
        result = execute_query(query)
        if isinstance(result, str):
            st.error(result)
        else:
            st.write(result)

# Insert record
def insert_page():
    st.title("Insert Records")
    table_name = st.selectbox(
        "Select Table",
        ["patient", "doctor", "hospital", "insurance", "treatment", "visits"]
    )
    st.write(f"Insert data into {table_name}")

    # Dynamically fetch column names for the selected table
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' AND column_default IS NULL
            """)
            columns = [row[0] for row in cursor.fetchall()]
            conn.close()
            st.write("Columns for the table (excluding auto-increment columns):")
            st.write(columns)

            # Prompt user to enter values
            values = st.text_input(f"Enter values for {', '.join(columns)} (comma-separated):")

            if st.button("Insert Record"):
                try:
                    # Prepare placeholders for query
                    placeholders = ", ".join(["%s"] * len(columns))
                    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
                    
                    # Split and execute query
                    val_list = values.split(",")
                    result = execute_query(query, val_list)
                    st.success(result)
                except Exception as e:
                    st.error(f"Error inserting record: {e}")
    except Exception as e:
        st.error(f"Error fetching columns: {e}")



# Delete record
def delete_page():
    st.title("Delete Records")
    table_name = st.selectbox(
        "Select Table",
        ["patient", "doctor", "hospital", "insurance", "treatment", "visits"]
    )
    condition = st.text_input(
        "Enter condition for deletion (e.g., patient_id = 1):"
    )
    if st.button("Delete Record"):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        result = execute_query(query)
        if "successfully" in result:
            st.success(result)
        else:
            st.error(result)

# Visualization page
def visualization_page():
    st.title("Visualizations")
    st.write("Generate visual insights from the database.")
    visual_option = st.selectbox(
        "Select Visualization Type",
        [
            "Patient Demographics",
            "Admission Types",
            "Billing Amounts",
            "Treatment Results"
        ]
    )
    if st.button("Generate Visualization"):
        try:
            if visual_option == "Patient Demographics":
                query = "SELECT gender, COUNT(*) AS count FROM patient GROUP BY gender;"
                data = execute_query(query)
                df = pd.DataFrame(data, columns=["Gender", "Count"])
                fig = px.pie(df, values="Count", names="Gender", title="Gender Distribution")
                st.plotly_chart(fig)

            elif visual_option == "Admission Types":
                query = "SELECT admission_type, COUNT(*) AS count FROM visits GROUP BY admission_type;"
                data = execute_query(query)
                df = pd.DataFrame(data, columns=["Admission Type", "Count"])
                fig = px.bar(df, x="Admission Type", y="Count", title="Admission Types")
                st.plotly_chart(fig)

            elif visual_option == "Billing Amounts":
                query = "SELECT billing_amount FROM visits;"
                data = execute_query(query)
                df = pd.DataFrame(data, columns=["Billing Amount"])
                fig = px.histogram(df, x="Billing Amount", title="Billing Amount Distribution")
                st.plotly_chart(fig)

            elif visual_option == "Treatment Results":
                query = "SELECT medical_condition, COUNT(*) AS count FROM treatment GROUP BY medical_condition;"
                data = execute_query(query)
                df = pd.DataFrame(data, columns=["Medical Condition", "Count"])
                fig = px.pie(df, values="Count", names="Medical Condition", title="Treatment Results")
                st.plotly_chart(fig)

            st.success("Visualization generated successfully!")
        except Exception as e:
            st.error(str(e))

# Main navigation
def main():
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio(
        "Go to",
        ["Home", "Query Page", "Insert Records", "Delete Records", "Visualizations"]
    )
    if menu == "Home":
        home()
    elif menu == "Query Page":
        query_page()
    elif menu == "Insert Records":
        insert_page()
    elif menu == "Delete Records":
        delete_page()
    elif menu == "Visualizations":
        visualization_page()

if __name__ == "__main__":
    main()
