"""The tools our QuickBite agent can use, and the data behind them."""

import json

RESTAURANTS = {
    "Napoli Express": {"cuisine": "pizza", "open": True},
    "Slice House": {"cuisine": "pizza", "open": False},
    "Green Bowl": {"cuisine": "salads", "open": True},
    "Tokyo Ramen": {"cuisine": "ramen", "open": True},
}

MENUS = {
    "Napoli Express": [
        {"item": "Margherita Pizza", "price": 12.50, "vegetarian": True},
        {"item": "Pepperoni Pizza", "price": 14.00, "vegetarian": False},
    ],
    "Slice House": [{"item": "Veggie Supreme", "price": 11.00, "vegetarian": True}],
    "Green Bowl": [
        {"item": "Caesar Salad", "price": 9.50, "vegetarian": False},
        {"item": "Falafel Bowl", "price": 10.00, "vegetarian": True},
    ],
    "Tokyo Ramen": [
        {"item": "Tonkotsu Ramen", "price": 15.00, "vegetarian": False},
        {"item": "Miso Veggie Ramen", "price": 13.50, "vegetarian": True},
    ],
}

ORDERS = {"QB-1001": "Out for delivery, arriving in 10 minutes"}


def search_restaurants(cuisine: str) -> str:
    """Find restaurants that serve a cuisine, and whether they are open now."""
    found = [{"name": name, **info} for name, info in RESTAURANTS.items() if info["cuisine"] == cuisine.strip().lower()]
    return json.dumps(found)


def get_menu(restaurant: str) -> str:
    """Return whether a restaurant is open now, and its menu."""
    is_open = RESTAURANTS.get(restaurant, {}).get("open", False)
    return json.dumps({"restaurant": restaurant, "open": is_open, "menu": MENUS.get(restaurant, [])})


def place_order(restaurant: str, item: str) -> str:
    """Place an order. Closed restaurants cannot take orders, and you can only order what is on the menu."""
    if restaurant not in RESTAURANTS:
        return json.dumps({"error": f"Unknown restaurant: {restaurant}"})
    if not RESTAURANTS[restaurant]["open"]:
        return json.dumps({"error": f"{restaurant} is closed"})
    if item not in [dish["item"] for dish in MENUS[restaurant]]:
        return json.dumps({"error": f"{item} is not on the menu at {restaurant}"})
    return json.dumps({"order_id": "QB-2002", "restaurant": restaurant, "item": item})


def track_order(order_id: str) -> str:
    """Return the delivery status of an order."""
    return json.dumps({"order_id": order_id, "status": ORDERS.get(order_id, "Order not found")})


TOOLS = {
    "search_restaurants": search_restaurants,
    "get_menu": get_menu,
    "place_order": place_order,
    "track_order": track_order,
}


def schema(name, description, **params):
    """Describe one tool to the OpenAI API. Every parameter is a string."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {p: {"type": "string", "description": d} for p, d in params.items()},
                "required": list(params),
            },
        },
    }


TOOL_SCHEMAS = [
    schema("search_restaurants", "Find restaurants for a cuisine (pizza, salads, ramen).", cuisine="The cuisine"),
    schema("get_menu", "Get whether a restaurant is open now, and its menu with prices.", restaurant="Exact restaurant name"),
    schema("place_order", "Order one item at one restaurant.", restaurant="Exact restaurant name", item="Exact menu item"),
    schema("track_order", "Get the delivery status of an order.", order_id="The order id, for example QB-1001"),
]
