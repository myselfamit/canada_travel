"""
tools/budget.py
---------------
TOOL 4: Budget Estimator

Takes: city + days + travel style
Returns: detailed CAD cost breakdown

WHY NO EXTERNAL API HERE:
    At MVP, hardcoded real research beats a live API that might
    return wrong currency, outdated prices, or rate-limit you.
    We cite real sources and update quarterly. Simple wins.

HOW TO TEST:
    python tools/budget.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.canada_data import (
    estimate_trip_cost,
    get_accommodation_cost,
    FOOD_COSTS_PER_DAY,
    TRANSPORT_COSTS_PER_DAY,
    ACTIVITY_COSTS_PER_DAY,
    DOMESTIC_FLIGHT_ESTIMATE,
    NATIONAL_PARKS,
)
from data.seasonal import get_seasonal_info, _month_name


# ─────────────────────────────────────────────────────────────
# SEASONAL PRICE ADJUSTMENTS
# Peak season costs more. This is the nuance no generic tool has.
# ─────────────────────────────────────────────────────────────

# Multipliers applied to base accommodation cost
SEASONAL_MULTIPLIERS = {
    # city_key → {month → multiplier}
    "banff": {
        7: 1.35, 8: 1.35,                  # Peak: +35%
        6: 1.15, 9: 1.10,                  # Shoulder: +10-15%
        12: 1.20, 1: 1.15, 2: 1.15,       # Ski season: +15-20%
        3: 1.0, 4: 0.85, 5: 0.90,         # Off-peak: -10-15%
        10: 0.90, 11: 0.80,               # Off-peak: -10-20%
    },
    "whistler": {
        12: 1.50, 1: 1.45, 2: 1.40,       # Ski peak: +40-50%
        7: 1.25, 8: 1.25,                  # Summer: +25%
        3: 1.20, 4: 0.70,                  # April = mud season discount
        5: 0.80, 6: 0.90,                  # Pre-summer
        9: 0.85, 10: 0.80, 11: 0.70,      # Fall shoulder
    },
    "toronto": {
        6: 1.15, 7: 1.20, 8: 1.20,        # Summer: +15-20%
        9: 1.10, 10: 1.05,                 # Fall: +5-10%
        1: 0.85, 2: 0.85, 3: 0.90,        # Winter: -10-15%
        4: 0.95, 5: 1.0,                   # Spring: normal
        11: 0.90, 12: 1.0,                 # December events push back up
    },
    "montreal": {
        2: 1.35,                            # Carnival: +35%
        6: 1.25, 7: 1.25,                  # Festival season: +25%
        8: 1.20,                            # Still festival season
        1: 0.80, 3: 0.85,                  # Winter off-peak
        4: 0.85, 5: 0.95,                  # Spring
        9: 1.0, 10: 1.0, 11: 0.85, 12: 0.90,
    },
    "default": {m: 1.0 for m in range(1, 13)},  # No adjustment for unlisted cities
}

# Money-saving tips by category — curated Canadian knowledge
SAVINGS_TIPS = {
    "accommodation": [
        "Book mid-week (Tue–Thu) for 10–20% lower rates in most Canadian cities",
        "HI Hostels Canada (hihostels.ca) — reliable, central, $30–75/night across Canada",
        "Parks Canada's Parks Pass ($75.25/adult/year) pays off in just 7 days of park visits",
        "AirBnB in residential neighbourhoods is typically 30% cheaper than downtown hotels",
    ],
    "food": [
        "Grocery stores (Loblaws, Metro, Sobeys) for breakfast and lunch — eat out for dinner only",
        "Lunch specials: most restaurants offer table d'hôte at lunch for 40% less than dinner",
        "Tim Hortons and A&W serve real food for $8–12 — not fancy but genuinely Canadian",
        "Costco in major cities: $1.50 hot dog + drink. Fuel up cheaply.",
    ],
    "transport": [
        "Multi-day transit passes save significantly — ask for tourist passes at major stations",
        "VIA Rail's Escape fares: 7+ days ahead, up to 50% off. Check viarail.ca/en/fares",
        "Flair Airlines for domestic flights — sometimes 60% cheaper than Air Canada",
        "Renting a car outside the airport saves the 25–30% airport surcharge",
    ],
    "activities": [
        "Most provincial and national parks have free entry one day per year (check dates)",
        "Many Canadian museums offer free admission one evening per week",
        "Library cards (often free for visitors in some cities) unlock museum passes",
        "Walking tours: most Canadian cities have free tip-based walking tours — just tip well",
    ],
}


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────

def estimate_budget(
    city:         str,
    days:         int,
    style:        str,
    month:        int  = None,
    include_flight: bool = True,
    flight_type:  str  = "medium",  # "short", "medium", "long", "budget_airline"
) -> dict:
    """
    Full budget estimate for a Canadian trip.

    WHY MONTH MATTERS:
        Banff in April (mud season) is 15% cheaper than July.
        Whistler in April is 30% cheaper than December.
        A tool that ignores this is lying to the user.

    Args:
        city:           Destination
        days:           Trip length in days
        style:          "budget", "mid", or "luxury"
        month:          Month of travel (1–12) for seasonal pricing
        include_flight: Whether to include domestic flight estimate
        flight_type:    "short", "medium", "long", or "budget_airline"

    Returns:
        Detailed cost breakdown in CAD
    """
    print(f"MCP CALLED: estimate_budget({city}, {days} days, {style})")

    style_key = style.lower().strip()
    if style_key not in ["budget", "mid", "luxury"]:
        style_key = "mid"

    city_key = city.lower().strip()

    # Step 1: Get base accommodation cost
    accom = get_accommodation_cost(city, style_key)
    accom_per_night = accom["avg"]
    print(f"DEBUG: base accommodation = {accom_per_night}")

    # Step 2: Apply seasonal multiplier
    city_multipliers = SEASONAL_MULTIPLIERS.get(city_key, SEASONAL_MULTIPLIERS["default"])
    seasonal_mult = city_multipliers.get(month, 1.0) if month else 1.0

    adjusted_accom = round(accom_per_night * seasonal_mult)
    seasonal_note  = ""
    if seasonal_mult > 1.05:
        pct = round((seasonal_mult - 1) * 100)
        seasonal_note = f"Peak season: accommodation ~{pct}% above base rates"
    elif seasonal_mult < 0.95:
        pct = round((1 - seasonal_mult) * 100)
        seasonal_note = f"Off-peak: accommodation ~{pct}% below peak rates — great time to visit!"

    # Step 3: Daily costs
    food      = FOOD_COSTS_PER_DAY[style_key]["amount"]
    transport = TRANSPORT_COSTS_PER_DAY[style_key]["amount"]
    activity  = ACTIVITY_COSTS_PER_DAY[style_key]["amount"]
    daily_total = adjusted_accom + food + transport + activity

    # Step 4: Parks Canada pass decision
    # Pass costs $75.25 but saves $10.50/day per adult
    # Breakeven: 75.25 / 10.50 = 7.2 days
    parks_daily_fee = 10.50
    parks_pass_cost = 75.25
    near_parks = _city_near_parks(city_key)

    if near_parks and days >= 7:
        parks_cost  = parks_pass_cost
        parks_note  = f"Discovery Pass (${parks_pass_cost}) — pays off after 7 days. Covers all national parks for 1 year."
    elif near_parks:
        parks_cost  = parks_daily_fee * days
        parks_note  = f"Day passes: ${parks_daily_fee}/day × {days} days = ${parks_cost:.2f}. Buy a Discovery Pass (${parks_pass_cost}) if you plan to visit again."
    else:
        parks_cost  = 0
        parks_note  = "No nearby national parks — no parks fee needed"

    # Step 5: One-time costs
    flight_cost = 0
    flight_note = "Not included"
    if include_flight:
        base_flight = DOMESTIC_FLIGHT_ESTIMATE.get(flight_type, 500)
        if flight_type == "budget_airline":
            base_flight = DOMESTIC_FLIGHT_ESTIMATE["medium"] + DOMESTIC_FLIGHT_ESTIMATE["budget_airline"]
        flight_cost = max(base_flight, 150)  # Minimum $150 even for short hops
        flight_note = f"Estimated domestic economy — check Air Canada, WestJet, Flair"

    # Step 6: Grand total
    accommodation_total = adjusted_accom * days
    food_total          = food * days
    transport_total     = transport * days
    activity_total      = activity * days
    trip_subtotal       = accommodation_total + food_total + transport_total + activity_total
    grand_total         = trip_subtotal + parks_cost + flight_cost

    # Step 7: Get seasonal context
    seasonal = None
    if month:
        from data.seasonal import get_seasonal_info
        from tools.destination import _infer_province
        prov = _infer_province(city)
        if prov:
            seasonal = get_seasonal_info(prov, month)

    return {
        "city":         city.title(),
        "days":         days,
        "style":        style_key,
        "month":        _month_name(month) if month else "Not specified",
        "currency":     "CAD",

        "daily_costs": {
            "accommodation": adjusted_accom,
            "food":          food,
            "transport":     transport,
            "activities":    activity,
            "total_per_day": daily_total,
        },

        "trip_totals": {
            "accommodation": accommodation_total,
            "food":          food_total,
            "transport":     transport_total,
            "activities":    activity_total,
            "parks_fees":    parks_cost,
            "flight":        flight_cost,
            "grand_total":   grand_total,
        },

        "notes": {
            "seasonal":    seasonal_note or f"Standard rates for {city.title()}",
            "parks":       parks_note,
            "flight":      flight_note,
            "booking_tip": f"Book accommodation 6–8 weeks ahead for best rates in {city.title()}",
        },

        "seasonal_alert": seasonal["alert"] if seasonal else None,

        # Money-saving tips — 1 from each category
        "savings_tips": {
            "accommodation": SAVINGS_TIPS["accommodation"][0],
            "food":          SAVINGS_TIPS["food"][0],
            "transport":     SAVINGS_TIPS["transport"][1],  # VIA Rail tip
            "activities":    SAVINGS_TIPS["activities"][0],
        },

        "source": "Based on Statistics Canada accommodation stats + provincial tourism board averages (2024). Update quarterly.",
    }


def _city_near_parks(city_key: str) -> bool:
    """Returns True if this city is near a national park."""
    park_cities = {
        "banff", "jasper", "lake louise", "tofino", "ucluelet",
        "gros morne", "cape breton", "jasper", "yoho",
        "kootenay", "waterton", "prince albert",
    }
    return city_key in park_cities or any(park in city_key for park in park_cities)


# ─────────────────────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING: tools/budget.py")
    print("=" * 60)

    print("\n[TEST 1] 5-day mid-range trip to Banff in July (peak)")
    result = estimate_budget("Banff", days=5, style="mid", month=7)
    print(f"  Daily total:   ${result['daily_costs']['total_per_day']} CAD")
    print(f"  Accommodation: ${result['daily_costs']['accommodation']}/night (peak season)")
    print(f"  Parks note:    {result['notes']['parks']}")
    print(f"  Seasonal note: {result['notes']['seasonal']}")
    print(f"  Grand total:   ${result['trip_totals']['grand_total']} CAD")

    print("\n[TEST 2] Same trip in November (off-peak)")
    result = estimate_budget("Banff", days=5, style="mid", month=11)
    print(f"  Accommodation: ${result['daily_costs']['accommodation']}/night (off-peak)")
    print(f"  Seasonal note: {result['notes']['seasonal']}")
    print(f"  Grand total:   ${result['trip_totals']['grand_total']} CAD")

    print("\n[TEST 3] Budget traveler, 3 days Toronto in June")
    result = estimate_budget("Toronto", days=3, style="budget", month=6, include_flight=False)
    print(f"  Daily total: ${result['daily_costs']['total_per_day']} CAD")
    print(f"  Trip total:  ${result['trip_totals']['grand_total']} CAD")
    print(f"  Savings tip (food): {result['savings_tips']['food']}")

    print("\n[TEST 4] Luxury trip, Montreal in February (Carnival)")
    result = estimate_budget("Montreal", days=4, style="luxury", month=2)
    print(f"  Accommodation: ${result['daily_costs']['accommodation']}/night (Carnival premium)")
    print(f"  Seasonal note: {result['notes']['seasonal']}")
    print(f"  Grand total:   ${result['trip_totals']['grand_total']} CAD")
    if result["seasonal_alert"]:
        print(f"  Alert: {result['seasonal_alert']}")

    print("\n✓ Budget tests complete")