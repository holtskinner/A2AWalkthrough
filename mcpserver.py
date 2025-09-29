import json

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("doctorserver")


@mcp.tool()
def list_doctors(state: str) -> str:
    """This tool returns a list of doctors practicing in a specific state. The search is case-insensitive.

    Args:
        state: The two-letter state code (e.g., "CA" for California).

    Returns:
        A JSON string representing a list of doctors found in that state.
        Example: '[{"name": "Dr John James", "specialty": "Cardiology", ...}]'
    """
    url = "https://raw.githubusercontent.com/holtskinner/A2AWalkthrough/refs/heads/main/doctors.json"

    doctors = requests.get(url, timeout=10).json()
    state = state.upper()

    matches = [
        doctor for doctor in doctors.values() if doctor["address"]["state"] == state
    ]

    return json.dumps(matches)


# Kick off server if file is run
if __name__ == "__main__":
    mcp.run(transport="stdio")
