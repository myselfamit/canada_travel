"""
server.py
---------
WEEK 2 — The MCP server. Wraps all 4 tools so Claude can call them.

WHY FastMCP:
    FastMCP is the official Anthropic-recommended way to build MCP servers.
    The @mcp.tool() decorator does two things:
    1. Registers your function as a callable tool
    2. Uses your docstring as the tool description Claude reads to decide
       which tool to call

CRITICAL: Write good docstrings.
    Claude reads the docstring to decide when to call your tool.
    "Search for destinations" is bad.
    "Search for Canadian travel destinations — returns attractions, seasonal
    alerts, park info, and transit details. Use when user asks about a
    specific city or place in Canada." is good.

HOW TO RUN:
    pip install mcp httpx python-dotenv
    python server.py

HOW TO ADD TO CLAUDE DESKTOP:
    Edit: ~/.claude/claude_desktop_config.json
    Add:
    {
      "mcpServers": {
        "canada-travel": {
          "command": "python",
          "args": ["/full/path/to/canada-travel/server.py"]
        }
      }
    }
"""


import sys
import os

# Ensure Python can find our tools and data modules
# WHY: When Claude Desktop runs your server, the working directory
# might not be your project folder. This makes imports reliable
# regardless of how the server is started.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

# Import our 4 tools
from tools.destination        import search_destination
from tools.weather_itinerary  import build_itinerary
from tools.experiences        import find_experiences
from tools.budget             import estimate_budget

# ─────────────────────────────────────────────────────────────
# CREATE THE MCP SERVER
# ─────────────────────────────────────────────────────────────
# The name here shows up in Claude Desktop's tool list
mcp = FastMCP("Canada Travel Assistant")


# ─────────────────────────────────────────────────────────────
# TOOL 1: Destination Search
# ─────────────────────────────────────────────────────────────

@mcp.tool()
def destination_search(city: str, month: int = None, province: str = None) -> dict:
    """
    Search for Canadian travel destinations.

    Use this when the user asks about:
    - A specific Canadian city, town, or region (e.g. "Tell me about Banff",
      "What's Tofino like?", "I'm thinking of going to Quebec City")
    - What to expect at a Canadian destination
    - Whether a destination is good to visit
    - What attractions exist in a Canadian city

    Returns: overview, seasonal alerts, nearby national park info,
             city transit details, and related attractions.

    Args:
        city:     City or destination name (e.g. "Banff", "Tofino", "Montreal")
        month:    Month number 1-12 if user mentions a travel month (optional)
        province: Province name if known (optional, improves seasonal accuracy)
    """
    return search_destination(city=city, month=month, province=province)


# ─────────────────────────────────────────────────────────────
# TOOL 2: Weather-Aware Itinerary
# ─────────────────────────────────────────────────────────────

@mcp.tool()
def weather_itinerary(
    city:         str,
    days:         int,
    budget_style: str = "mid",
    interest:     str = "all",
    province:     str = None,
) -> dict:
    """
    Build a weather-aware day-by-day travel itinerary for a Canadian destination.

    Use this when the user wants:
    - A day-by-day plan for their trip
    - Activities suggested based on weather
    - An itinerary for a specific number of days

    The itinerary adapts activities to the forecasted weather — rainy days
    get indoor suggestions, warm sunny days get outdoor activities.

    Args:
        city:         Destination city (e.g. "Banff", "Vancouver", "Montreal")
        days:         Number of days for the trip (1-5 for live weather; 6+ uses seasonal data)
        budget_style: Travel style — "budget", "mid", or "luxury" (default: "mid")
        interest:     Activity focus — "hiking", "food", "culture", "family", or "all" (default: "all")
        province:     Province name for better seasonal data (optional)
    """
    return build_itinerary(
        city=city,
        days=days,
        budget_style=budget_style,
        interest=interest,
        province=province,
    )


# ─────────────────────────────────────────────────────────────
# TOOL 3: Local Experience Finder
# ─────────────────────────────────────────────────────────────

@mcp.tool()
def local_experiences(city: str, interest: str = "all", limit: int = 6) -> dict:
    """
    Find local experiences, activities, and places in a Canadian city.

    Use this when the user asks:
    - "What should I do in [city]?"
    - "Where should I eat in [city]?"
    - "What are the best hikes near [city]?"
    - "Family-friendly activities in [city]?"
    - "What's good for culture in [city]?"

    Combines real Foursquare Places data with curated Canadian insider picks
    that guidebooks and AI models typically miss.

    Args:
        city:     City name (e.g. "Montreal", "Banff", "Victoria")
        interest: Type of experience — "hiking", "food", "culture", "family",
                  "nightlife", "wellness", or "all" (default: "all")
        limit:    Max number of Foursquare results (default: 6)
    """
    return find_experiences(city=city, interest=interest, limit=limit)


# ─────────────────────────────────────────────────────────────
# TOOL 4: Budget Estimator
# ─────────────────────────────────────────────────────────────

@mcp.tool()
def budget_estimate(
    city:           str,
    days:           int,
    style:          str,
    month:          int  = None,
    include_flight: bool = True,
    flight_type:    str  = "medium",
) -> dict:
    """
    Estimate the cost of a Canadian trip with a detailed CAD breakdown.

    Use this when the user asks:
    - "How much will it cost to visit [city] for [n] days?"
    - "What's the budget for a trip to [city]?"
    - "Is [city] expensive?"
    - "How much should I budget for [city]?"

    Returns: daily costs (accommodation, food, transport, activities),
             total trip cost, Parks Canada pass advice, seasonal price
             adjustments, and money-saving tips.

    Args:
        city:           Destination city
        days:           Trip length in days
        style:          Travel style — "budget", "mid", or "luxury"
        month:          Month of travel 1-12 (enables seasonal price adjustments)
        include_flight: Whether to include a domestic flight estimate (default: True)
        flight_type:    "short" (<2hr flight), "medium" (2-4hr), "long" (4hr+),
                        or "budget_airline" (Flair/Swoop)
    """
    return estimate_budget(
        city=city,
        days=days,
        style=style,
        month=month,
        include_flight=include_flight,
        flight_type=flight_type,
    )


# ─────────────────────────────────────────────────────────────
# RUN THE SERVER
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Starting Canada Travel MCP Server...")
    print("Tools registered:")
    print("  1. destination_search  — city/region info + seasonal alerts")
    print("  2. weather_itinerary   — day-by-day plan with weather")
    print("  3. local_experiences   — curated activities by interest")
    print("  4. budget_estimate     — CAD cost breakdown with seasonal pricing")
    print("")
    print("Waiting for Claude to connect...")
    mcp.run()