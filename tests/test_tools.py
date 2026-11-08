"""Unit tests for the tools. Plain Python, no AI, no API key: they give the same result every run."""

import json

import pytest

from tools import get_menu, place_order, search_restaurants, track_order


def test_search_finds_both_pizza_places():
    names = [r["name"] for r in json.loads(search_restaurants("pizza"))]
    assert names == ["Napoli Express", "Slice House"]


@pytest.mark.parametrize("cuisine", ["Pizza", "PIZZA", " pizza "])
def test_search_ignores_case_and_spaces(cuisine):
    assert len(json.loads(search_restaurants(cuisine))) == 2


def test_search_for_a_cuisine_we_do_not_serve_finds_nothing():
    assert json.loads(search_restaurants("sushi")) == []


def test_menu_has_prices():
    menu = json.loads(get_menu("Green Bowl"))["menu"]
    assert {"item": "Falafel Bowl", "price": 10.00, "vegetarian": True} in menu


def test_menu_says_when_a_restaurant_is_closed():
    assert json.loads(get_menu("Slice House"))["open"] is False


def test_menu_of_an_unknown_restaurant_is_empty():
    assert json.loads(get_menu("Burger Barn")) == {"restaurant": "Burger Barn", "open": False, "menu": []}


def test_open_restaurant_takes_orders():
    result = json.loads(place_order("Napoli Express", "Margherita Pizza"))
    assert result == {"order_id": "QB-2002", "restaurant": "Napoli Express", "item": "Margherita Pizza"}


@pytest.mark.parametrize(
    "restaurant, item, error",
    [
        ("Slice House", "Veggie Supreme", "Slice House is closed"),
        ("Burger Barn", "Cheeseburger", "Unknown restaurant: Burger Barn"),
        ("Napoli Express", "Falafel Bowl", "Falafel Bowl is not on the menu at Napoli Express"),
    ],
)
def test_bad_orders_are_refused(restaurant, item, error):
    assert json.loads(place_order(restaurant, item)) == {"error": error}


def test_track_known_order():
    assert json.loads(track_order("QB-1001"))["status"].startswith("Out for delivery")


def test_track_unknown_order():
    assert json.loads(track_order("QB-9999"))["status"] == "Order not found"
