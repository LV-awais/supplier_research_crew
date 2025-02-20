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

# Combine lists of countries (Europe, America, Asia) and sort
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

countries_america = [
    "Antigua and Barbuda", "Argentina", "Bahamas", "Barbados", "Belize",
    "Bolivia", "Brazil", "Canada", "Chile", "Colombia", "Costa Rica",
    "Cuba", "Dominica", "Dominican Republic", "Ecuador", "El Salvador",
    "Grenada", "Guatemala", "Guyana", "Haiti", "Honduras", "Jamaica",
    "Mexico", "Nicaragua", "Panama", "Paraguay", "Peru", "Saint Kitts and Nevis",
    "Saint Lucia", "Saint Vincent and the Grenadines", "Suriname", "Trinidad and Tobago",
    "United States", "Uruguay", "Venezuela"
]

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

all_countries = sorted(list(set(countries_europe + countries_america + countries_asia)))

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

        # Function to make the API request (or simulate one)
        def make_request():
            try:
                # Uncomment the next line to make a real API call:
                # response_container["response"] = requests.post(API_URL, json=payload)
                # For simulation, we include the complete JSON response:
                response_container["response"] = {
                    "message": "Crew run completed successfully",
                    "result": {
                        "raw": "```markdown\n# Supplier Research Report\n\nThis report provides detailed information on potential suppliers, excluding Amazon, to aid the supplier acquisition team in making informed decisions. Each supplier section includes business model details, offerings, domain age, Trustpilot ratings, and comprehensive ZoomInfo data.\n\n## Table of Contents\n\n1.  [Elioplus](#elioplus)\n2.  [Getic](#getic)\n3.  [Volza](#volza)\n4.  [NetXL](#netxl)\n\n## 1. Elioplus\n\n### Overview\n\nElioplus is a provider of partner recruitment and management solutions for IT software companies. They offer services like partner recruitment automation, a partner database, and partner relationship management software.\n\n| Attribute          | Value                                                                                                     |\n| ------------------ | --------------------------------------------------------------------------------------------------------- |\n| **Supplier Name**  | Elioplus                                                                                                  |\n| **URL**            | [www.elioplus.com](www.elioplus.com)                                                                    |\n| **Domain Age**     | 11 years                                                                                                  |\n| **Trustpilot Rating**| No Trustpilot page found.                                                                               |\n| **Company ID**     | 359275211                                                                                                 |\n| **Founding Year**  | 2014                                                                                                      |\n| **Total Funding**  | $0                                                                                                        |\n| **Employees**      | <25                                                                                                       |\n| **Industry**       | Software                                                                                                    |\n| **Address**          | 108 W 13th St Ste 105, Wilmington, Delaware, 19801, United States                                         |\n\n### Detailed Information\n\n*   **Business Model**: Elioplus focuses on helping IT software companies expand their partner networks. Their services streamline the partner management process through innovative software tools.\n*   **Offerings**:\n    *   Partner Recruitment Automation\n    *   Partner Database\n    *   Partner Relationship Management Software\n*   **Domain Age**: 11 years (as of current data).\n*   **Trustpilot Rating**: No Trustpilot page found.\n*   **ZoomInfo Details**:\n    *   **companyId**: 359275211\n    *   **name**: Elioplus\n    *   **url**: [www.elioplus.com](www.elioplus.com)\n    *   **foundingYear**: 2014\n    *   **totalFundingAmount**: 0\n    *   **address**: 108 W 13th St Ste 105, Wilmington, Delaware, 19801, United States\n    *   **techUsed**:\n        *   reCAPTCHA (Google LLC)\n        *   Google AdSense (Google LLC)\n        *   Google Universal Analytics (Google LLC)\n        *   Cloudflare CDN (Cloudflare Inc)\n    *   **competitors**: TEEC, INNOVO, SaaSMAX, Nordic APIs, meldCX, Taking Care of Business, Inc.\n    *   **executives**:\n        *   CEO: Ilias Ndreu (Chief Executive Officer, Business Development)\n        *   CTO: Vagelis Varvitsiotis (Chief Technology Officer & Lead Developer)\n    *   **description**: Elioplus is a leading provider of partner recruitment and management solutions aimed at assisting IT software companies in expanding their partner networks.\n    *   **intents**:\n        *   Cloud Migration (Signal Score: 100)\n        *   Data Analytics (Signal Score: 74)\n\n### Analysis\n\nElioplus appears to be a relatively young company (founded in 2014) focusing on a niche market within the IT sector. The lack of Trustpilot reviews makes it difficult to assess customer satisfaction directly. However, their use of common web technologies suggests a standard online presence.\n\n## 2. Getic\n\n### Overview\n\nGetic is an IT company and network equipment distributor, selling a variety of wired and wireless devices and shipping to over 150 countries.\n\n| Attribute          | Value                                                                       |\n| ------------------ | --------------------------------------------------------------------------- |\n| **Supplier Name**  | Getic                                                                       |\n| **URL**            | [www.getic.com](www.getic.com)                                             |\n| **Domain Age**     | 22 years                                                                      |\n| **Trustpilot Rating**| Excellent (4.9/5)                                                           |\n| **Company ID**     | 1311087626                                                                  |\n| **Founding Year**  | 2007                                                                        |\n| **Total Funding**  | $0                                                                          |\n| **Employees**      | 67                                                                          |\n| **Industry**       | Telecommunications                                                            |\n| **Address**          | 6 Satiksmes Iela, Liepaja, Liepaja, LV-3401, Latvia                       |\n\n### Detailed Information\n\n*   **Business Model**: Getic operates as a distributor of network equipment, providing a wide range of wired and wireless devices to a global market.\n*   **Offerings**:\n    *   Routers\n    *   Antennas\n    *   Switches\n    *   Cables\n    *   Security and Monitoring Equipment\n*   **Domain Age**: 22 years (as of current data).\n*   **Trustpilot Rating**: Excellent (4.9/5).\n*   **ZoomInfo Details**:\n    *   **companyId**: 1311087626\n    *   **name**: Getic\n    *   **url**: [www.getic.com](www.getic.com)\n    *   **foundingYear**: 2007\n    *   **totalFundingAmount**: 0\n    *   **address**: 6 Satiksmes Iela, Liepaja, Liepaja, LV-3401, Latvia\n    *   **techUsed**:\n        *   YouTube (Google LLC)\n        *   Facebook Workplace (Facebook Inc)\n        *   Google Tag Manager (Google LLC)\n        *   Tawk.to (Tawk.to Inc)\n    *   **competitors**: None listed.\n    *   **executives**: None listed.\n    *   **description**: Getic is one of the fast-growing IT companies and is a network equipment distributor that sells a large variety of wired and wireless devices.\n     *   **intents**:\n        *   Managed Services (Signal Score: 100)\n        *   Digital Marketing (Signal Score: 86)\n\n### Analysis\n\nGetic has a strong Trustpilot rating, indicating high customer satisfaction. Founded in 2007, they have established themselves as a global distributor of network equipment. The lack of listed competitors in ZoomInfo may require further investigation.\n\n## 3. Volza\n\n### Overview\n\nVolza is a trade data startup providing export-import trade intelligence across numerous countries, offering insights into profitable products, markets, buyers, and suppliers.\n\n| Attribute          | Value                                                                                    |\n| ------------------ | ---------------------------------------------------------------------------------------- |\n| **Supplier Name**  | Volza                                                                                    |\n| **URL**            | [www.volza.com](www.volza.com)                                                          |\n| **Domain Age**     | 9 years                                                                                    |\n| **Trustpilot Rating**| Average (3.7/5)                                                                          |\n| **Company ID**     | 453622914                                                                                |\n| **Founding Year**  | 2017                                                                                     |\n| **Total Funding**  | $0                                                                                       |\n| **Employees**      | 248                                                                                      |\n| **Industry**       | Financial Software, Software, Banking, Finance                                           |\n| **Address**          | 19266 Coastal Hwy Unit 4, Rehoboth Beach, Delaware, 19971, United States                |\n\n### Detailed Information\n\n*   **Business Model**: Volza offers a self-service app providing export-import trade intelligence, helping businesses identify profitable trade opportunities.\n*   **Offerings**:\n    *   Export-Import Trade Intelligence\n    *   Data Analytics and Reporting\n    *   Identification of Profitable Products, Markets, Buyers, and Suppliers\n*   **Domain Age**: 9 years (as of current data).\n*   **Trustpilot Rating**: Average (3.7/5).\n*   **ZoomInfo Details**:\n    *   **companyId**: 453622914\n    *   **name**: Volza\n    *   **url**: [www.volza.com](www.volza.com)\n    *   **foundingYear**: 2017\n    *   **totalFundingAmount**: 0\n    *   **address**: 19266 Coastal Hwy Unit 4, Rehoboth Beach, Delaware, 19971, United States\n    *   **techUsed**:\n        *   goo.gl (Google LLC)\n        *   Facebook Web Custom Audiences (Facebook Inc)\n        *   Facebook Pixel (Facebook Inc)\n        *   Cloudflare Rocket Loader (Cloudflare Inc)\n    *   **competitors**: First Southern State Bank, Focus Bank, Harford Bank, Vantage Bank Texas, Farmers & Merchants Bank, Village Bank.\n    *   **acquisitions**: InfodriveIndia.com (Apr 10, 2021)\n    *   **description**: Volza is a revolutionary self-service app bringing together the export-import trade intelligence of 78+ countries.\n         *   **intents**:\n            *   Managed Services (Signal Score: 100)\n            *   Digital Marketing (Signal Score: 86)\n\n### Analysis\n\nVolza, founded in 2017, has quickly grown to 248 employees and has made one acquisition. Their Trustpilot rating is average, which may warrant further investigation into customer feedback. The news feed indicates active involvement in trade events and AI-driven solutions.\n\n## 4. NetXL\n\n### Overview\n\nNetXL is a distributor specializing in networking, VoIP, and smart automation solutions, providing a range of products including antennas, CCTV, smart home security systems, and VoIP accessories.\n\n| Attribute          | Value                                                                                                      |\n| ------------------ | ---------------------------------------------------------------------------------------------------------- |\n| **Supplier Name**  | NetXL                                                                                                     |\n| **URL**            | [www.netxl.com](www.netxl.com)                                                                           |\n| **Domain Age**     | 22 years                                                                                                     |\n| **Trustpilot Rating**| Excellent (4.8/5)                                                                                           |\n| **Company ID**     | 358015272                                                                                                  |\n| **Founding Year**  | 1999                                                                                                       |\n| **Total Funding**  | $0                                                                                                         |\n| **Employees**      | <25                                                                                                        |\n| **Industry**       | Consumer Electronics & Computers Retail, Retail                                                              |\n| **Address**          | Unit 4 Riverside Business Park Walnut Tree Close, Guildford, Surrey, GU1 4UG, United Kingdom               |\n\n### Detailed Information\n\n*   **Business Model**: NetXL operates as a distributor of technology solutions, focusing on networking, VoIP, and smart automation.\n*   **Offerings**:\n    *   Antennas\n    *   CCTV Systems\n    *   Smart Home Security Systems\n    *   VoIP Accessories\n*   **Domain Age**: 22 years (as of current data).\n*   **Trustpilot Rating**: Excellent (4.8/5).\n*   **ZoomInfo Details**:\n    *   **companyId**: 358015272\n    *   **name**: NetXL\n    *   **url**: [www.netxl.com](www.netxl.com)\n    *   **foundingYear**: 1999\n    *   **totalFundingAmount**: 0\n    *   **address**: Unit 4 Riverside Business Park Walnut Tree Close, Guildford, Surrey, GU1 4UG, United Kingdom\n    *   **techUsed**:\n        *   PHP\n        *   Cloudflare Website Optimization (Cloudflare Inc)\n        *   Cloudflare CDN (Cloudflare Inc)\n        *   Google Cloud Web Serving (Google LLC)\n    *   **competitors**: Best4systems, VoIP Store, Discountcomms, Electronic Frontier, PMC Telecom, Irison\n    *   **description**: NetXL Distribution Ltd. specializes in disruptive technology distribution, offering market-leading networking, VoIP, and smart automation solutions at competitive prices.\n          *   **intents**:\n            *   Digital Transformation (Signal Score: 100)\n            *   Candidate Sourcing (Signal Score: 86)\n\n### Analysis\n\nNetXL, established in 1999, has a strong Trustpilot rating, reflecting positive customer experiences. Despite being in operation for over two decades, the company has fewer than 25 employees, indicating a potentially lean business model. The scoop about their CEO leaving suggests potential organizational changes.\n```",
                         "pydantic": None,
                        "json_dict": None,
                        "tasks_output": [
                            {
                                "raw": "```markdown\n# Supplier Research Report\n\nThis report provides detailed information on potential suppliers, excluding Amazon, to aid the supplier acquisition team in making informed decisions. Each supplier section includes business model details, offerings, domain age, Trustpilot ratings, and comprehensive ZoomInfo data.\n\n## Table of Contents\n\n1.  [Elioplus](#elioplus)\n2.  [Getic](#getic)\n3.  [Volza](#volza)\n4.  [NetXL](#netxl)\n\n## 1. Elioplus\n\n### Overview\n\nElioplus is a provider of partner recruitment and management solutions for IT software companies. They offer services like partner recruitment automation, a partner database, and partner relationship management software.\n\n| Attribute          | Value                                                                                                     |\n| ------------------ | --------------------------------------------------------------------------------------------------------- |\n| **Supplier Name**  | Elioplus                                                                                                  |\n| **URL**            | [www.elioplus.com](www.elioplus.com)                                                                    |\n| **Domain Age**     | 11 years                                                                                                  |\n| **Trustpilot Rating**| No Trustpilot page found.                                                                               |\n| **Company ID**     | 359275211                                                                                                 |\n| **Founding Year**  | 2014                                                                                                      |\n| **Total Funding**  | $0                                                                                                        |\n| **Employees**      | <25                                                                                                       |\n| **Industry**       | Software                                                                                                  |\n| **Address**        | 108 W 13th St Ste 105, Wilmington, Delaware, 19801, United States                                           |\n\n### Detailed Information\n\n*   **Business Model**: Elioplus focuses on helping IT software companies expand their partner networks. Their services streamline the partner management process through innovative software tools.\n*   **Offerings**:\n    *   Partner Recruitment Automation\n    *   Partner Database\n    *   Partner Relationship Management Software\n*   **Domain Age**: 11 years (as of current data).\n*   **Trustpilot Rating**: No Trustpilot page found.\n*   **ZoomInfo Details**:\n    *   **companyId**: 359275211\n    *   **name**: Elioplus\n    *   **url**: [www.elioplus.com](www.elioplus.com)\n    *   **foundingYear**: 2014\n    *   **totalFundingAmount**: 0\n    *   **address**: 108 W 13th St Ste 105, Wilmington, Delaware, 19801, United States\n    *   **techUsed**:\n        *   reCAPTCHA (Google LLC)\n        *   Google AdSense (Google LLC)\n        *   Google Universal Analytics (Google LLC)\n        *   Cloudflare CDN (Cloudflare Inc)\n    *   **competitors**: TEEC, INNOVO, SaaSMAX, Nordic APIs, meldCX, Taking Care of Business, Inc.\n    *   **executives**:\n        *   CEO: Ilias Ndreu (Chief Executive Officer, Business Development)\n        *   CTO: Vagelis Varvitsiotis (Chief Technology Officer & Lead Developer)\n    *   **description**: Elioplus is a leading provider of partner recruitment and management solutions aimed at assisting IT software companies in expanding their partner networks.\n    *   **intents**:\n        *   Cloud Migration (Signal Score: 100)\n        *   Data Analytics (Signal Score: 74)\n\n### Analysis\n\nElioplus appears to be a relatively young company (founded in 2014) focusing on a niche market within the IT sector. The lack of Trustpilot reviews makes it difficult to assess customer satisfaction directly. However, their use of common web technologies suggests a standard online presence.\n\n## 2. Getic\n\n### Overview\n\nGetic is an IT company and network equipment distributor, selling a variety of wired and wireless devices and shipping to over 150 countries.\n\n| Attribute          | Value                                                                       |\n| ------------------ | --------------------------------------------------------------------------- |\n| **Supplier Name**  | Getic                                                                       |\n| **URL**            | [www.getic.com](www.getic.com)                                             |\n| **Domain Age**     | 22 years                                                                    |\n| **Trustpilot Rating**| Excellent (4.9/5)                                                          |\n| **Company ID**     | 1311087626                                                                 |\n| **Founding Year**  | 2007                                                                       |\n| **Total Funding**  | $0                                                                         |\n| **Employees**      | 67                                                                         |\n| **Industry**       | Telecommunications                                                         |\n| **Address**        | 6 Satiksmes Iela, Liepaja, Liepaja, LV-3401, Latvia                         |\n\n### Detailed Information\n\n*   **Business Model**: Getic operates as a distributor of network equipment, providing a wide range of wired and wireless devices to a global market.\n*   **Offerings**:\n    *   Routers\n    *   Antennas\n    *   Switches\n    *   Cables\n    *   Security and Monitoring Equipment\n*   **Domain Age**: 22 years (as of current data).\n*   **Trustpilot Rating**: Excellent (4.9/5).\n*   **ZoomInfo Details**:\n    *   **companyId**: 1311087626\n    *   **name**: Getic\n    *   **url**: [www.getic.com](www.getic.com)\n    *   **foundingYear**: 2007\n    *   **totalFundingAmount**: 0\n    *   **address**: 6 Satiksmes Iela, Liepaja, Liepaja, LV-3401, Latvia\n    *   **techUsed**:\n        *   YouTube (Google LLC)\n        *   Facebook Workplace (Facebook Inc)\n        *   Google Tag Manager (Google LLC)\n        *   Tawk.to (Tawk.to Inc)\n    *   **competitors**: None listed.\n    *   **executives**: None listed.\n    *   **description**: Getic is one of the fast-growing IT companies and is a network equipment distributor that sells a large variety of wired and wireless devices.\n    *   **intents**:\n        *   Managed Services (Signal Score: 100)\n        *   Digital Marketing (Signal Score: 86)\n\n### Analysis\n\nGetic has a strong Trustpilot rating, indicating high customer satisfaction. Founded in 2007, they have established themselves as a global distributor of network equipment. The lack of listed competitors in ZoomInfo may require further investigation.\n\n## 3. Volza\n\n### Overview\n\nVolza is a trade data startup providing export-import trade intelligence across numerous countries, offering insights into profitable products, markets, buyers, and suppliers.\n\n| Attribute          | Value                                                                                    |\n| ------------------ | ---------------------------------------------------------------------------------------- |\n| **Supplier Name**  | Volza                                                                                    |\n| **URL**            | [www.volza.com](www.volza.com)                                                          |\n| **Domain Age**     | 9 years                                                                                  |\n| **Trustpilot Rating**| Average (3.7/5)                                                                            |\n| **Company ID**     | 453622914                                                                                |\n| **Founding Year**  | 2017                                                                                     |\n| **Total Funding**  | $0                                                                                       |\n| **Employees**      | 248                                                                                      |\n| **Industry**       | Financial Software, Software, Banking, Finance                                           |\n| **Address**        | 19266 Coastal Hwy Unit 4, Rehoboth Beach, Delaware, 19971, United States                |\n\n### Detailed Information\n\n*   **Business Model**: Volza offers a self-service app providing export-import trade intelligence, helping businesses identify profitable trade opportunities.\n*   **Offerings**:\n    *   Export-Import Trade Intelligence\n    *   Data Analytics and Reporting\n    *   Identification of Profitable Products, Markets, Buyers, and Suppliers\n*   **Domain Age**: 9 years (as of current data).\n*   **Trustpilot Rating**: Average (3.7/5).\n*   **ZoomInfo Details**:\n    *   **companyId**: 453622914\n    *   **name**: Volza\n    *   **url**: [www.volza.com](www.volza.com)\n    *   **foundingYear**: 2017\n    *   **totalFundingAmount**: 0\n    *   **address**: 19266 Coastal Hwy Unit 4, Rehoboth Beach, Delaware, 19971, United States\n    *   **techUsed**:\n        *   goo.gl (Google LLC)\n        *   Facebook Web Custom Audiences (Facebook Inc)\n        *   Facebook Pixel (Facebook Inc)\n        *   Cloudflare Rocket Loader (Cloudflare Inc)\n    *   **competitors**: First Southern State Bank, Focus Bank, Harford Bank, Vantage Bank Texas, Farmers & Merchants Bank, Village Bank.\n    *   **acquisitions**: InfodriveIndia.com (Apr 10, 2021)\n    *   **description**: Volza is a revolutionary self-service app bringing together the export-import trade intelligence of 78+ countries.\n    *   **intents**:\n        *   Managed Services (Signal Score: 100)\n        *   Digital Marketing (Signal Score: 86)\n\n### Analysis\n\nVolza, founded in 2017, has quickly grown to 248 employees and has made one acquisition. Their Trustpilot rating is average, which may warrant further investigation into customer feedback. The news feed indicates active involvement in trade events and AI-driven solutions.\n\n## 4. NetXL\n\n### Overview\n\nNetXL is a distributor specializing in networking, VoIP, and smart automation solutions, providing a range of products including antennas, CCTV, smart home security systems, and VoIP accessories.\n\n| Attribute          | Value                                                                                                      |\n| ------------------ | ---------------------------------------------------------------------------------------------------------- |\n| **Supplier Name**  | NetXL                                                                                                     |\n| **URL**            | [www.netxl.com](www.netxl.com)                                                                           |\n| **Domain Age**     | 22 years                                                                                                   |\n| **Trustpilot Rating**| Excellent (4.8/5)                                                                                         |\n| **Company ID**     | 358015272                                                                                                  |\n| **Founding Year**  | 1999                                                                                                       |\n| **Total Funding**  | $0                                                                                                         |\n| **Employees**      | <25                                                                                                        |\n| **Industry**       | Consumer Electronics & Computers Retail, Retail                                                           |\n| **Address**        | Unit 4 Riverside Business Park Walnut Tree Close, Guildford, Surrey, GU1 4UG, United Kingdom                |\n\n### Detailed Information\n\n*   **Business Model**: NetXL operates as a distributor of technology solutions, focusing on networking, VoIP, and smart automation.\n*   **Offerings**:\n    *   Antennas\n    *   CCTV Systems\n    *   Smart Home Security Systems\n    *   VoIP Accessories\n*   **Domain Age**: 22 years (as of current data).\n*   **Trustpilot Rating**: Excellent (4.8/5).\n*   **ZoomInfo Details**:\n    *   **companyId**: 358015272\n    *   **name**: NetXL\n    *   **url**: [www.netxl.com](www.netxl.com)\n    *   **foundingYear**: 1999\n    *   **totalFundingAmount**: 0\n    *   **address**: Unit 4 Riverside Business Park Walnut Tree Close, Guildford, Surrey, GU1 4UG, United Kingdom\n    *   **techUsed**:\n        *   PHP\n        *   Cloudflare Website Optimization (Cloudflare Inc)\n        *   Cloudflare CDN (Cloudflare Inc)\n        *   Google Cloud Web Serving (Google LLC)\n    *   **competitors**: Best4systems, VoIP Store, Discountcomms, Electronic Frontier, PMC Telecom, Irison\n    *   **description**: NetXL Distribution Ltd. specializes in disruptive technology distribution, offering market-leading networking, VoIP, and smart automation solutions at competitive prices.\n    *   **intents**:\n        *   Digital Transformation (Signal Score: 100)\n        *   Candidate Sourcing (Signal Score: 86)\n\n### Analysis\n\nNetXL, established in 1999, has a strong Trustpilot rating, reflecting positive customer experiences. Despite being in operation for over two decades, the company has fewer than 25 employees, indicating a potentially lean business model. The scoop about their CEO leaving suggests potential organizational changes.\n```",
                            }
                        ],
                        "token_usage": {
                            "total_tokens": 43912,
                            "prompt_tokens": 38889,
                            "cached_prompt_tokens": 0,
                            "completion_tokens": 5023,
                            "successful_requests": 5
                        }
                    }
                }
            except Exception as e:
                response_container["response"] = None
                st.error(f"An error occurred while calling the API: {e}")

        # Start API call in a separate thread
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
            time.sleep(6)
            i += 1

        request_thread.join()

        # Simulate fetching the response (for a real API call, use response_container["response"].json())
        response = response_container["response"]

        if response:
            data = response  # Simulated response as a dict
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
            # st.markdown(f"<div class='final-answer-box'>{final_text}</div>", unsafe_allow_html=True)
            st.success("Supplier research is completed.")

            # Check for supplier table data and display it if available
            # supplier_data = data.get("suppliers", [])
            # if supplier_data:
            #     df = pd.DataFrame(supplier_data)
            #     st.dataframe(df, use_container_width=True)
            # else:
            #     st.warning("No supplier data found.")
        else:
            st.error("Failed to fetch results from the backend server.")