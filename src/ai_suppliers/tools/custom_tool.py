import asyncio
import json
import os
import time

import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

from exa_py import Exa
from scrapfly import ScrapflyClient, ScrapeConfig, ScrapeApiResponse
# Initialize the Exa tool with your API key





class CustomExaTool(BaseTool):
    name: str = "Custom Exa Tool"
    description: str = "Search the internet using the Exa tool."

    def _run(self, query: str) -> str:
        """
        Use the Exa tool to perform a search and print the extracted information.
        """
        # Initialize the Exa tool with your API key.
        # You can store the API key in an environment variable (e.g., EXA_API_KEY)
        API_KEY = os.getenv("EXA_API_KEY", "290e3940-9dc8-4f4c-ad48-2dadf906964c")
        exa = Exa(api_key=API_KEY)

        # Execute the search with default parameters: type "neural" and autoprompt enabled.
        result = exa.search(query, type="neural", use_autoprompt=True)

        # Extract the main data container
        data = result.get("data", {})



        # === Extract and print search results ===
        print("=== Search Results ===")
        results = data.get("results", [])
        for idx, res in enumerate(results, start=1):
            print(f"Result {idx}:")
            print("  Title         :", res.get("title"))
            print("  URL           :", res.get("url"))
            print("  ID            :", res.get("id"))
            print("  Score         :", res.get("score"))
            print("  Published Date:", res.get("publishedDate"))
            print("  Author        :", res.get("author"))
            print()
        return "Custom Exa Tool completed execution."

import os
import json
import requests
from urllib.parse import urlparse
from crewai.tools import BaseTool

import os
import json
import requests
from urllib.parse import urlparse

import json
import os
import requests
from urllib.parse import urlparse
scrapfly = ScrapflyClient(key="scp-live-8e13e5e37c4f4161b370861db39e447e")

# Base configuration for Scrapfly requests
BASE_CONFIG = {
    "asp": True,      # Helps to avoid Zoominfo blocking
    "country": "US"   # Sets proxy location to US
}

def parse_company(response: ScrapeApiResponse) -> dict:
    """
    Parse the company page to extract the JSON data.
    The JSON data is assumed to be in a script tag with an ID of either
    'app-root-state' or 'ng-state', and the JSON structure contains a key "pageData".
    """
    data_text = response.selector.css("script#app-root-state::text").get()
    if not data_text:
        data_text = response.selector.css("script#ng-state::text").get()
    if not data_text:
        raise ValueError("No company data script found.")
    data = json.loads(data_text)
    return data["pageData"]

async def scrape_company(url: str) -> dict:
    """
    Asynchronously scrape the given company URL using Scrapfly and return the raw JSON data.
    """
    response = await scrapfly.async_scrape(ScrapeConfig(url, **BASE_CONFIG))
    return parse_company(response)

class CombinedTool(BaseTool):
    name: str = "CombinedTool"
    description: str = (
        "Fetches domain age for a list of URLs using the Apivoid API, retrieves Trustpilot review data, "
        "and scrapes company details from ZoomInfo by leveraging SerperAPI and Scrapfly."
    )

    def _run(self, suppliers: list[dict] = None) -> str:
        """
        Retrieves domain age details, Trustpilot review data, and company data in one run.

        Parameters:
            suppliers (list): A list of dictionaries containing business information,
                              including the URL for domain age lookup.

        Returns:
            str: A JSON string containing domain age information, Trustpilot review data,
                 and scraped company data.
        """
        results = {}

        if suppliers:
            # Environment variables and headers setup
            # ea1ced053cb40f986f73516b749e6f488cf3034d(backup)

            apivoid_api_key = os.getenv("APIVOID_API_KEY", "ea1ced053cb40f986f73516b749e6f488cf3034d")
            serper_api_key = os.getenv("SERPER_API_KEY")
            headers = {
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            }

            domain_age_results = {}
            trustpilot_results = {}
            company_data_results = {}

            for supplier in suppliers:
                try:
                    url = supplier["url"]
                    parsed_url = urlparse(url)
                    domain_parts = parsed_url.netloc.split('.')

                    # Handle subdomains (e.g., www.example.com -> example.com)
                    if len(domain_parts) > 2:
                        main_domain = ".".join(domain_parts[-2:])
                    else:
                        main_domain = parsed_url.netloc

                    # Derive business name (can be adjusted as needed)
                    business_name = main_domain.split('.')[0]

                    # ------------------------------
                    # Part 1: Domain Age via Apivoid API
                    # ------------------------------
                    host = parsed_url.netloc.split(':')[0]  # Remove port if present
                    apivoid_url = f"https://endpoint.apivoid.com/domainage/v1/pay-as-you-go/?key={apivoid_api_key}&host={host}"
                    response = requests.get(apivoid_url)
                    time.sleep(1)
                    response.raise_for_status()
                    data = response.json()
                    domain_age = data.get('data', {}).get('domain_age_in_years', '')
                    domain_age_results[url] = domain_age

                    # ------------------------------
                    # Part 2: Trustpilot Reviews via SerperAPI
                    # ------------------------------
                    tp_search_payload = json.dumps({
                        "q": f"{business_name} site:trustpilot.com",
                        "num": 10,
                        "location": "United States"
                    })
                    tp_search_url = "https://google.serper.dev/search"
                    tp_response = requests.post(tp_search_url, headers=headers, data=tp_search_payload)
                    time.sleep(1)
                    tp_search_data = tp_response.json()

                    trustpilot_link = None
                    for result in tp_search_data.get("organic", []):
                        link = result.get("link", "")
                        if "trustpilot.com" in link and business_name.lower() in link.lower():
                            trustpilot_link = link
                            break

                    if trustpilot_link:
                        # Scrape the Trustpilot page
                        scrape_payload = json.dumps({"url": trustpilot_link})
                        scrape_url = "https://google.serper.dev/scrape"
                        scrape_response = requests.post(scrape_url, headers=headers, data=scrape_payload)
                        time.sleep(1)
                        scrape_data = scrape_response.json()

                        og_title = scrape_data.get("metadata", {}).get("og:title", "N/A")
                        aggregate_rating = None
                        for item in scrape_data.get("jsonld", {}).get("@graph", []):
                            if item.get("@type") == "AggregateRating":
                                aggregate_rating = item
                                break
                        review_count = aggregate_rating.get("reviewCount") if aggregate_rating else None

                        local_business_info = {}
                        for item in scrape_data.get("jsonld", {}).get("@graph", []):
                            if item.get("@type") == "LocalBusiness":
                                local_business_info = {
                                    "name": item.get("name"),
                                    "description": item.get("description"),
                                    "address": item.get("address", {})
                                }
                                break

                        trustpilot_results[business_name] = {
                            "og_title": og_title,
                            "aggregate_rating": aggregate_rating,
                            "review_count": review_count,
                            "local_business_info": local_business_info
                        }
                    else:
                        trustpilot_results[business_name] = {"error": f"No Trustpilot page found for {business_name}."}

                    # ------------------------------
                    # Part 3: Company Data via Scrapfly & ZoomInfo
                    # ------------------------------
                    # Use SerperAPI to search for a ZoomInfo URL using the business name
                    zi_search_payload = json.dumps({
                        "q": f"{business_name} site:zoominfo.com",
                        "num": 10,
                        "location": "United States"
                    })
                    zi_search_response = requests.post(tp_search_url, headers=headers, data=zi_search_payload)
                    zi_search_data = zi_search_response.json()

                    zoominfo_link = None
                    for result in zi_search_data.get("organic", []):
                        link = result.get("link", "")
                        if "zoominfo.com" in link:
                            zoominfo_link = link
                            break

                    if zoominfo_link:
                        try:
                            # Run the asynchronous Scrapfly scraping synchronously.
                            company_data = asyncio.run(scrape_company(zoominfo_link))
                        except Exception as scrape_error:
                            company_data = {"error": f"Scraping failed: {str(scrape_error)}"}
                    else:
                        company_data = {"error": f"No ZoomInfo page found for {business_name}."}

                    company_data_results[business_name] = company_data

                except Exception as e:
                    error_message = f"Error processing supplier {supplier.get('url', 'N/A')}: {str(e)}"
                    domain_age_results[url] = f"Error: {str(e)}"
                    trustpilot_results[business_name] = {"error": str(e)}
                    company_data_results[business_name] = {"error": str(e)}

            # Aggregate all results into a single JSON structure
            results = {
                "domain_age": domain_age_results,
                "trustpilot_reviews": trustpilot_results,
                "company_data": company_data_results
            }

        return json.dumps(results, indent=2)

class CustomSerperDevTool(BaseTool):
    name: str = "Custom Serper Dev Tool"
    description: str = "Search the internet for suppliers."

    def _run(self, query: str) -> str:
        """
        Search the internet for news.
        """

        url = "https://google.serper.dev/search"

        payload = json.dumps({
            "q": query,
            "num": 20,
            "location": "United States",
        })

        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # Parse the JSON response
        response_data = response.json()



        # === Extract Search Parameters ===
        search_params = response_data.get("searchParameters", {})
        print("Search Parameters:")
        for key, value in search_params.items():
            print(f"  {key}: {value}")
        print()

        # === Extract Organic Results ===
        organic_results = response_data.get("organic", [])
        print("Organic Results:")
        for result in organic_results:
            print("Position:", result.get("position"))
            print("Title:", result.get("title"))
            print("Link:", result.get("link"))
            print("Snippet:", result.get("snippet"))
            # Some entries may have a date field
            if "date" in result:
                print("Date:", result.get("date"))
            print()

        # === Extract People Also Ask ===
        people_also_ask = response_data.get("peopleAlsoAsk", [])
        print("People Also Ask:")
        for item in people_also_ask:
            print("Question:", item.get("question"))
            print("Title:", item.get("title"))
            print("Snippet:", item.get("snippet"))
            print("Link:", item.get("link"))
            print()

        # === Extract Related Searches ===
        related_searches = response_data.get("relatedSearches", [])
        print("Related Searches:")
        for item in related_searches:
            print("Query:", item.get("query"))
        print()
class DomainAgeTool(BaseTool):
    name: str = "DomainAgeTool"
    description: str = "Fetches the domain age for a list of URLs using the Apivoid Domain Age API."

    def _run(self, urls: list[str]) -> str:
        """
        Retrieves domain age details from the Apivoid API for each URL in the provided list.

        Parameters:
            urls (list): A list of domain URLs (e.g., ["https://gps4us.com", "https://example.com"]).

        Returns:
            dict: A mapping of URLs to their respective domain age information.
        """
        api_key = os.getenv("APIVOID_API_KEY", "f98d120f40bc56cfe63cde52c056bc935578bbd6")
        results = {}

        for url in urls:
            try:
                # Extract the domain from the URL
                parsed_url = urlparse(url)
                host = parsed_url.netloc or url
                host = host.split(':')[0]  # Remove port if present

                # Call the API
                api_url = f"https://endpoint.apivoid.com/domainage/v1/pay-as-you-go/?key={api_key}&host={host}"
                # response = requests.get(api_url)
                # response.raise_for_status()

                # Parse the response and extract domain age
                # json_data = response.json()
                domain_age=10
                # domain_age = json_data.get("data", {}).get("domain_age_in_years", "N/A")
                results[url] = domain_age
            except Exception as e:
                results[url] = f"Error: {str(e)}"

        return json.dumps(results,indent=2)

import os
import json
import requests
from crewai.tools import BaseTool  # Adjust the import as needed

import json
import os
import requests
from crewai.tools import BaseTool

class CustomTrustpilotTool(BaseTool):
    name: str = "CustomTrustpilotTool"
    description: str = "Search for multiple businesses' Trustpilot pages and extract review data."

    def _run(self, business_names: list[str]) -> str:
        """
        Search Trustpilot for multiple business names and extract review details.

        Parameters:
            business_names (list[str]): A list of business names to search for on Trustpilot.

        Returns:
            str: JSON string containing the extracted Trustpilot data or error messages.
        """
        results = {}

        headers = {
            "X-API-KEY": os.getenv("SERPER_API_KEY"),
            "Content-Type": "application/json"
        }

        for business_name in business_names:
            try:
                # Step 1: Search for the Trustpilot page
                search_url = "https://google.serper.dev/search"
                search_payload = json.dumps({
                    "q": f"{business_name} site:trustpilot.com",
                    "num": 10,
                    "location": "United States"
                })
                search_response = requests.post(search_url, headers=headers, data=search_payload)
                search_data = search_response.json()

                # Find the most relevant Trustpilot link
                trustpilot_link = None
                for result in search_data.get("organic", []):
                    link = result.get("link", "")
                    if "trustpilot.com" in link and business_name.lower() in link.lower():
                        trustpilot_link = link
                        break

                if not trustpilot_link:
                    results[business_name] = {"error": f"No Trustpilot page found for {business_name}."}
                    continue

                # Step 2: Scrape the Trustpilot page
                scrape_url = "https://google.serper.dev/scrape"
                scrape_payload = json.dumps({"url": trustpilot_link})
                scrape_response = requests.post(scrape_url, headers=headers, data=scrape_payload)
                scrape_data = scrape_response.json()

                # Extract metadata and review data
                og_title = scrape_data.get("metadata", {}).get("og:title", "N/A")
                aggregate_rating = None
                for item in scrape_data.get("jsonld", {}).get("@graph", []):
                    if item.get("@type") == "AggregateRating":
                        aggregate_rating = item
                        break

                results[business_name] = {
                    "og_title": og_title,
                    "aggregate_rating": aggregate_rating
                }

            except Exception as e:
                results[business_name] = {"error": str(e)}

        return json.dumps(results, indent=2)
