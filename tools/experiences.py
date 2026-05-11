"""
tools/experiences.py
--------------------
TOOL 3: Local Experience Finder

Takes: city + interest type
Returns: curated local experiences with real ratings and addresses

WHY FOURSQUARE:
    Foursquare Places API free tier gives 1000 calls/day.
    It covers Canadian cities well, returns real ratings,
    and has category IDs for precise filtering.
    Sign up at foursquare.com/developer (2 minutes, free).

WHY NOMINATIM FOR GEOCODING:
    Foursquare needs lat/lng, not city names.
    Nominatim (OpenStreetMap) converts city names to coordinates
    for free — no key needed. We just need to set a User-Agent header
    (their terms of service requirement).

HOW TO TEST:
    python tools/experiences.py
"""

import httpx
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

FSQ_KEY  = os.getenv("FSQ_KEY", "")
FSQ_BASE = "https://api.foursquare.com/v3/places"

# Nominatim geocoding — free, no key needed
NOMINATIM_BASE = "https://nominatim.openstreetmap.org/search"


# ─────────────────────────────────────────────────────────────
# FOURSQUARE CATEGORY IDs
# Full list: developer.foursquare.com/reference/v3/categories
# We map friendly interest names → Foursquare category IDs
# ─────────────────────────────────────────────────────────────

INTEREST_TO_CATEGORIES = {
    "hiking":    ["16032", "16019", "16031"],  # Parks, Nature, Mountains
    "food":      ["13000", "13065", "13338"],  # Food, Restaurants, Farmers Market
    "culture":   ["10000", "10009", "10027"],  # Arts, Museums, Historic sites
    "family":    ["12000", "12058", "18000"],  # Family, Children's Museums, Attractions
    "nightlife": ["11000", "11013", "11025"],  # Nightlife, Bars, Live Music
    "wellness":  ["15000", "15014", "15052"],  # Fitness, Spas, Yoga
    "shopping":  ["17000", "17114", "17069"],  # Shopping, Markets, Boutiques
    "all":       ["13000", "10000", "16032"],  # Food + Arts + Outdoors
}

# Canadian experience extras — things Foursquare won't tell you but we know
CANADIAN_EXTRAS = {
    "banff": {
        "hiking": [
            {"name": "Tunnel Mountain Trail", "note": "Easy 45-min loop, great Banff townsite view", "free": True},
            {"name": "Johnston Canyon", "note": "Book the shuttle — parking fills by 8am in summer", "free": False},
            {"name": "Plain of Six Glaciers Tea House", "note": "2.5hr hike from Lake Louise, cash only at tea house", "free": False},
        ],
        "food": [
            {"name": "Banff Farmers Market", "note": "Thursdays July–September, Bear St", "free": True},
            {"name": "The Bison Restaurant", "note": "Best bison burger in Banff, book ahead for dinner", "free": False},
        ],
    },
    "tofino": {
        "hiking": [
            {"name": "South Beach Trail", "note": "30-min easy trail through old-growth forest to beach", "free": True},
            {"name": "Radar Hill Trail", "note": "10-min walk to best views of Clayoquot Sound", "free": True},
        ],
        "food": [
            {"name": "Tacofino (original truck)", "note": "The original location — lineup worth it", "free": False},
            {"name": "Tofino Brewing", "note": "Try the Kelp Stout — seriously Canadian", "free": False},
        ],
    },
    "montreal": {
        "food": [
            {"name": "Marché Jean-Talon", "note": "Best market in Canada — go hungry on Saturday morning", "free": True},
            {"name": "St-Viateur Bagel (original)", "note": "Open 24/7. Get a dozen sesame. This is the correct bagel.", "free": False},
            {"name": "Schwartz's Deli", "note": "Cash only. Lineup is part of the experience.", "free": False},
        ],
        "culture": [
            {"name": "Plateau-Mont-Royal walk", "note": "Walk St-Denis + Mont-Royal Ave — no guide needed, just wander", "free": True},
            {"name": "Musée des beaux-arts", "note": "Free on Saturday morning for under-30", "free": False},
        ],
    },
    "québec city": {
        "culture": [
            {"name": "Plains of Abraham walk", "note": "Free, historic, 1 km from Old City", "free": True},
            {"name": "Quartier Petit-Champlain", "note": "Most photographed street in Canada — go at golden hour", "free": True},
        ],
        "food": [
            {"name": "Le Lapin Sauté", "note": "Best patio in Old Quebec, try the rabbit", "free": False},
        ],
    },
}


# ─────────────────────────────────────────────────────────────
# GEOCODING
# ─────────────────────────────────────────────────────────────

# Hardcoded coordinates — fallback when Nominatim is unavailable
CITY_COORDS = {
    "toronto":        (43.6532, -79.3832),
    "vancouver":      (49.2827, -123.1207),
    "montreal":       (45.5017, -73.5673),
    "calgary":        (51.0447, -114.0719),
    "edmonton":       (53.5461, -113.4938),
    "ottawa":         (45.4215, -75.6972),
    "winnipeg":       (49.8951, -97.1384),
    "quebec city":    (46.8139, -71.2080),
    "halifax":        (44.6488, -63.5752),
    "victoria":       (48.4284, -123.3656),
    "banff":          (51.1784, -115.5708),
    "jasper":         (52.8734, -118.0811),
    "whistler":       (50.1163, -122.9574),
    "tofino":         (49.1531, -125.9072),
    "kelowna":        (49.8880, -119.4960),
    "whitehorse":     (60.7212, -135.0568),
    "yellowknife":    (62.4540, -114.3718),
    "charlottetown":  (46.2382, -63.1311),
    "fredericton":    (45.9636, -66.6431),
    "moncton":        (46.0878, -64.7782),
    "tadoussac":      (48.1439, -69.7189),
    "mont-tremblant": (46.1185, -74.5956),
    "niagara falls":  (43.0896, -79.0849),
    "cape breton":    (46.1548, -60.1942),
    "st. john's":     (47.5615, -52.7126),
    "dawson city":    (64.0603, -139.4325),
    "lake louise":    (51.4254, -116.1773),
    "churchill":      (58.7684, -94.1650),
}


def _geocode_city(city: str) -> dict:
    """
    Converts a city name to lat/lng using Nominatim (OpenStreetMap).

    WHY NOMINATIM:
        Free, no API key, excellent Canadian coverage.
        Nominatim requires a User-Agent identifying your app —
        it's in their terms and they'll block you without it.

    Returns dict with lat/lon or error info.
    """
    # Check hardcoded coords first — faster and works without internet
    city_key = city.lower().strip()
    if city_key in CITY_COORDS:
        lat, lon = CITY_COORDS[city_key]
        return {"found": True, "lat": lat, "lon": lon, "display": city, "province": ""}

    try:
        resp = httpx.get(
            NOMINATIM_BASE,
            params={
                "q":               f"{city}, Canada",
                "format":          "json",
                "limit":           1,
                "addressdetails":  1,
            },
            headers={
                # REQUIRED by Nominatim TOS — identify your application
                "User-Agent": "CanadaTravelMCP/1.0 (contact@yourdomain.ca)"
            },
            timeout=10
        )
        resp.raise_for_status()
        results = resp.json()

        if not results:
            return {"found": False, "error": f"Location not found: {city}"}

        r = results[0]
        return {
            "found":    True,
            "lat":      float(r["lat"]),
            "lon":      float(r["lon"]),
            "display":  r.get("display_name", city),
            "province": r.get("address", {}).get("state", ""),
        }

    except httpx.TimeoutException:
        return {"found": False, "error": "Geocoding timeout"}
    except Exception as e:
        return {"found": False, "error": str(e)}


# ─────────────────────────────────────────────────────────────
# FOURSQUARE SEARCH
# ─────────────────────────────────────────────────────────────

def _search_foursquare(lat: float, lon: float, categories: list[str], limit: int = 8) -> list[dict]:
    """
    Searches Foursquare Places API near lat/lon for given categories.

    WHY HEADERS NOT PARAMS FOR THE KEY:
        Foursquare uses Bearer token auth in the Authorization header —
        not a URL parameter like OpenWeatherMap does. This is more secure
        (keys in URL show up in server logs).

    WHY "fields" PARAMETER:
        Foursquare by default returns minimal data. We request exactly
        what we need to avoid large responses and stay in free tier limits.
    """
    if not FSQ_KEY:
        return _mock_foursquare_results(lat, lon)

    try:
        resp = httpx.get(
            f"{FSQ_BASE}/search",
            headers={
                "Authorization": FSQ_KEY,
                "Accept":        "application/json",
            },
            params={
                "ll":          f"{lat},{lon}",
                "categories":  ",".join(categories),
                "limit":       limit,
                "radius":      10000,    # 10km radius
                "fields":      "name,location,rating,description,tel,website,hours",
                "sort":        "RATING",  # best-rated first
            },
            timeout=10
        )
        resp.raise_for_status()
        return resp.json().get("results", [])

    except httpx.TimeoutException:
        return []
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print("  [WARNING] FSQ_KEY invalid — check your .env file")
        return []
    except Exception:
        return []


def _mock_foursquare_results(lat: float, lon: float) -> list[dict]:
    """
    Mock Foursquare results for testing without an API key.
    Returns realistic Canadian experience data.
    """
    return [
        {
            "name":     "Local Farmers Market",
            "location": {"formatted_address": "Downtown, Canada"},
            "rating":   9.1,
            "description": "Popular weekend market with local produce and artisans",
            "tel":      "",
            "website":  "",
        },
        {
            "name":     "Riverside Trail",
            "location": {"formatted_address": "Riverfront, Canada"},
            "rating":   8.8,
            "description": "Well-maintained trail along the river, popular with cyclists",
            "tel":      "",
            "website":  "",
        },
        {
            "name":     "Heritage Museum",
            "location": {"formatted_address": "Main St, Canada"},
            "rating":   8.5,
            "description": "Local history and indigenous culture exhibits",
            "tel":      "",
            "website":  "",
        },
    ]


def _format_fsq_result(place: dict) -> dict:
    """
    Cleans a raw Foursquare result into our standard format.

    WHY SEPARATE FORMATTER:
        If Foursquare changes their API response format, we only
        update this one function — nothing else breaks.
        Also makes testing easy: pass in mock data, verify output.
    """
    location = place.get("location", {})
    return {
        "name":        place.get("name", "Unknown"),
        "address":     location.get("formatted_address", ""),
        "rating":      place.get("rating"),          # None if not rated
        "description": place.get("description", ""),
        "phone":       place.get("tel", ""),
        "website":     place.get("website", ""),
        "hours":       place.get("hours", {}).get("display", ""),
    }


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────

def find_experiences(city: str, interest: str = "all", limit: int = 6) -> dict:
    """
    Finds local experiences for a city and interest type.

    Combines:
    1. Foursquare Places API (real businesses with ratings)
    2. Our Canadian extras (curated insider knowledge)

    Args:
        city:     City name (e.g. "Montreal", "Banff")
        interest: "hiking", "food", "culture", "family", "nightlife", "all"
        limit:    Max results from Foursquare (default 6)

    Returns:
        dict with Foursquare results + our Canadian extras
    """
    # Step 1: Geocode the city
    geo = _geocode_city(city)
    if not geo["found"]:
        return {
            "error":   True,
            "city":    city,
            "message": geo["error"],
            "tip":     "Try adding the province: 'Victoria, BC' instead of just 'Victoria'"
        }

    # Step 2: Get Foursquare category IDs for this interest
    interest_key = interest.lower().strip()
    if interest_key not in INTEREST_TO_CATEGORIES:
        interest_key = "all"
    categories = INTEREST_TO_CATEGORIES[interest_key]

    # Step 3: Search Foursquare
    raw_results = _search_foursquare(geo["lat"], geo["lon"], categories, limit)
    fsq_results = [_format_fsq_result(r) for r in raw_results]

    # Step 4: Add our curated Canadian extras
    city_key = city.lower().strip()
    our_extras = CANADIAN_EXTRAS.get(city_key, {}).get(interest_key, [])

    # Step 5: Assemble result
    return {
        "city":        city.title(),
        "province":    geo.get("province", ""),
        "interest":    interest_key,
        "coordinates": {"lat": geo["lat"], "lon": geo["lon"]},

        # Main Foursquare results
        "experiences": fsq_results,

        # Our Canadian insider knowledge (the differentiator)
        "insider_picks": our_extras,

        # Data quality info
        "data_note": "Using mock Foursquare data — add FSQ_KEY to .env for real results" if not FSQ_KEY else "Live Foursquare data",
        "result_count": len(fsq_results),
        "insider_count": len(our_extras),
    }


# ─────────────────────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING: tools/experiences.py")
    if not FSQ_KEY:
        print("(No FSQ_KEY found — using mock Foursquare data)")
    print("=" * 60)

    print("\n[TEST 1] Food experiences in Montreal")
    result = find_experiences("Montreal", interest="food")
    print(f"  City: {result['city']}, {result.get('province', '')}")
    print(f"  Foursquare results: {result['result_count']}")
    for exp in result["experiences"][:2]:
        print(f"    - {exp['name']} | {exp['address']}")
    print(f"  Insider picks:")
    for pick in result["insider_picks"]:
        print(f"    - {pick['name']}: {pick['note']}")

    print("\n[TEST 2] Hiking in Banff")
    result = find_experiences("Banff", interest="hiking")
    print(f"  City: {result['city']}")
    print(f"  Insider hiking picks:")
    for pick in result["insider_picks"]:
        print(f"    - {pick['name']}: {pick['note']}")

    print("\n[TEST 3] Geocoding check — Tofino")
    geo = _geocode_city("Tofino")
    print(f"  Found: {geo['found']}")
    if geo["found"]:
        print(f"  Lat/Lon: {geo['lat']}, {geo['lon']}")
        print(f"  Province: {geo['province']}")

    print("\n[TEST 4] Formatter in isolation (no API)")
    mock_fsq_place = {
        "name": "Test Cafe",
        "location": {"formatted_address": "123 Main St, Ottawa, ON"},
        "rating": 8.9,
        "description": "Great coffee",
        "tel": "613-555-0100",
    }
    formatted = _format_fsq_result(mock_fsq_place)
    print(f"  Name:    {formatted['name']}")
    print(f"  Address: {formatted['address']}")
    print(f"  Rating:  {formatted['rating']}")

    print("\n✓ Experiences tests complete")