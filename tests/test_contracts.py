"""Contract tests: the tool schemas the model sees must match the Python functions we actually run.

If someone renames a parameter in tools.py but forgets the schema, the model sends the old name and
every call fails at runtime. These tests catch that on the developer's laptop, for free.
"""

import inspect

import pytest

from agent import SYSTEM_PROMPT
from tools import RESTAURANTS, TOOL_SCHEMAS, TOOLS

SCHEMAS = {s["function"]["name"]: s["function"] for s in TOOL_SCHEMAS}


def test_every_tool_has_a_schema_and_every_schema_has_a_tool():
    assert set(SCHEMAS) == set(TOOLS)


@pytest.mark.parametrize("name", sorted(TOOLS))
def test_schema_parameters_match_the_function(name):
    function_params = set(inspect.signature(TOOLS[name]).parameters)
    schema = SCHEMAS[name]["parameters"]
    assert set(schema["properties"]) == function_params
    assert set(schema["required"]) == function_params


@pytest.mark.parametrize("name", sorted(TOOLS))
def test_every_tool_is_described_for_the_model(name):
    assert SCHEMAS[name]["description"].strip()
    assert all(p["description"].strip() for p in SCHEMAS[name]["parameters"]["properties"].values())


@pytest.mark.parametrize("cuisine", sorted({r["cuisine"] for r in RESTAURANTS.values()}))
def test_the_model_is_told_about_every_cuisine_we_serve(cuisine):
    assert cuisine in SYSTEM_PROMPT
    assert cuisine in SCHEMAS["search_restaurants"]["description"]
