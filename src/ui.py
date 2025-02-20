import re

import streamlit as st
import requests
import time
import threading
import pandas as pd  # Required for better table handling

# Set Streamlit page configuration
st.set_page_config(page_title="Supplier Acquisition Tool", layout="wide", page_icon="search.jpg")

# ---------------------------
# Define Logo & Styling
# ---------------------------
logo_url = "search.jpg"

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

search_button = st.sidebar.button("Search")

# ---------------------------
# Main Page: Search Logic & Display
# ---------------------------
if not user_query.strip():
    st.write("Enter your query in the sidebar and click **Search** to retrieve supplier details.")

if search_button:
    if not user_query.strip():
        st.error("Please enter a valid query.")
    else:
        result_container = st.empty()
        status_container = st.empty()

        API_URL = "http://localhost:8001/run"
        # Payload now includes both the query and the selected country
        payload = {"topic": user_query, "country": selected_country}

        response_container = {"response": None}

        # Function to make the API request
        def make_request():
            try:

                response_container["response"] = requests.post(API_URL, json=payload)
            except Exception as e:
                response_container["response"] = None
                st.error(f"An error occurred while calling the API: {e}")

        # Start API call in separate thread
        request_thread = threading.Thread(target=make_request)
        request_thread.start()

        spinner_messages = [
            "Connecting to the supplier database...",
            "Fetching relevant supplier details...",
            "Compiling supplier information...",
            "Analyzing domain metrics...",
            "Extracting Trustpilot reviews...",
            "Retrieving ZoomInfo company data...",
            "Integrating data sources...",
            "Validating URL formats...",
            "Performing error checks...",
            "Finalizing results..."
        ]

        i = 0

        while request_thread.is_alive():
            current_message = spinner_messages[i % len(spinner_messages)]
            status_container.markdown(f"*{current_message}*")
            time.sleep(6)
            i += 1

        request_thread.join()

        response = response_container["response"]
        if response:
            data = response.json()  # Simulated response as a dict
            # Extract final answer text from tasks_output if available; otherwise fallback to raw
            tasks_output = data.get("result", {}).get("tasks_output", [])
            final_text = tasks_output[-1].get("raw", "") if tasks_output else data.get("result", {}).get("raw", "")
            final_text = str(final_text).strip()
            # Remove markdown code block delimiters and compress multiple newlines
            final_text = final_text.replace("```markdown", "").replace("```", "").strip()
            final_text = re.sub(r'\n\s*\n', '\n\n', final_text)

            # Convert markdown to HTML so that headers (like # Supplier Research Report) render properly
            html_text = st.markdown(final_text)

            # Display the final answer box with styling and rendered HTML content
            st.markdown(f"<div class='final-answer-box'>{html_text}</div>", unsafe_allow_html=True)
            st.success("Supplier research is completed.")

            # Check for supplier table data and display it if available
            supplier_data = data.get("suppliers", [])
            if supplier_data:
                df = pd.DataFrame(supplier_data)
                st.dataframe(df, use_container_width=True)
            else:
               pass
        else:
            st.error("Failed to fetch results from the backend server.")