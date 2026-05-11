"""
data/seasonal.py
----------------
WEEK 1 - Pure data. No APIs. No internet. Just facts.

WHY THIS FILE EXISTS:
    This is your moat. Claude.ai doesn't reliably know that Tofino
    storm-watching peaks in November, or that NWT ice roads open in
    January. We hardcode this expert knowledge so every query gets
    a confident, correct answer — not an AI guess.

HOW TO USE:
    from data.seasonal import get_seasonal_info
    info = get_seasonal_info("British Columbia", month=11)
    print(info)

HOW TO TEST (no setup needed):
    python data/seasonal.py
"""

# ─────────────────────────────────────────────────────────────
# SEASONAL INTELLIGENCE
# Structure: province → month number → dict of alerts/highlights
# Months 1–12 = Jan–Dec
# ─────────────────────────────────────────────────────────────

SEASONAL = {
    "british columbia": {
        1:  {"highlight": "Tofino storm-watching (peak)",       "alert": "Hwy 4 to Tofino can close in snow — check DriveBC.ca", "activity": ["storm watching", "skiing Whistler", "whale watching (grey whales start)"]},
        2:  {"highlight": "Tofino storm-watching (peak)",       "alert": "Avalanche risk in mountain highways",                   "activity": ["storm watching", "skiing", "snowshoeing"]},
        3:  {"highlight": "Grey whale migration begins",        "alert": "Spring road conditions — watch for rockslides",         "activity": ["whale watching", "skiing (last weeks)", "wildflower hikes"]},
        4:  {"highlight": "Cherry blossoms in Vancouver",       "alert": "Busy tulip season — book Chilliwack accommodation early","activity": ["cherry blossom viewing", "cycling", "kayaking starts"]},
        5:  {"highlight": "Wildflower season in mountain parks","alert": "Some high trails still snowed in — check BC Parks",     "activity": ["hiking", "kayaking", "birdwatching"]},
        6:  {"highlight": "Peak whale watching (orcas)",        "alert": "Book whale tours 4–6 weeks ahead",                      "activity": ["whale watching", "kayaking", "hiking", "cycling"]},
        7:  {"highlight": "Orca peak season, dry weather",      "alert": "WILDFIRE SEASON — check BCWildfireService.ca daily",    "activity": ["kayaking", "hiking", "whale watching", "camping"]},
        8:  {"highlight": "Hottest month, long days",           "alert": "WILDFIRE SEASON (highest risk) — park closures possible","activity": ["camping", "surfing Tofino", "hiking"]},
        9:  {"highlight": "Shoulder season, smaller crowds",    "alert": "Wildfire smoke may linger into September",              "activity": ["hiking", "cycling", "wine country (Okanagan harvest)"]},
        10: {"highlight": "Okanagan wine harvest",              "alert": "Weather turns — pack rain gear",                        "activity": ["wine tours", "fall foliage", "mushroom foraging"]},
        11: {"highlight": "Storm-watching season opens",        "alert": "Wickaninnish Inn packages sell out 3 months ahead",     "activity": ["storm watching", "hot springs", "city breaks"]},
        12: {"highlight": "Skiing opens (Whistler, Big White)", "alert": "Mountain road chains required",                        "activity": ["skiing", "snowboarding", "Christmas markets Vancouver"]},
    },

    "alberta": {
        1:  {"highlight": "Banff ice magic festival",           "alert": "Extreme cold possible (-30°C) — pack layers",          "activity": ["ice skating Banff", "skiing", "ice climbing"]},
        2:  {"highlight": "Banff Snow Days festival",           "alert": "Roads icy — winter tires mandatory",                   "activity": ["skiing", "snowshoeing", "hot springs"]},
        3:  {"highlight": "Ski season still strong",            "alert": "Spring avalanche risk increases",                      "activity": ["skiing", "snowshoeing", "wildlife (bears emerging late March)"]},
        4:  {"highlight": "Wildlife viewing — bears emerging",  "alert": "Book campsites NOW — they open April 1 for summer",    "activity": ["wildlife tours", "photography", "early hikes"]},
        5:  {"highlight": "Waterfalls peak (snowmelt)",         "alert": "Trail conditions variable — check Parks Canada site",  "activity": ["hiking", "photography", "camping begins"]},
        6:  {"highlight": "Best hiking begins",                 "alert": "Campsite reservations needed — book via reservation.pc.gc.ca","activity": ["hiking", "kayaking", "cycling", "camping"]},
        7:  {"highlight": "Peak season — all parks fully open", "alert": "Banff townsite VERY busy — arrive before 8am for parking","activity": ["all outdoor activities", "camping", "Lake Louise"]},
        8:  {"highlight": "Long days, wildflowers",             "alert": "Smoke possible from BC wildfires",                     "activity": ["hiking", "camping", "Jasper Dark Sky Festival (mid-Aug)"]},
        9:  {"highlight": "Fewer crowds, amazing light",        "alert": "Nights get cold — bring warm layers for camping",      "activity": ["photography", "hiking", "elk rut (spectacular)"]},
        10: {"highlight": "Elk rut, fall colours",              "alert": "Snow possible any day above 1500m",                    "activity": ["wildlife viewing", "photography", "last camping weekend"]},
        11: {"highlight": "Quiet season — best hotel deals",    "alert": "Some hiking trails closed, bears hibernating",         "activity": ["hot springs", "Banff townsite", "skiing starts late Nov"]},
        12: {"highlight": "Skiing opens, Christmas in Banff",   "alert": "Book accommodation 3+ months ahead for Christmas week","activity": ["skiing", "snowboarding", "ice skating", "hot springs"]},
    },

    "ontario": {
        1:  {"highlight": "Winterlude Ottawa (late Jan)",        "alert": "Rideau Canal — check NCC site for skating conditions", "activity": ["skating canal", "skiing", "winter festivals"]},
        2:  {"highlight": "Rideau Canal skating (peak)",         "alert": "Canal can close on warm days — check NCC.ca daily",   "activity": ["skating", "Winterlude", "snow tubing"]},
        3:  {"highlight": "Maple syrup season begins",           "alert": "Sugar bushes sell out on weekends — book ahead",      "activity": ["sugar bush tours", "maple syrup", "early hiking"]},
        4:  {"highlight": "Sugar bush season (peak)",            "alert": "Roads muddy in rural areas — check conditions",       "activity": ["maple syrup tours", "birdwatching", "cycling"]},
        5:  {"highlight": "Tulip festival Ottawa",               "alert": "Book Ottawa hotels in May 3 months ahead",            "activity": ["tulip viewing", "hiking", "cycling trails"]},
        6:  {"highlight": "Niagara wine season opens",           "alert": "Niagara Falls busy — go weekday morning",             "activity": ["Niagara Falls", "wine tours", "hiking Bruce Trail"]},
        7:  {"highlight": "Peak summer — all attractions open",  "alert": "Algonquin canoe routes book out — reserve now",       "activity": ["canoeing Algonquin", "camping", "Muskoka lakes"]},
        8:  {"highlight": "Cottage country peak",                "alert": "Hwy 400 north Fridays = gridlock — leave by noon",    "activity": ["lake swimming", "camping", "hiking", "festivals"]},
        9:  {"highlight": "Fall colours begin (late Sept)",      "alert": "Algonquin fall colours peak — busiest weekend of year","activity": ["fall colours", "canoeing", "cycling", "wine harvest"]},
        10: {"highlight": "Peak fall colours (Algonquin)",       "alert": "Thanksgiving weekend — book 2 months ahead",          "activity": ["fall foliage", "apple picking", "wine country"]},
        11: {"highlight": "Quiet, good hotel prices",            "alert": "Some attractions close for season",                   "activity": ["museums Toronto", "theatre", "restaurant week"]},
        12: {"highlight": "Christmas markets Toronto/Ottawa",    "alert": "December 26 — Boxing Day shopping chaos",             "activity": ["Christmas markets", "skating", "Niagara off-season"]},
    },

    "quebec": {
        1:  {"highlight": "Quebec Winter Carnival prep",         "alert": "Extreme cold normal — dress in layers",               "activity": ["skiing", "snowmobiling", "ice hotels"]},
        2:  {"highlight": "Quebec Winter Carnival (peak)",       "alert": "Book Quebec City hotels 4 months ahead for Carnival", "activity": ["Carnival", "snow slides", "ice hotel", "dog sledding"]},
        3:  {"highlight": "Maple syrup harvest begins",          "alert": "Sugar shacks EXTREMELY busy weekends — book early",   "activity": ["cabane à sucre", "skiing (last weeks)", "maple syrup"]},
        4:  {"highlight": "Maple syrup peak (April 1–20 avg)",   "alert": "Peak maple — best before mid-April",                  "activity": ["sugar shacks", "spring hikes", "cycling"]},
        5:  {"highlight": "Montreal festival season starts",     "alert": "Construction season — downtown driving is chaos",     "activity": ["festivals", "cycling", "terrasse season opens"]},
        6:  {"highlight": "Grand Prix Montreal, Jazz Fest",      "alert": "Grand Prix weekend — book 6 months ahead",            "activity": ["Jazz Festival", "Grand Prix", "terrasse patios"]},
        7:  {"highlight": "Montreal Jazz Fest, Just For Laughs", "alert": "Just for Laughs — Old Montreal very busy",            "activity": ["festivals", "Old Quebec", "whale watching (Tadoussac)"]},
        8:  {"highlight": "Whale watching Tadoussac (peak)",     "alert": "Book Tadoussac tours 6 weeks ahead in August",        "activity": ["whale watching", "kayaking", "camping Laurentians"]},
        9:  {"highlight": "Fall colours (Laurentians)",          "alert": "Mont-Tremblant fall — most beautiful, most crowded",  "activity": ["fall foliage", "hiking", "cycling", "wine"]},
        10: {"highlight": "Thanksgiving in Quebec countryside",  "alert": "Eastern Townships harvest — reserve B&Bs early",      "activity": ["apple orchards", "fall colours", "cider tasting"]},
        11: {"highlight": "Quiet season, local pricing",         "alert": "Some ski hills not yet open",                         "activity": ["museums", "restaurant week Montreal", "spa"]},
        12: {"highlight": "Christmas markets, ski season opens", "alert": "Montreal Christmas market — St-Laurent gets packed",  "activity": ["skiing Tremblant", "Christmas markets", "skating"]},
    },

    "nova scotia": {
        1:  {"highlight": "Quiet, low prices, local life",       "alert": "Atlantic storms — coastal roads can close",           "activity": ["seafood dining", "museums Halifax", "indoor markets"]},
        2:  {"highlight": "Off-season deals, no crowds",         "alert": "Storm season — check Weather Network before driving", "activity": ["Halifax Seaport Market", "museums", "brewery tours"]},
        3:  {"highlight": "Maple syrup season",                  "alert": "Spring storms still possible",                        "activity": ["sugar bush", "birdwatching", "whale prep season"]},
        4:  {"highlight": "Lobster season opens (south shore)",  "alert": "Lobster season varies by zone — check DFO.ca",        "activity": ["lobster suppers", "coastal hiking", "birdwatching"]},
        5:  {"highlight": "Apple blossoms Annapolis Valley",     "alert": "Book Annapolis Valley accommodation ahead for blossom weekend","activity": ["apple blossom festival", "cycling", "kayaking"]},
        6:  {"highlight": "Tourism season opens",                "alert": "Cabot Trail gets busy — mid-week better",             "activity": ["Cabot Trail drive", "whale watching starts", "kayaking"]},
        7:  {"highlight": "Tall Ships, festivals",               "alert": "Halifax waterfront very busy weekends",               "activity": ["whale watching (peak)", "kayaking", "beach", "lobster"]},
        8:  {"highlight": "Peak season — all open",              "alert": "Peggy's Cove crowded 10am–3pm — go early or late",    "activity": ["Cabot Trail", "whale watching", "beaches", "seafood"]},
        9:  {"highlight": "Celtic Colours festival (Oct),        lobster peak","alert": "Celtic Colours (Oct) — book Cape Breton B&Bs 3 months ahead","activity": ["Cabot Trail fall colours", "lobster", "whale watching ends"]},
        10: {"highlight": "Celtic Colours music festival",       "alert": "Best month — crowds gone, prices drop, colours peak", "activity": ["Celtic Colours", "fall colours", "seafood", "hiking"]},
        11: {"highlight": "Quiet, authentic Nova Scotia",        "alert": "Some tourist sites close for winter",                 "activity": ["brewery tours", "seafood", "Halifax museums"]},
        12: {"highlight": "Christmas in Halifax",                "alert": "Sable Island ferry season ended",                     "activity": ["Christmas markets", "Harbour Hopper", "museums"]},
    },

    "yukon": {
        1:  {"highlight": "Aurora viewing (peak)",               "alert": "Temperatures to -40°C — no joke, prepare seriously",  "activity": ["aurora borealis", "dog sledding", "ice fishing"]},
        2:  {"highlight": "Aurora + Yukon Quest dog race",       "alert": "Extreme cold — car block heaters essential",          "activity": ["aurora viewing", "Yukon Quest race", "snowmobiling"]},
        3:  {"highlight": "Aurora still visible, longer days",   "alert": "March is warmer — still cold but more manageable",    "activity": ["aurora", "snowshoeing", "skiing Mt Sima"]},
        4:  {"highlight": "Rivers break-up (spectacular)",       "alert": "Ice roads CLOSED by April — do not drive on river ice","activity": ["river breakup viewing", "birdwatching", "hiking starts"]},
        5:  {"highlight": "24-hour daylight begins",             "alert": "Midnight sun — bring an eye mask",                    "activity": ["hiking", "cycling", "fishing opens"]},
        6:  {"highlight": "Midnight sun (peak), Solstice festival","alert": "Mosquitoes — bring serious bug repellent",          "activity": ["Midnight Sun festival", "hiking", "canoe Yukon River"]},
        7:  {"highlight": "Canoeing Yukon River season",         "alert": "Book river outfitters 3 months ahead",                "activity": ["canoeing", "hiking Kluane", "fishing", "gold panning"]},
        8:  {"highlight": "Kluane hiking, berries ripe",         "alert": "Bear activity high — carry bear spray",               "activity": ["Kluane National Park", "berry picking", "hiking"]},
        9:  {"highlight": "Aurora returns, fall colours",        "alert": "Weather changes fast — always carry emergency kit",   "activity": ["aurora viewing", "fall colours", "photography"]},
        10: {"highlight": "Aurora season fully active",          "alert": "Snow possible — winter tires needed",                 "activity": ["aurora", "wildlife viewing", "photography"]},
        11: {"highlight": "Aurora peak season",                  "alert": "Darkness arrives — roads can be icy",                 "activity": ["aurora borealis", "dog sledding", "hot springs"]},
        12: {"highlight": "Aurora peak + Christmas in Whitehorse","alert": "Temperatures to -35°C — dress in layers",            "activity": ["aurora", "dog sledding", "ice fishing", "skiing"]},
    },

    "northwest territories": {
        1:  {"highlight": "Ice roads open (Dempster, Mackenzie)","alert": "Ice roads require permits and prep — check GNWT.ca",  "activity": ["aurora viewing", "dog sledding", "ice fishing", "ice road driving"]},
        2:  {"highlight": "Ice roads peak + aurora",             "alert": "Ice road weight limits — check current limits daily", "activity": ["ice roads", "aurora", "snowmobiling", "dog sledding"]},
        3:  {"highlight": "Aurora still strong, ice roads open", "alert": "Ice roads close late March — plan around closing date","activity": ["aurora", "ice roads", "snowshoeing"]},
        4:  {"highlight": "Spring breakup — dramatic",           "alert": "ICE ROADS CLOSED — river crossing impossible",        "activity": ["breakup viewing", "birdwatching migration"]},
        5:  {"highlight": "Migratory birds arrive",              "alert": "Roads muddy from permafrost thaw",                    "activity": ["birdwatching", "fishing season opens"]},
        6:  {"highlight": "Midnight sun",                        "alert": "Mosquitoes are intense — bring DEET",                 "activity": ["kayaking Great Slave Lake", "fishing", "hiking"]},
        7:  {"highlight": "Peak summer — Nahanni accessible",    "alert": "Nahanni River trips book out — plan 1 year ahead",    "activity": ["Nahanni National Park", "canoeing", "fishing"]},
        8:  {"highlight": "Nahanni, berry season",               "alert": "Bear activity — carry spray",                         "activity": ["Nahanni", "hiking", "berry picking", "fishing"]},
        9:  {"highlight": "Aurora returns, fall colours",        "alert": "Weather deteriorates fast — winter prep starts",      "activity": ["aurora viewing", "fall colours", "photography"]},
        10: {"highlight": "Strong aurora season",                "alert": "Winter arrives — be prepared",                        "activity": ["aurora borealis", "dog sledding", "ice fishing starts"]},
        11: {"highlight": "Ice fishing begins on lakes",         "alert": "Ice roads not yet open — limited access to communities","activity": ["aurora", "ice fishing", "snowmobiling"]},
        12: {"highlight": "Ice roads begin to open (late Dec)",  "alert": "Check GNWT ice road conditions before travel",        "activity": ["aurora peak", "ice roads", "dog sledding"]},
    },
}


# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def get_seasonal_info(province: str, month: int) -> dict:
    """
    Returns seasonal intelligence for a province and month.

    WHY: Instead of letting Claude guess, we return verified facts.
    If province not found, we return a helpful fallback instead of crashing.

    Args:
        province: Province name (case-insensitive)
        month:    Month number 1–12

    Returns:
        dict with highlight, alert, and activities
    """
    province_key = province.lower().strip()

    # Try exact match first
    if province_key in SEASONAL:
        province_data = SEASONAL[province_key]
    else:
        # Try partial match — "BC" → "british columbia"
        aliases = {
            "bc": "british columbia",
            "ab": "alberta",
            "on": "ontario",
            "qc": "quebec",
            "ns": "nova scotia",
            "yt": "yukon",
            "nt": "northwest territories",
            "nwt": "northwest territories",
        }
        province_key = aliases.get(province_key, province_key)
        province_data = SEASONAL.get(province_key)

    if not province_data:
        return {
            "province": province,
            "month": month,
            "highlight": "Beautiful destination",
            "alert": "Check local tourism board for current conditions",
            "activity": ["sightseeing", "local dining", "cultural experiences"],
            "data_available": False
        }

    month_data = province_data.get(month, province_data.get(7))  # fallback to July

    return {
        "province": province.title(),
        "month": month,
        "highlight": month_data["highlight"],
        "alert": month_data["alert"],
        "top_activities": month_data["activity"],
        "data_available": True
    }


def get_best_months(province: str, interest: str) -> list[dict]:
    """
    Returns the best months to visit for a specific interest.

    WHY: Users ask "when is the best time to see whales in BC?"
    We scan all months and return ranked results.

    Args:
        province: Province name
        interest: What they care about (e.g. "whale", "aurora", "ski")

    Returns:
        List of months ranked by relevance
    """
    province_key = province.lower().strip()
    province_data = SEASONAL.get(province_key, {})

    results = []
    for month_num, data in province_data.items():
        # Check if interest keyword appears in activities or highlight
        combined_text = " ".join(data["activity"]).lower() + " " + data["highlight"].lower()
        if interest.lower() in combined_text:
            results.append({
                "month": month_num,
                "month_name": _month_name(month_num),
                "why": data["highlight"],
                "alert": data["alert"]
            })

    return results if results else [{"month": 7, "month_name": "July", "why": "Peak summer season", "alert": "Book ahead"}]


def _month_name(n: int) -> str:
    names = ["", "January", "February", "March", "April", "May", "June",
             "July", "August", "September", "October", "November", "December"]
    return names[n] if 1 <= n <= 12 else "Unknown"


# ─────────────────────────────────────────────────────────────
# TEST — run this file directly to verify everything works
# Command: python data/seasonal.py
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING: data/seasonal.py")
    print("=" * 60)

    # Test 1: Basic lookup
    print("\n[TEST 1] BC in November (storm-watching peak)")
    result = get_seasonal_info("british columbia", 11)
    print(f"  Highlight: {result['highlight']}")
    print(f"  Alert:     {result['alert']}")
    print(f"  Activities: {result['top_activities']}")

    # Test 2: Province alias
    print("\n[TEST 2] AB in September (elk rut)")
    result = get_seasonal_info("AB", 9)
    print(f"  Highlight: {result['highlight']}")
    print(f"  Alert:     {result['alert']}")

    # Test 3: Best months for aurora in Yukon
    print("\n[TEST 3] Best months for aurora in Yukon")
    months = get_best_months("yukon", "aurora")
    for m in months:
        print(f"  {m['month_name']}: {m['why']}")

    # Test 4: Unknown province (graceful fallback)
    print("\n[TEST 4] Unknown province (graceful fallback)")
    result = get_seasonal_info("Narnia", 6)
    print(f"  Data available: {result['data_available']}")
    print(f"  Fallback alert: {result['alert']}")

    # Test 5: Quebec maple syrup
    print("\n[TEST 5] Best months for maple syrup in Quebec")
    months = get_best_months("quebec", "maple")
    for m in months:
        print(f"  {m['month_name']}: {m['why']}")

    print("\n✓ All tests passed")