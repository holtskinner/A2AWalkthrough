import json

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("doctorserver")


@mcp.tool()
def list_doctors(state: str | None = None, city: str | None = None) -> str:
    """This tool returns a list of doctors practicing in a specific location. The search is case-insensitive.

    Args:
        state: The two-letter state code (e.g., "CA" for California).
        city: The name of the city or town (e.g., "Boston").

    Returns:
        A JSON string representing a list of doctors matching the criteria.
        If no criteria are provided, an error message is returned.
        Example: '[{"name": "Dr John James", "specialty": "Cardiology", ...}]'
    """
    # Input validation: ensure at least one search term is given.
    if not state and not city:
        return json.dumps(
            {"error": "Search failed. Please provide at least a state or a city."}
        )

    url = "https://raw.githubusercontent.com/holtskinner/A2AWalkthrough/refs/heads/main/data/doctors.json"

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    candidates = list(response.json().values())

    if state:
        state_normalized = state.strip().upper()
        candidates = [
            doc
            for doc in candidates
            if doc.get("address", {}).get("state", "").upper() == state_normalized
        ]

    if city:
        # Normalize city input for case-insensitive comparison.
        city_normalized = city.strip().lower()
        candidates = [
            doc
            for doc in candidates
            if doc.get("address", {}).get("city", "").lower() == city_normalized
        ]

    return json.dumps(candidates)


# Kick off server if file is run
if __name__ == "__main__":
    mcp.run(transport="stdio")
