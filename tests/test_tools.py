"""Unit tests for the tools. Plain Python, no AI, no API key: they give the same result every run."""

import json

from tools import get_menu, place_order, search_restaurants, track_order


def test_search_finds_both_pizza_places():
    names = [r["name"] for r in json.loads(search_restaurants("pizza"))]
    assert names == ["Napoli Express", "Slice House"]


def test_menu_has_prices():
    menu = json.loads(get_menu("Green Bowl"))["menu"]
    assert {"item": "Falafel Bowl", "price": 10.00, "vegetarian": True} in menu


def test_menu_says_when_a_restaurant_is_closed():
    assert json.loads(get_menu("Slice House"))["open"] is False


def test_closed_restaurant_cannot_take_orders():
    result = json.loads(place_order("Slice House", "Veggie Supreme"))
    assert result == {"error": "Slice House is closed"}


def test_open_restaurant_takes_orders():
    result = json.loads(place_order("Napoli Express", "Margherita Pizza"))
    assert result["order_id"] == "QB-2002"


def test_track_known_order():
    assert json.loads(track_order("QB-1001"))["status"].startswith("Out for delivery")
