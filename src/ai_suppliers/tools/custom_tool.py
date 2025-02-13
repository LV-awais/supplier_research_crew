import json
import os
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from urllib.parse import urlparse
from dotenv import load_dotenv
load_dotenv()

from exa_py import Exa

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

class CombinedTool(BaseTool):
    name: str = "CombinedTool"
    description: str = "Fetches domain age for a list of URLs using the Apivoid API and retrieves Trustpilot review data for business names derived from the URLs."

    def _run(self, suppliers: list[dict] = None) -> str:
        """
        Retrieves domain age details and Trustpilot review data in one run.

        Parameters:
            suppliers (list): A list of dictionaries containing business information, including the URL for domain age lookup.

        Returns:
            str: A JSON string containing domain age information and Trustpilot review data.
        """
        results = {}

        if suppliers:
            api_key = os.getenv("APIVOID_API_KEY", "ea1ced053cb40f986f73516b749e6f488cf3034d")
            domain_age_results = {}
            trustpilot_results = {}
            headers = {
                "X-API-KEY": os.getenv("SERPER_API_KEY"),
                "Content-Type": "application/json"
            }

            # Part 1: Fetch domain ages
            for supplier in suppliers:
                try:
                    url = supplier["url"]
                    parsed_url = urlparse(url)
                    domain_parts = parsed_url.netloc.split('.')

                    # Handling subdomains (e.g., www.example.com -> example.com)
                    if len(domain_parts) > 2:
                        main_domain = ".".join(domain_parts[-2:])
                    else:
                        main_domain = parsed_url.netloc

                    # Use extracted domain name for Trustpilot searches
                    business_name = main_domain.split('.')[0]
                    # business_name = supplier['business_name']
                    # Extract domain from URL
                    parsed_url = urlparse(url)
                    host = parsed_url.netloc or url
                    host = host.split(':')[0]  # Remove port if present

                    # Call the Apivoid API to get domain age
                    api_url = f"https://endpoint.apivoid.com/domainage/v1/pay-as-you-go/?key={api_key}&host={host}"
                    response = requests.get(api_url)
                    response.raise_for_status()
                    data = response.json()
                    # Simulate domain age response (replace this when enabling API call)
                    domain_age = data.get('data',{}).get('domain_age_in_years','')  # Placeholder for domain age

                    domain_age_results[url] = domain_age

                    # Part 2: Fetch Trustpilot reviews for extracted business name
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
                        trustpilot_results[business_name] = {"error": f"No Trustpilot page found for {business_name}."}
                        continue

                    # Scrape the Trustpilot page for reviews
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

                except Exception as e:
                    domain_age_results[url] = f"Error: {str(e)}"
                    trustpilot_results[business_name] = {"error": str(e)}

            # Combine the results
            results['domain_age'] = domain_age_results
            results['trustpilot_reviews'] = trustpilot_results

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
