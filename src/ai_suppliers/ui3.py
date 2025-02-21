import sys
if sys.platform == "linux":  # Only apply on Streamlit Cloud (Linux)
    import pysqlite3
    sys.modules['sqlite3'] = pysqlite3
import sys
import os

# Ensure ChromaDB uses system SQLite
os.environ["ALLOW_CHROMA_DB_SYSTEM_SQLITE"] = "1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get current script directory
sys.path.append(os.path.join(BASE_DIR, "src", "ai_suppliers"))
import re

import streamlit as st
import requests
import time
import threading
import pandas as pd  # Required for better table handling

from crew import  AiSuppliers
logo_url = os.path.join(BASE_DIR, "search.jpg")

# Set Streamlit page configuration
st.set_page_config(page_title="Supplier Acquisition Tool", layout="wide",page_icon=logo_url)

# ---------------------------
# Define Logo & Styling
# ---------------------------


# Custom CSS to fix spacing and table overflow
st.markdown(
    """
    <style>
        /* Reduce excess space */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        /* Table styling */
        .dataframe {
            width: 100% !important;
            overflow-x: auto;
        }

        /* Make the header centered */
        .header {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }

        .header img {
            height: 70px;
            margin-right: 15px;
        }

        .title {
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
        }

        /* Improve final answer box */
        .final-answer-box {
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 6px;
            background-color: #fff;
            margin: 10px 0;
            white-space: pre-wrap;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
            overflow-x: auto;  /* Prevents table overflow */
        }

        /* Sidebar header */
        .sidebar-header {
            font-size: 1.2rem;
            font-weight: 600;
            color: #34495e;
            margin-bottom: 10px;
        }

        /* Buttons */
        .stButton button {
            background-color: #2c3e50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 10px 16px;
            font-size: 1rem;
        }

        .stButton button:hover {
            background-color: #34495e;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Header with Logo & Title
# ---------------------------
col1, col2 = st.columns([1, 6])
with col1:
    st.image(logo_url, width=100)
with col2:
    st.markdown("<h1 class='title'>Supplier Acquisition Tool</h1>", unsafe_allow_html=True)

# ---------------------------
# Sidebar: Query Input
# ---------------------------
st.sidebar.markdown("<div class='sidebar-header'>Enter your Brand</div>", unsafe_allow_html=True)
user_query = st.sidebar.text_area(
    "Brand",
    value="",
    placeholder="Enter the name of Brand you want to search for",
    height=80,
)
# List of European countries
countries_europe = [
    "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus",
    "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus",
    "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Georgia",
    "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo",
    "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Malta",
    "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia", "Norway",
    "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia",
    "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine",
    "United Kingdom", "Vatican City"
]

# List of American countries (North, Central, South America, and the Caribbean)
countries_america = [
    "Antigua and Barbuda", "Argentina", "Bahamas", "Barbados", "Belize",
    "Bolivia", "Brazil", "Canada", "Chile", "Colombia", "Costa Rica",
    "Cuba", "Dominica", "Dominican Republic", "Ecuador", "El Salvador",
    "Grenada", "Guatemala", "Guyana", "Haiti", "Honduras", "Jamaica",
    "Mexico", "Nicaragua", "Panama", "Paraguay", "Peru", "Saint Kitts and Nevis",
    "Saint Lucia", "Saint Vincent and the Grenadines", "Suriname", "Trinidad and Tobago",
    "United States", "Uruguay", "Venezuela"
]

# List of Asian countries
countries_asia = [
    "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan",
    "Brunei", "Cambodia", "China", "Cyprus", "Georgia", "India", "Indonesia",
    "Iran", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan", "Kuwait",
    "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia",
    "Myanmar", "Nepal", "North Korea", "Oman", "Pakistan", "Palestine", "Philippines",
    "Qatar", "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria",
    "Taiwan", "Tajikistan", "Thailand", "Timor-Leste", "Turkey", "Turkmenistan",
    "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen"
]

# Combine all lists into one, remove duplicates, and sort the result
all_countries = sorted(list(set(countries_europe + countries_america + countries_asia)))

# New: Country selection dropdown added to sidebar
selected_country = st.sidebar.selectbox(
    "Select Country",
    options=all_countries,
    index=0,
)
status_container = st.empty()
search_button = st.sidebar.button("Search")


def run_crew_process(topic, country):
    inputs = {"topic": topic, "country": country}
    st.write("Debug: Running crew process with inputs:", inputs)

    # Call the Crew AI kickoff function directly
    result = AiSuppliers().crew().kickoff(inputs=inputs)
    st.write("Debug: Raw crew process result:", result)
    return result
# ---------------------------
# Main Page: Search Logic & Display
# ---------------------------
if not user_query.strip():
    st.write("Enter your query in the sidebar and click **Search** to retrieve supplier details.")
if search_button:
    if not user_query.strip():
        st.error("Please enter a valid query.")
    else:
        status_container.markdown("*Running Crew AI process...*")

        # Run the Crew AI process
        result = run_crew_process(user_query, selected_country)

        # Debug: Print the entire result for troubleshooting purposes
        # st.write("Debug: Full result dictionary:", result)

        # Extract final answer text based on common keys
        if "result" in result and "raw" in result["result"]:
            final_text = result["result"]["raw"]
            # st.write("Debug: Extracted final_text from result['result']['raw']:", final_text)
        elif "tasks_output" in result and len(result["tasks_output"]) > 0:
            final_text = result["tasks_output"][-1].get("raw", "")
            # st.write("Debug: Extracted final_text from result['tasks_output'][-1]['raw']:", final_text)
        else:
            final_text = str(result)
            # st.write("Debug: Using entire result as final_text:", final_text)

        # Clean the final_text from any markdown code block delimiters and extra newlines
        final_text = final_text.replace("```markdown", "").replace("```", "").strip()
        final_text = "\n\n".join([line.strip() for line in final_text.splitlines() if line.strip()])

        # Display the final answer in a styled container
        st.markdown(f"<div class='final-answer-box'>{final_text}</div>", unsafe_allow_html=True)
        st.success("Supplier research is completed.")

        # If supplier table data is available in the result, display it
        supplier_data = result.get("suppliers", [])
        if supplier_data:
            df = pd.DataFrame(supplier_data)
            st.dataframe(df, use_container_width=True)