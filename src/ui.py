import streamlit as st
import requests
import time
import threading
import pandas as pd  # Required for better table handling

# Set Streamlit page configuration
st.set_page_config(page_title="Supplier Acquisition Tool", layout="wide", page_icon="🔍")

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
    st.image(logo_url, width=70)
with col2:
    st.markdown("<h1 class='title'>Supplier Acquisition Tool</h1>", unsafe_allow_html=True)

# ---------------------------
# Sidebar: Query Input
# ---------------------------
st.sidebar.markdown("<div class='sidebar-header'>Enter your Query</div>", unsafe_allow_html=True)
user_query = st.sidebar.text_area(
    "Query",
    value="",
    placeholder="Find suppliers of Garmin brand along with all necessary supplier details in the US.",
    height=80,
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
        payload = {"topic": user_query}

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
            "Finalizing results..."
        ]
        i = 0

        while request_thread.is_alive():
            current_message = spinner_messages[i % len(spinner_messages)]
            status_container.markdown(f"*{current_message}*")
            time.sleep(1)
            i += 1

        request_thread.join()

        response = response_container["response"]
        if response is not None and response.status_code == 200:
            data = response.json()

            # Extract final answer text
            tasks_output = data.get("result", {}).get("tasks_output", [])
            final_text = tasks_output[-1].get("raw", "") if tasks_output else data.get("result", {}).get("raw", "")
            final_text = str(final_text).strip()

            # Display Final Answer Box
            st.markdown(f"<div class='final-answer-box'>{final_text}</div>", unsafe_allow_html=True)
            st.success("Supplier research is completed.")

            # Check for table data and display it properly
            supplier_data = data.get("suppliers", [])
            if supplier_data:
                df = pd.DataFrame(supplier_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No supplier data found.")
        else:
            st.error("Failed to fetch results from the backend server.")
