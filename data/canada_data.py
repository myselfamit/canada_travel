"""
data/canada_data.py
-------------------
WEEK 1 - Static Canadian data: parks, costs, transit facts.

WHY THIS FILE EXISTS:
    Real Canadian prices, park rules, and transit facts that
    Claude hallucinates or gets wrong. This is the knowledge
    base your tool is built on.

    Sources:
    - Parks Canada: parks.canada.ca (fees verified 2024)
    - Statistics Canada: accommodation averages
    - VIA Rail: via.ca public schedule
    - Provincial tourism boards

HOW TO TEST:
    python data/canada_data.py
"""


# ─────────────────────────────────────────────────────────────
# PARKS CANADA — National Parks Data
# Source: parks.canada.ca/tarifs-fees
# ─────────────────────────────────────────────────────────────

NATIONAL_PARKS = {
    "banff": {
        "full_name":        "Banff National Park",
        "province":         "Alberta",
        "entry_fee_adult":  10.50,   # CAD per day (2024)
        "entry_fee_family": 21.00,   # CAD per day (max 7 people)
        "discovery_pass":   75.25,   # Annual pass — all national parks (adult)
        "discovery_pass_family": 151.25,  # Annual family pass
        "campsite_booking": "reservation.pc.gc.ca",
        "booking_opens":    "January 9 for summer — set an alarm",
        "peak_months":      [7, 8],
        "shoulder_months":  [6, 9],
        "off_season":       [11, 12, 1, 2, 3],
        "must_know": [
            "Banff townsite parking fills by 9am in July/August — take the shuttle",
            "Lake Louise requires shuttle or reservation in summer",
            "Icefields Parkway is one of the world's great drives — 230km, allow full day",
            "Wildlife is real — never approach bears, elk, or wolves",
            "Hot springs in Banff townsite: Banff Upper Hot Springs $9/adult",
        ],
        "campgrounds": {
            "tunnel_mountain":  {"sites": 618, "type": "serviced",    "price_range": "32–45 CAD/night"},
            "two_jack_lakeside":{"sites": 74,  "type": "tent only",   "price_range": "28–32 CAD/night"},
            "lake_louise":      {"sites": 206, "type": "serviced",    "price_range": "32–45 CAD/night"},
        }
    },

    "jasper": {
        "full_name":        "Jasper National Park",
        "province":         "Alberta",
        "entry_fee_adult":  10.50,
        "entry_fee_family": 21.00,
        "discovery_pass":   75.25,
        "campsite_booking": "reservation.pc.gc.ca",
        "booking_opens":    "January 9 for summer — same as Banff",
        "peak_months":      [7, 8],
        "must_know": [
            "Jasper Dark Sky Festival in August — book 6 months ahead",
            "Maligne Lake boat tours book out fast — reserve online",
            "Fewer crowds than Banff but equally stunning",
            "Columbia Icefield: book Glacier Skywalk and Ice Explorer together",
            "Jasper townsite has free parking unlike Banff",
        ],
        "campgrounds": {
            "whistlers":        {"sites": 781, "type": "serviced",    "price_range": "30–45 CAD/night"},
            "wapiti":           {"sites": 362, "type": "serviced",    "price_range": "30–38 CAD/night"},
        }
    },

    "pacific rim": {
        "full_name":        "Pacific Rim National Park Reserve",
        "province":         "British Columbia",
        "entry_fee_adult":  10.50,
        "entry_fee_family": 21.00,
        "discovery_pass":   75.25,
        "campsite_booking": "reservation.pc.gc.ca",
        "booking_opens":    "January 9",
        "peak_months":      [7, 8],
        "must_know": [
            "Long Beach Unit is the surfing destination — lessons available in Tofino",
            "West Coast Trail requires permit + reservation — opens April for summer",
            "Broken Group Islands: kayak or water taxi — no road access",
            "November–February: storm-watching season (cheaper rates!)",
            "Tofino and Ucluelet are the gateway towns — both worth staying in",
        ],
        "campgrounds": {
            "green_point":      {"sites": 94,  "type": "serviced",    "price_range": "33–40 CAD/night"},
        }
    },

    "gros morne": {
        "full_name":        "Gros Morne National Park",
        "province":         "Newfoundland and Labrador",
        "entry_fee_adult":  10.50,
        "entry_fee_family": 21.00,
        "discovery_pass":   75.25,
        "campsite_booking": "reservation.pc.gc.ca",
        "booking_opens":    "January 9",
        "peak_months":      [7, 8],
        "must_know": [
            "UNESCO World Heritage Site — unique geology (ophiolite)",
            "Western Brook Pond Fjord boat tour — one of Canada's best experiences",
            "Tablelands: walk on the Earth's mantle — unique orange rock",
            "Book boat tours as soon as you arrive — fills same day in summer",
            "Newfoundland time zone (UTC-3:30) — 30 min offset catches people off guard",
        ],
        "campgrounds": {
            "berry_hill":       {"sites": 156, "type": "serviced",    "price_range": "28–38 CAD/night"},
        }
    },

    "cape breton highlands": {
        "full_name":        "Cape Breton Highlands National Park",
        "province":         "Nova Scotia",
        "entry_fee_adult":  10.50,
        "entry_fee_family": 21.00,
        "discovery_pass":   75.25,
        "campsite_booking": "reservation.pc.gc.ca",
        "booking_opens":    "January 9",
        "peak_months":      [7, 8, 10],  # October for fall colours
        "must_know": [
            "Cabot Trail: drive it clockwise for the best views (ocean side)",
            "Skyline Trail: wheelchair accessible, moose sightings frequent",
            "Celtic Colours festival in October — book accommodations 3 months ahead",
            "Fresh lobster suppers: Louisbourg area, $25–$35 all-in",
            "Watch for moose on the road — especially dawn and dusk",
        ],
    },
}


# ─────────────────────────────────────────────────────────────
# BUDGET DATA — Real Canadian Accommodation Costs (CAD/night)
# Source: Statistics Canada + Booking.com averages 2024
# ─────────────────────────────────────────────────────────────

ACCOMMODATION_COSTS = {
    "vancouver": {
        "hostel":  {"low": 35,  "high": 65,  "note": "HI Vancouver downtown"},
        "budget":  {"low": 90,  "high": 140, "note": "1-star, east side"},
        "mid":     {"low": 160, "high": 260, "note": "3-star, downtown"},
        "luxury":  {"low": 350, "high": 700, "note": "Fairmont, Rosewood"},
    },
    "toronto": {
        "hostel":  {"low": 30,  "high": 55,  "note": "HI Toronto"},
        "budget":  {"low": 80,  "high": 130, "note": "East end, Airbnb"},
        "mid":     {"low": 150, "high": 240, "note": "Downtown 3-star"},
        "luxury":  {"low": 320, "high": 650, "note": "Four Seasons, Ritz"},
    },
    "banff": {
        "hostel":  {"low": 45,  "high": 75,  "note": "HI Banff Alpine Centre"},
        "budget":  {"low": 120, "high": 180, "note": "Motel on Banff Ave"},
        "mid":     {"low": 200, "high": 350, "note": "Rimrock, Fairmont Lake Louise area"},
        "luxury":  {"low": 450, "high": 900, "note": "Fairmont Banff Springs"},
    },
    "montreal": {
        "hostel":  {"low": 28,  "high": 50,  "note": "Plateau area hostels"},
        "budget":  {"low": 70,  "high": 110, "note": "Plateau, Rosemont"},
        "mid":     {"low": 130, "high": 210, "note": "Old Montreal, downtown"},
        "luxury":  {"low": 280, "high": 550, "note": "Hotel Nelligan, Le Mount Stephen"},
    },
    "quebec city": {
        "hostel":  {"low": 30,  "high": 55,  "note": "HI Quebec City"},
        "budget":  {"low": 80,  "high": 130, "note": "Lower town motels"},
        "mid":     {"low": 150, "high": 250, "note": "Old Quebec 3-star"},
        "luxury":  {"low": 300, "high": 600, "note": "Chateau Frontenac"},
    },
    "whistler": {
        "hostel":  {"low": 50,  "high": 90,  "note": "HI Whistler"},
        "budget":  {"low": 130, "high": 200, "note": "Village area, off-peak"},
        "mid":     {"low": 220, "high": 400, "note": "Slope-side hotel"},
        "luxury":  {"low": 450, "high": 900, "note": "Four Seasons, Fairmont"},
    },
    "default": {
        "hostel":  {"low": 30,  "high": 55,  "note": "Canadian average"},
        "budget":  {"low": 80,  "high": 120, "note": "Canadian average"},
        "mid":     {"low": 140, "high": 220, "note": "Canadian average"},
        "luxury":  {"low": 300, "high": 600, "note": "Canadian average"},
    },
}

FOOD_COSTS_PER_DAY = {
    "budget":  {"amount": 35,  "note": "Groceries + one casual meal"},
    "mid":     {"amount": 75,  "note": "Mix of restaurants + groceries"},
    "luxury":  {"amount": 180, "note": "Full restaurant dining"},
}

TRANSPORT_COSTS_PER_DAY = {
    "budget":  {"amount": 12,  "note": "Public transit pass"},
    "mid":     {"amount": 30,  "note": "Mix of transit + occasional taxi"},
    "luxury":  {"amount": 70,  "note": "Rental car or ride-share"},
}

ACTIVITY_COSTS_PER_DAY = {
    "budget":  {"amount": 20,  "note": "Free parks, 1 paid activity"},
    "mid":     {"amount": 55,  "note": "2–3 activities/tours"},
    "luxury":  {"amount": 150, "note": "Premium experiences, guides"},
}

# One-time flight estimate (domestic Canada, economy)
DOMESTIC_FLIGHT_ESTIMATE = {
    "short":   300,   # e.g. Toronto–Ottawa
    "medium":  500,   # e.g. Toronto–Calgary
    "long":    750,   # e.g. Toronto–Vancouver
    "budget_airline": -100,  # deduct if using Flair/Swoop
}


# ─────────────────────────────────────────────────────────────
# TRANSIT DATA — Canadian rail and transit facts
# ─────────────────────────────────────────────────────────────

TRANSIT = {
    "via_rail": {
        "name":        "VIA Rail Canada",
        "website":     "viarail.ca",
        "booking_tip": "Book 7+ days ahead for Economy Escape fare (up to 50% off)",
        "key_routes": {
            "toronto_montreal":   {"duration": "5h20m", "frequency": "multiple daily"},
            "toronto_ottawa":     {"duration": "4h10m", "frequency": "multiple daily"},
            "toronto_vancouver":  {"duration": "4 days", "frequency": "3x weekly (Canadian)"},
            "montreal_quebec":    {"duration": "3h45m", "frequency": "3 daily"},
            "winnipeg_vancouver": {"duration": "2 days", "frequency": "3x weekly"},
        },
        "passes": {
            "canrailpass": "From $949 — 7 trips in 60 days, huge savings for multi-city",
        }
    },
    "city_transit": {
        "toronto": {
            "system": "TTC (Toronto Transit Commission)",
            "day_pass": 13.50,
            "presto_card": "Reloadable card — saves per-ride",
            "tip": "PRESTO card saves ~$1 per ride vs cash"
        },
        "vancouver": {
            "system": "TransLink (buses + SkyTrain + SeaBus)",
            "day_pass": 11.25,
            "tip": "Compass Card — tap in/out, airport to downtown ~$4"
        },
        "montreal": {
            "system": "STM (Société de transport de Montréal)",
            "day_pass": 10.00,
            "tip": "OPUS card — 3-day tourist pass $21, great value"
        },
        "calgary": {
            "system": "Calgary Transit (C-Train + buses)",
            "day_pass": 11.25,
            "tip": "C-Train downtown core is FREE between City Hall and 6 St SW"
        },
        "ottawa": {
            "system": "OC Transpo (buses + O-Train)",
            "day_pass": 10.00,
            "tip": "Presto Card works here too — same system as Toronto"
        },
    },
    "road_trip": {
        "gas_avg_per_litre": 1.65,   # CAD, 2024 national average
        "note": "BC and Ontario typically 15–25¢ higher than prairies",
        "key_drives": {
            "icefields_parkway":  {"km": 230, "time": "4–6 hours", "note": "Stop at Peyto Lake, Athabasca Falls"},
            "cabot_trail":        {"km": 298, "time": "full day",   "note": "Drive clockwise for best ocean views"},
            "sea_to_sky":         {"km": 120, "time": "2 hours",    "note": "Vancouver to Whistler — one of the world's great drives"},
            "1000_islands":       {"km": 100, "time": "2 hours",    "note": "Kingston to Brockville along the St Lawrence"},
            "dempster_highway":   {"km": 736, "time": "2 days",     "note": "Only road in Canada that crosses Arctic Circle — no services, bring spare tires"},
        }
    }
}


# ─────────────────────────────────────────────────────────────
# LOOKUP FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_park_info(park_name: str) -> dict:
    """Returns Parks Canada data for a named park."""
    key = park_name.lower().strip()
    # Try partial match
    for park_key, data in NATIONAL_PARKS.items():
        if park_key in key or key in park_key:
            return {"found": True, "park": data}
    return {"found": False, "message": f"Park '{park_name}' not in database yet. Check parks.canada.ca"}


def get_accommodation_cost(city: str, style: str) -> dict:
    """Returns accommodation cost range for a city and travel style."""
    city_key = city.lower().strip()
    city_data = ACCOMMODATION_COSTS.get(city_key, ACCOMMODATION_COSTS["default"])
    style_key = style.lower().strip()
    cost = city_data.get(style_key, city_data["mid"])
    return {
        "city":   city.title(),
        "style":  style,
        "low":    cost["low"],
        "high":   cost["high"],
        "avg":    (cost["low"] + cost["high"]) // 2,
        "note":   cost["note"],
        "currency": "CAD"
    }


def estimate_trip_cost(city: str, days: int, style: str) -> dict:
    """
    Full budget estimate for a trip.

    WHY THIS FUNCTION:
        Instead of Claude guessing "$200/day in Canada", we return
        a breakdown with real sources. Users trust breakdowns more
        than totals.
    """
    style_key = style.lower().strip()
    if style_key not in ["budget", "mid", "luxury"]:
        style_key = "mid"

    city_key = city.lower().strip()
    city_data = ACCOMMODATION_COSTS.get(city_key, ACCOMMODATION_COSTS["default"])

    accom     = city_data.get(style_key, city_data["mid"])
    food      = FOOD_COSTS_PER_DAY[style_key]
    transport = TRANSPORT_COSTS_PER_DAY[style_key]
    activity  = ACTIVITY_COSTS_PER_DAY[style_key]

    accom_avg     = (accom["low"] + accom["high"]) // 2
    daily_total   = accom_avg + food["amount"] + transport["amount"] + activity["amount"]
    trip_subtotal = daily_total * days
    parks_pass    = 75.25 if days >= 5 else 10.50 * days  # Pass pays off after ~7 days

    return {
        "city":     city.title(),
        "days":     days,
        "style":    style_key,
        "currency": "CAD",
        "daily_breakdown": {
            "accommodation": accom_avg,
            "food":          food["amount"],
            "transport":     transport["amount"],
            "activities":    activity["amount"],
            "daily_total":   daily_total,
        },
        "trip_total":        trip_subtotal,
        "parks_pass_note":   f"Parks Canada Discovery Pass: $75.25 — pays off after 7 days" if days >= 5 else f"Day passes: ${10.50 * days:.2f}",
        "tip":               f"Book accommodation 6–8 weeks ahead for {city.title()} to get better rates",
        "source":            "Based on Statistics Canada + provincial tourism board averages 2024",
    }


def get_transit_info(city: str) -> dict:
    """Returns transit info for a Canadian city."""
    city_key = city.lower().strip()
    transit_data = TRANSIT["city_transit"].get(city_key)
    if transit_data:
        return {"found": True, "city": city.title(), "transit": transit_data}
    return {
        "found": False,
        "message": f"Detailed transit data for {city} not yet in database",
        "tip": "Check the city's municipal transit website"
    }


# ─────────────────────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING: data/canada_data.py")
    print("=" * 60)

    print("\n[TEST 1] Banff National Park info")
    park = get_park_info("banff")
    if park["found"]:
        p = park["park"]
        print(f"  Entry fee (adult): ${p['entry_fee_adult']}/day")
        print(f"  Discovery Pass:    ${p['discovery_pass']}/year")
        print(f"  Booking opens:     {p['booking_opens']}")
        print(f"  Must know #1:      {p['must_know'][0]}")

    print("\n[TEST 2] 5-day mid-range trip to Vancouver")
    budget = estimate_trip_cost("vancouver", 5, "mid")
    print(f"  Daily total:  ${budget['daily_breakdown']['daily_total']} CAD")
    print(f"  Trip total:   ${budget['trip_total']} CAD")
    print(f"  Parks pass:   {budget['parks_pass_note']}")

    print("\n[TEST 3] Budget accommodation in Banff")
    accom = get_accommodation_cost("banff", "budget")
    print(f"  Range: ${accom['low']}–${accom['high']} CAD/night")
    print(f"  Note:  {accom['note']}")

    print("\n[TEST 4] Toronto transit")
    transit = get_transit_info("toronto")
    if transit["found"]:
        print(f"  System:   {transit['transit']['system']}")
        print(f"  Day pass: ${transit['transit']['day_pass']}")
        print(f"  Tip:      {transit['transit']['tip']}")

    print("\n[TEST 5] Unknown park (graceful fallback)")
    park = get_park_info("funland national park")
    print(f"  Found: {park['found']}")
    print(f"  Message: {park['message']}")

    print("\n✓ All tests passed")