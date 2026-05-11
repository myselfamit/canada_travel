"""
tools/destination.py
--------------------
TOOL 1: Destination Search
Combines Wikipedia API (free) + our Canadian data layer.

WHY httpx OVER requests:
    Same interface, but httpx supports async — meaning later when
    your MCP server handles multiple users, you can call Wikipedia
    and your data layer simultaneously instead of one-at-a-time.
    Start right, no refactor later.

HOW TO TEST:
    python tools/destination.py
"""

import httpx
import sys
import os

# Add parent directory to path so we can import our data modules
# WHY: Python needs to know where data/seasonal.py lives when we
# run this file directly. When run via the MCP server, it's fine.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.seasonal import get_seasonal_info, get_best_months
from data.canada_data import get_park_info, get_transit_info


# ─────────────────────────────────────────────────────────────
# WIKIPEDIA API HELPER
# ─────────────────────────────────────────────────────────────

WIKIPEDIA_BASE = "https://en.wikipedia.org/api/rest_v1"

def _fetch_wiki_summary(city: str) -> dict:
    """
    Fetches a Wikipedia page summary for a city.

    WHY WIKIPEDIA:
        Free, no API key, authoritative, covers all Canadian cities.
        The REST API (not the main API) returns clean JSON summaries
        without needing to parse wikitext.

    WHY .get() EVERYWHERE:
        Wikipedia's API response varies — some pages have images,
        some don't. Some have coordinates, some don't. Using .get()
        with a default means we never crash on missing fields.
    """
    try:
        # Replace spaces with underscores for Wikipedia URL format
        city_slug = city.strip().replace(" ", "_")
        url = f"{WIKIPEDIA_BASE}/page/summary/{city_slug}"

        # timeout=10: if Wikipedia is slow, we fail fast with a clear error
        # instead of hanging forever
        resp = httpx.get(url, timeout=10)

        # 404 means Wikipedia doesn't have this page
        if resp.status_code == 404:
            return {"found": False, "reason": "not_found"}

        # raise_for_status() raises an exception for 5xx server errors
        resp.raise_for_status()

        data = resp.json()

        return {
            "found":       True,
            "title":       data.get("title", city),
            "description": data.get("description", ""),
            "extract":     data.get("extract", "")[:800],  # first 800 chars only
            "image_url":   data.get("originalimage", {}).get("source"),
            "coordinates": data.get("coordinates", {}),
            "wikipedia_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }

    except httpx.TimeoutException:
        return {"found": False, "reason": "timeout", "error": "Wikipedia took too long to respond"}

    except httpx.HTTPStatusError as e:
        return {"found": False, "reason": "http_error", "error": str(e)}

    except Exception as e:
        return {"found": False, "reason": "unknown_error", "error": str(e)}


def _fetch_wiki_related(city: str) -> list[str]:
    """
    Fetches related Wikipedia pages — useful for finding attractions.

    WHY:
        Wikipedia's /related endpoint gives us pages linked from the
        city article — typically nearby attractions, neighbourhoods,
        or notable landmarks. Better than generic "top 10" lists.
    """
    try:
        city_slug = city.strip().replace(" ", "_")
        url = f"{WIKIPEDIA_BASE}/page/related/{city_slug}"
        resp = httpx.get(url, timeout=10)

        if resp.status_code != 200:
            return []

        data = resp.json()
        pages = data.get("pages", [])

        # Filter for pages that sound like attractions (not meta-pages)
        skip_keywords = ["wikipedia", "list of", "category:", "template:", "disambiguation"]
        related = []
        for page in pages[:10]:
            title = page.get("title", "")
            if not any(kw in title.lower() for kw in skip_keywords):
                related.append(title)

        return related[:6]  # Return top 6

    except Exception:
        return []


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────

def search_destination(city: str, month: int = None, province: str = None) -> dict:
    """
    Main destination search — combines Wikipedia + our Canadian data.

    WHY WE COMBINE SOURCES:
        Wikipedia gives general info (what is this place).
        Our data gives Canadian-specific insight (when to go, what it costs,
        what parks are nearby). Neither source alone is enough.

    Args:
        city:     City or destination name (e.g. "Banff", "Tofino")
        month:    Month number 1–12 for seasonal tips (optional)
        province: Province name for deeper seasonal data (optional)

    Returns:
        Structured dict with all info Claude needs to answer a travel question
    """

    # Step 1: Try Wikipedia for basic info
    # We search for "City, Canada" to avoid getting the wrong city
    # (e.g. "Victoria" could be Australia — add ", Canada" to be sure)
    wiki_city   = city
    wiki_result = _fetch_wiki_summary(f"{city}, Canada")

    if not wiki_result["found"]:
        # Fallback: try just the city name without ", Canada"
        wiki_result = _fetch_wiki_summary(city)

    # Step 2: Get related attractions from Wikipedia
    related_pages = _fetch_wiki_related(wiki_city)

    # Step 3: Get seasonal intelligence from our data layer
    # If province not provided, try to infer it from the city
    # (simple lookup — for MVP this is fine)
    province_guess = province or _infer_province(city)
    seasonal = None
    if province_guess and month:
        seasonal = get_seasonal_info(province_guess, month)

    # Step 4: Check if it's a national park
    park_info = get_park_info(city)

    # Step 5: Get transit info
    transit_info = get_transit_info(city)

    # Step 6: Assemble and return
    result = {
        "destination":   city.title(),
        "province":      province_guess.title() if province_guess else "Canada",

        # Wikipedia data
        "overview":      wiki_result.get("extract", f"{city} is a Canadian destination."),
        "description":   wiki_result.get("description", ""),
        "image_url":     wiki_result.get("image_url"),
        "wikipedia_url": wiki_result.get("wikipedia_url", ""),
        "related_attractions": related_pages,

        # Our Canadian data
        "seasonal_intel": seasonal,
        "national_park":  park_info if park_info["found"] else None,
        "city_transit":   transit_info if transit_info["found"] else None,

        # Data quality flags — be honest about what we know
        "data_sources": {
            "wikipedia":   wiki_result["found"],
            "seasonal":    seasonal is not None,
            "parks":       park_info["found"],
            "transit":     transit_info["found"],
        }
    }

    return result


def _infer_province(city: str) -> str:
    """
    Simple city → province lookup for common Canadian destinations.

    WHY HARDCODED:
        At MVP, this is fine. Later you'd call a geocoding API.
        For the top 20 Canadian destinations, hardcoded is faster
        and never fails due to API limits.
    """
    CITY_PROVINCE = {
        "toronto":        "ontario",
        "ottawa":         "ontario",
        "hamilton":       "ontario",
        "kingston":       "ontario",
        "niagara falls":  "ontario",
        "algonquin":      "ontario",
        "muskoka":        "ontario",
        "vancouver":      "british columbia",
        "victoria":       "british columbia",
        "whistler":       "british columbia",
        "tofino":         "british columbia",
        "kelowna":        "british columbia",
        "banff":          "alberta",
        "jasper":         "alberta",
        "calgary":        "alberta",
        "edmonton":       "alberta",
        "lake louise":    "alberta",
        "montreal":       "quebec",
        "quebec city":    "quebec",
        "tadoussac":      "quebec",
        "mont-tremblant": "quebec",
        "halifax":        "nova scotia",
        "cape breton":    "nova scotia",
        "peggy's cove":   "nova scotia",
        "winnipeg":       "manitoba",
        "churchill":      "manitoba",
        "saskatoon":      "saskatchewan",
        "regina":         "saskatchewan",
        "whitehorse":     "yukon",
        "dawson city":    "yukon",
        "yellowknife":    "northwest territories",
        "fredericton":    "new brunswick",
        "moncton":        "new brunswick",
        "charlottetown":  "prince edward island",
        "pei":            "prince edward island",
        "st. john's":     "newfoundland and labrador",
        "gros morne":     "newfoundland and labrador",
    }
    return CITY_PROVINCE.get(city.lower().strip(), "")


# ─────────────────────────────────────────────────────────────
# TEST
# Run: python tools/destination.py
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING: tools/destination.py")
    print("(requires internet connection — calls Wikipedia API)")
    print("=" * 60)

    print("\n[TEST 1] Banff in July")
    result = search_destination("Banff", month=7, province="alberta")
    print(f"  Destination:   {result['destination']}, {result['province']}")
    print(f"  Overview:      {result['overview'][:120]}...")
    print(f"  Park found:    {result['data_sources']['parks']}")
    if result["national_park"]:
        print(f"  Entry fee:     ${result['national_park']['park']['entry_fee_adult']}/day")
    if result["seasonal_intel"]:
        print(f"  July highlight: {result['seasonal_intel']['highlight']}")
        print(f"  July alert:     {result['seasonal_intel']['alert']}")
    print(f"  Related pages: {result['related_attractions'][:3]}")

    print("\n[TEST 2] Tofino in November (storm-watching)")
    result = search_destination("Tofino", month=11, province="british columbia")
    print(f"  Destination:   {result['destination']}, {result['province']}")
    if result["seasonal_intel"]:
        print(f"  Nov highlight: {result['seasonal_intel']['highlight']}")
        print(f"  Nov alert:     {result['seasonal_intel']['alert']}")

    print("\n[TEST 3] Toronto with transit info")
    result = search_destination("Toronto", month=6, province="ontario")
    print(f"  Destination: {result['destination']}")
    if result["city_transit"]:
        print(f"  Transit: {result['city_transit']['transit']['system']}")
        print(f"  Day pass: ${result['city_transit']['transit']['day_pass']}")

    print("\n[TEST 4] Fake city (graceful fallback)")
    result = search_destination("Fakevilleshire")
    print(f"  Destination: {result['destination']}")
    print(f"  Wikipedia found: {result['data_sources']['wikipedia']}")
    print(f"  Overview starts: {result['overview'][:60]}")

    print("\n✓ Destination search tests complete")