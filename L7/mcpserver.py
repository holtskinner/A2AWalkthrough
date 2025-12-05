import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Initialize the server
mcp = FastMCP("doctorserver")

# Load Data
doctors: list = json.loads(Path("../data/doctors.json").read_text())


@mcp.tool()
def list_doctors(state: str | None = None, city: str | None = None) -> list[dict]:
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
        return [{"error": "Please provide a state or a city."}]

    target_state = state.strip().lower() if state else None
    target_city = city.strip().lower() if city else None

    return [
        doc
        for doc in doctors
        if (not target_state or doc["address"]["state"].lower() == target_state)
        and (not target_city or doc["address"]["city"].lower() == target_city)
    ]


# Kick off server if file is run
if __name__ == "__main__":
    mcp.run(transport="stdio")
