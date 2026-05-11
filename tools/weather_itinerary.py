"""
tools/weather_itinerary.py
--------------------------
TOOL 2: Weather-Aware Itinerary Builder

Takes: destination + arrival date + number of days + budget style
Returns: day-by-day itinerary shaped around real weather forecast

WHY OPENWEATHERMAP:
    Free tier gives 5-day forecast in 3-hour intervals — enough for
    trip planning. 1000 API calls/day free. Requires signup at
    openweathermap.org (takes 2 minutes).

HOW TO GET YOUR KEY:
    1. Go to openweathermap.org/api
    2. Sign up free
    3. Go to "API keys" tab
    4. Copy your key into .env file as: OWM_KEY=your_key_here

HOW TO TEST:
    python tools/weather_itinerary.py
"""

import httpx
import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.seasonal import get_seasonal_info, _month_name
from data.canada_data import get_accommodation_cost, FOOD_COSTS_PER_DAY

# Load API key from environment variable
# WHY ENV VARIABLE: Never hardcode secrets in source code.
# If you push to GitHub with a hardcoded key, bots find it in minutes.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional — can set env vars manually too

OWM_KEY = os.getenv("OWM_KEY", "")
OWM_BASE = "https://api.openweathermap.org/data/2.5"


# ─────────────────────────────────────────────────────────────
# ACTIVITY DATABASE
# Maps weather conditions to Canadian activities by category.
# This is where your Canadian expertise lives.
# ─────────────────────────────────────────────────────────────

ACTIVITIES = {
    # Format: condition → [list of activities]
    # Conditions: "rain", "cold" (<5°C), "cool" (5-14°C),
    #             "mild" (15-19°C), "warm" (20-27°C), "hot" (>27°C)

    "rain": {
        "all":     ["indoor public market", "museum visit", "spa day", "brewery or winery tour", "cooking class"],
        "food":    ["food hall visit", "local restaurant crawl", "cooking class", "brewery tour"],
        "culture": ["art gallery", "history museum", "live theatre matinee", "symphony or jazz club"],
        "family":  ["science centre", "indoor water park", "children's museum", "bowling"],
        "hiking":  ["indoor climbing gym", "hot springs", "cave tour"],
    },
    "cold": {  # below 5°C
        "all":     ["hot spring soak", "indoor market", "cozy café hopping", "museum"],
        "food":    ["warm restaurant crawl", "fondue dinner", "sugar shack (if winter)"],
        "culture": ["live music venue", "art gallery", "theatre"],
        "family":  ["indoor play centre", "skating rink", "science centre"],
        "hiking":  ["snowshoe trail", "winter hiking (dress properly)", "cross-country skiing"],
    },
    "cool": {  # 5–14°C
        "all":     ["city walking tour", "cycling", "kayaking", "farmers market"],
        "food":    ["food tour on foot", "outdoor market", "waterfront restaurant"],
        "culture": ["historic neighbourhood walk", "public art tour", "cemetery walk (history)"],
        "family":  ["park visit", "bike ride", "petting zoo"],
        "hiking":  ["trail hike", "waterfall hike", "birdwatching"],
    },
    "mild": {  # 15–19°C
        "all":     ["hiking", "cycling", "kayaking or canoeing", "whale watching tour"],
        "food":    ["outdoor food market", "patio dining", "farm visit"],
        "culture": ["open-air festival", "walking tour", "botanical garden"],
        "family":  ["beach walk", "bike rental", "outdoor pool", "playground"],
        "hiking":  ["full-day mountain hike", "waterfall trail", "ridge walk"],
    },
    "warm": {  # 20–27°C
        "all":     ["lake swimming", "beach day", "kayaking", "cycling", "whale watching"],
        "food":    ["BBQ patio", "ice cream tour", "outdoor market"],
        "culture": ["outdoor concert", "open-air theatre", "night market"],
        "family":  ["beach day", "water park", "mini golf", "boat tour"],
        "hiking":  ["alpine hike", "summit trail", "mountain biking"],
    },
    "hot": {  # above 27°C
        "all":     ["lake or ocean swimming", "early morning hike", "evening kayak", "shaded market"],
        "food":    ["food truck festival (evening)", "waterfront restaurant", "ice cream"],
        "culture": ["evening outdoor event", "air-conditioned gallery in midday"],
        "family":  ["water park", "splash pad", "beach all day"],
        "hiking":  ["early morning hike only", "waterfall swim", "shaded forest trail"],
    },
}


def _get_weather_condition(temp_c: float, has_rain: bool) -> str:
    """Maps temperature + rain into one of our condition keys."""
    if has_rain:
        return "rain"
    if temp_c < 5:
        return "cold"
    if temp_c < 15:
        return "cool"
    if temp_c < 20:
        return "mild"
    if temp_c < 28:
        return "warm"
    return "hot"


def _pick_activities(condition: str, interest: str, budget_style: str) -> list[str]:
    """
    Returns activities for a given condition + interest.

    WHY SEPARATE FUNCTION:
        Testable in isolation. Pass in (condition="rain", interest="hiking",
        budget_style="budget") and verify the output without any API calls.
    """
    condition_activities = ACTIVITIES.get(condition, ACTIVITIES["mild"])
    interest_key = interest.lower() if interest.lower() in condition_activities else "all"
    activities = condition_activities.get(interest_key, condition_activities["all"])

    # Budget filter: remove expensive activities for budget travelers
    if budget_style == "budget":
        expensive_keywords = ["spa", "whale watching", "helicopter", "luxury"]
        activities = [a for a in activities if not any(kw in a.lower() for kw in expensive_keywords)]

    return activities[:3]  # Return top 3 suggestions


# ─────────────────────────────────────────────────────────────
# WEATHER FETCH
# ─────────────────────────────────────────────────────────────

def _fetch_weather_forecast(city: str) -> dict:
    """
    Fetches 5-day weather forecast from OpenWeatherMap.

    WHY "q": city + ",CA":
        The "CA" country code ensures we get Canadian cities, not
        cities in California or other countries with the same name.
        Without it, "Victoria" returns Victoria, Australia.

    WHY "units": "metric":
        Canada uses Celsius. Always request metric for Canadian apps.
    """
    if not OWM_KEY:
        # Return mock data if no API key — useful for testing the
        # rest of the pipeline without setting up OWM yet
        return _mock_weather_forecast(city)

    try:
        resp = httpx.get(
            f"{OWM_BASE}/forecast",
            params={
                "q":      f"{city},CA",
                "appid":  OWM_KEY,
                "units":  "metric",
                "cnt":    40,       # 40 intervals = ~5 days of 3-hour blocks
            },
            timeout=10
        )
        resp.raise_for_status()
        return {"success": True, "data": resp.json()}

    except httpx.TimeoutException:
        return {"success": False, "error": "Weather API timeout"}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return {"success": False, "error": "Invalid API key — check your OWM_KEY in .env"}
        if e.response.status_code == 404:
            return {"success": False, "error": f"City '{city}' not found in OpenWeatherMap"}
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _mock_weather_forecast(city: str) -> dict:
    """
    Returns realistic mock weather so you can build + test the
    itinerary logic without an OWM API key.

    WHY MOCK DATA:
        Lets you develop and test the full pipeline (including the MCP
        server) before signing up for external APIs. Replace with real
        calls once the rest works.
    """
    base_date = datetime.now()
    mock_list = []
    for i in range(40):
        dt = base_date + timedelta(hours=i * 3)
        mock_list.append({
            "dt_txt": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "main": {
                "temp":     15 + (i % 5),   # 15–19°C range
                "humidity": 60,
                "feels_like": 14,
            },
            "weather": [{"description": "partly cloudy", "main": "Clouds"}],
            "rain": {},
        })

    return {
        "success": True,
        "data": {
            "city": {"name": city, "country": "CA"},
            "list": mock_list,
        },
        "mock": True,  # Flag so we know this isn't real data
    }


def _group_forecast_by_day(forecast_list: list) -> dict:
    """
    OpenWeatherMap returns 3-hour interval data.
    We group it into days for cleaner itinerary building.

    Example input:
        [{"dt_txt": "2024-07-15 00:00:00", "main": {"temp": 18}, ...},
         {"dt_txt": "2024-07-15 03:00:00", "main": {"temp": 16}, ...},
         ...]

    Example output:
        {"2024-07-15": [{"temp": 18, "rain": 0, ...}, {...}, ...]}

    WHY defaultdict:
        defaultdict(list) automatically creates an empty list when we
        first access a key — no need to check "if date not in dict".
    """
    grouped = defaultdict(list)

    for item in forecast_list:
        # "2024-07-15 12:00:00" → split on space → take date part
        date = item["dt_txt"].split(" ")[0]
        grouped[date].append({
            "temp":        item["main"]["temp"],
            "feels_like":  item["main"]["feels_like"],
            "humidity":    item["main"]["humidity"],
            "description": item["weather"][0]["description"],
            "rain_mm":     item.get("rain", {}).get("3h", 0),
        })

    return dict(grouped)


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────

def build_itinerary(
    city:         str,
    days:         int,
    budget_style: str  = "mid",
    interest:     str  = "all",
    province:     str  = None,
) -> dict:
    """
    Builds a weather-aware day-by-day itinerary.

    Args:
        city:         Destination city (e.g. "Banff")
        days:         Number of days (1–5 for weather data; we handle 6+ with seasonal fallback)
        budget_style: "budget", "mid", or "luxury"
        interest:     "all", "hiking", "food", "culture", or "family"
        province:     Province for seasonal intelligence (optional, inferred if blank)

    Returns:
        dict with itinerary, weather summary, cost estimate, seasonal alerts
    """
    print(f"🔧 MCP CALLED: build_itinerary({city}, {days} days, {budget_style})")  # ADD THIS

    # Step 1: Get weather forecast
    weather_result = _fetch_weather_forecast(city)

    if not weather_result["success"]:
        return {
            "error":   True,
            "message": weather_result["error"],
            "tip":     "Check your OWM_KEY in .env file, or try a different city name"
        }

    # Step 2: Group by day
    days_data = _group_forecast_by_day(weather_result["data"]["list"])

    # Step 3: Get seasonal context (our Canadian data layer)
    # Use the first forecast date's month for seasonal lookup
    try:
        first_date  = list(days_data.keys())[0]
        month       = int(first_date.split("-")[1])
    except (IndexError, ValueError):
        month = datetime.now().month

    prov = province or ""
    seasonal = get_seasonal_info(prov, month) if prov else None

    # Step 4: Build itinerary day by day
    itinerary = []
    sorted_dates = sorted(days_data.keys())[:days]  # Limit to requested days

    for i, date in enumerate(sorted_dates, start=1):
        day_weather = days_data[date]

        # Calculate day's weather summary
        avg_temp  = sum(w["temp"] for w in day_weather) / len(day_weather)
        max_temp  = max(w["temp"] for w in day_weather)
        min_temp  = min(w["temp"] for w in day_weather)
        total_rain = sum(w["rain_mm"] for w in day_weather)
        has_rain  = total_rain > 0.5  # >0.5mm is meaningful rain
        condition = _get_weather_condition(avg_temp, has_rain)

        # Midday description (most representative)
        midday_idx = len(day_weather) // 2
        weather_desc = day_weather[midday_idx]["description"]

        # Pick activities based on weather + interest + budget
        activities = _pick_activities(condition, interest, budget_style)

        # Format date nicely: "2024-07-15" → "Monday, July 15"
        try:
            dt_obj = datetime.strptime(date, "%Y-%m-%d")
            friendly_date = dt_obj.strftime("%A, %B %-d")
        except Exception:
            friendly_date = date

        day_plan = {
            "day":         i,
            "date":        date,
            "date_label":  friendly_date,
            "weather": {
                "condition":    condition,
                "description":  weather_desc.capitalize(),
                "avg_temp_c":   round(avg_temp, 1),
                "max_temp_c":   round(max_temp, 1),
                "min_temp_c":   round(min_temp, 1),
                "rain_mm":      round(total_rain, 1),
                "has_rain":     has_rain,
            },
            "suggested_activities": activities,
            "tip": _generate_day_tip(condition, city, i, seasonal),
        }
        itinerary.append(day_plan)

    # Step 5: Budget estimate for the trip
    accom_cost  = get_accommodation_cost(city, budget_style)
    food_cost   = FOOD_COSTS_PER_DAY.get(budget_style, FOOD_COSTS_PER_DAY["mid"])

    return {
        "city":          city.title(),
        "days":          days,
        "budget_style":  budget_style,
        "interest_focus": interest,
        "itinerary":     itinerary,
        "weather_note":  "Uses mock weather data — add OWM_KEY to .env for real forecasts" if weather_result.get("mock") else "Live weather forecast",

        "cost_estimate": {
            "accommodation_per_night": accom_cost["avg"],
            "food_per_day":            food_cost["amount"],
            "total_accommodation":     accom_cost["avg"] * days,
            "total_food":              food_cost["amount"] * days,
            "currency":                "CAD",
        },

        "seasonal_alert": seasonal["alert"] if seasonal else None,
        "seasonal_highlight": seasonal["highlight"] if seasonal else None,
    }


def _generate_day_tip(condition: str, city: str, day_num: int, seasonal: dict) -> str:
    """
    Returns a practical tip for the day.

    WHY:
        Generic itinerary builders just list activities. Adding a specific
        tip (like "arrive at Lake Louise before 8am") is what makes your
        tool feel like a real travel expert, not just an AI.
    """
    tips = {
        "rain":  f"Rain day — perfect for indoor experiences you'd skip in good weather.",
        "cold":  f"Cold but crisp — dress in layers and plan indoor breaks every 2 hours.",
        "cool":  f"Cool and comfortable — ideal hiking weather with fewer crowds.",
        "mild":  f"Near-perfect conditions — prioritize outdoor activities today.",
        "warm":  f"Warm day — start outdoor activities before 10am, rest midday.",
        "hot":   f"Hot day — hike early (before 9am), swim midday, sightsee in the evening.",
    }
    base_tip = tips.get(condition, "Check local conditions before heading out.")

    # Add seasonal alert on day 1 if available
    if day_num == 1 and seasonal and seasonal.get("alert"):
        return f"{base_tip} Note: {seasonal['alert']}"

    return base_tip


# ─────────────────────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING: tools/weather_itinerary.py")
    if not OWM_KEY:
        print("(No OWM_KEY found — using mock weather data)")
    print("=" * 60)

    print("\n[TEST 1] 3-day hiking trip to Banff")
    result = build_itinerary("Banff", days=3, budget_style="mid", interest="hiking", province="alberta")
    if result.get("error"):
        print(f"  ERROR: {result['message']}")
    else:
        print(f"  City: {result['city']} | Days: {result['days']}")
        print(f"  Weather note: {result['weather_note']}")
        for day in result["itinerary"]:
            print(f"\n  {day['date_label']}:")
            print(f"    Weather: {day['weather']['description']} | {day['weather']['avg_temp_c']}°C avg")
            print(f"    Activities: {day['suggested_activities']}")
            print(f"    Tip: {day['tip'][:70]}...")
        print(f"\n  Accommodation/night: ${result['cost_estimate']['accommodation_per_night']} CAD")
        print(f"  Food/day:            ${result['cost_estimate']['food_per_day']} CAD")

    print("\n[TEST 2] 2-day food trip to Montreal")
    result = build_itinerary("Montreal", days=2, budget_style="budget", interest="food", province="quebec")
    if not result.get("error"):
        print(f"  City: {result['city']}")
        if result["seasonal_alert"]:
            print(f"  Seasonal alert: {result['seasonal_alert']}")
        for day in result["itinerary"]:
            print(f"  Day {day['day']}: {day['suggested_activities']}")

    print("\n[TEST 3] Activity picker in isolation (no API)")
    print("  rain + hiking:  ", _pick_activities("rain", "hiking", "mid"))
    print("  warm + food:    ", _pick_activities("warm", "food", "budget"))
    print("  cold + family:  ", _pick_activities("cold", "family", "luxury"))

    print("\n✓ Weather itinerary tests complete")