"""
api.py
------
FastAPI backend — Claude calls your 4 tools, returns answer to the user.

HOW IT WORKS:
    User types in the browser → hits this API → we call Claude API
    → Claude calls your Python tools → answer goes back to user

RUN IT:
    uvicorn api:app --reload --port 8000
"""

import os
import sys
import json
import anthropic
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.destination       import search_destination
from tools.weather_itinerary import build_itinerary
from tools.experiences       import find_experiences
from tools.budget            import estimate_budget

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI()

# ─────────────────────────────────────────────────────────────
# TOOL DEFINITIONS — Claude reads these to decide which to call
# Same logic as MCP but sent via the Anthropic API instead
# ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "destination_search",
        "description": "Search for Canadian travel destinations. Use when user asks about a specific Canadian city or place.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city":     {"type": "string",  "description": "City or destination name e.g. Banff, Tofino"},
                "month":    {"type": "integer", "description": "Month number 1-12 if user mentions a travel month"},
                "province": {"type": "string",  "description": "Province name if known"},
            },
            "required": ["city"]
        }
    },
    {
        "name": "weather_itinerary",
        "description": "Build a day-by-day travel itinerary for a Canadian destination based on weather.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city":         {"type": "string",  "description": "Destination city"},
                "days":         {"type": "integer", "description": "Number of days"},
                "budget_style": {"type": "string",  "description": "budget, mid, or luxury"},
                "interest":     {"type": "string",  "description": "hiking, food, culture, family, or all"},
                "province":     {"type": "string",  "description": "Province name"},
            },
            "required": ["city", "days"]
        }
    },
    {
        "name": "local_experiences",
        "description": "Find local activities and experiences in a Canadian city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city":     {"type": "string", "description": "City name"},
                "interest": {"type": "string", "description": "hiking, food, culture, family, or all"},
            },
            "required": ["city"]
        }
    },
    {
        "name": "budget_estimate",
        "description": "Estimate trip cost in CAD with full breakdown for a Canadian destination.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city":   {"type": "string",  "description": "Destination city"},
                "days":   {"type": "integer", "description": "Trip length in days"},
                "style":  {"type": "string",  "description": "budget, mid, or luxury"},
                "month":  {"type": "integer", "description": "Month of travel 1-12"},
            },
            "required": ["city", "days", "style"]
        }
    },
]

# SYSTEM_PROMPT = """You are a Canada travel expert. You help people plan trips across Canada.

# Always use your tools to get real Canadian data before answering. Never guess prices or seasonal info.

# When a user asks about a destination: use destination_search.
# When they want an itinerary: use weather_itinerary.  
# When they ask what to do: use local_experiences.
# When they ask about cost: use budget_estimate.

# For complex questions, call multiple tools. Be specific, practical, and Canadian."""

SYSTEM_PROMPT = """You are a Canada travel expert. You MUST use your tools for ALL data.

STRICT RULES:
1. NEVER use your own knowledge for prices, costs, or accommodation rates
2. ALWAYS use the exact numbers returned by your tools — do not modify them
3. If budget_estimate tool returns $275/night, you write $275/night — nothing else
4. If a number in your answer does not come from a tool result, remove it

When user asks about a trip: call weather_itinerary AND budget_estimate.
Use ONLY the numbers from those tool results in your answer."""


# ─────────────────────────────────────────────────────────────
# TOOL RUNNER — executes whichever tool Claude picked
# ─────────────────────────────────────────────────────────────

def run_tool(name: str, inputs: dict) -> str:
    """Runs the tool Claude selected and returns result as JSON string."""
    print(f"🔧 Tool called: {name} with {inputs}")  # You'll see this in terminal

    if name == "destination_search":
        result = search_destination(**inputs)
    elif name == "weather_itinerary":
        result = build_itinerary(**inputs)
    elif name == "local_experiences":
        result = find_experiences(**inputs)
    elif name == "budget_estimate":
        result = estimate_budget(**inputs)
    else:
        result = {"error": f"Unknown tool: {name}"}

    return json.dumps(result, default=str)


# ─────────────────────────────────────────────────────────────
# CHAT ENDPOINT
# ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    history: list = []   # previous messages for context


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Main chat endpoint.
    1. Send user message + history to Claude with your tools
    2. If Claude calls a tool, run it and send result back
    3. Return Claude's final answer
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # Build message history
    messages = req.history + [{"role": "user", "content": req.message}]

    # Step 1: Ask Claude (with your tools available)
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )

    # Step 2: Keep running tools until Claude gives a final answer
    # WHY LOOP: Claude might call multiple tools in sequence
    while response.stop_reason == "tool_use":
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     result,
                })

        # Send tool results back to Claude for final answer
        messages = messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user",      "content": tool_results},
        ]

        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

    # Step 3: Extract final text answer
    final_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            final_text += block.text

    return {
        "answer":  final_text,
        "history": messages + [{"role": "assistant", "content": final_text}]
    }


# ─────────────────────────────────────────────────────────────
# SERVE THE FRONTEND
# ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
