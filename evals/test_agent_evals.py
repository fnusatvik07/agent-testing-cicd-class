"""Evals for the QuickBite agent. Run with: deepeval test run evals/test_agent_evals.py

Every test case runs the real agent, then checks it with DeepEval metrics:
- Tool Correctness     (plain code): did it call the tools we expected, in the right order?
- Argument Correctness (LLM judge) : were the arguments it passed to each tool right?
- Task Completion      (LLM judge) : did it do what the customer asked?
If any metric scores below its threshold, the test fails, and so does CI.
"""

import pytest
from deepeval import assert_test
from deepeval.metrics import ArgumentCorrectnessMetric, TaskCompletionMetric, ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

from agent import run_agent

CASES = [
    {
        "name": "order a vegetarian pizza",
        "request": "Order me a vegetarian pizza from a place that is open now.",
        "expected_tools": ["search_restaurants", "get_menu", "place_order"],
    },
    {
        "name": "track an order",
        "request": "Where is my order QB-1001?",
        "expected_tools": ["track_order"],
    },
    {
        "name": "order a salad by name",
        "request": "I'd like a Falafel Bowl from Green Bowl, please.",
        "expected_tools": ["get_menu", "place_order"],
    },
    {
        "name": "vegetarian ramen",
        "request": "I'm vegetarian. Order me a ramen.",
        "expected_tools": ["search_restaurants", "get_menu", "place_order"],
    },
]


def metrics():
    return [
        ToolCorrectnessMetric(threshold=1.0, should_consider_ordering=True),
        ArgumentCorrectnessMetric(threshold=0.8),
        TaskCompletionMetric(threshold=0.7),
    ]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_agent(case):
    result = run_agent(case["request"])
    test_case = LLMTestCase(
        input=case["request"],
        actual_output=result["answer"],
        tools_called=result["tools_called"],
        expected_tools=[ToolCall(name=name) for name in case["expected_tools"]],
    )
    assert_test(test_case, metrics())


def test_never_orders_from_a_closed_restaurant():
    """A business rule, checked with plain Python: Slice House is closed, so the agent must not order there."""
    result = run_agent("Order me a Veggie Supreme from Slice House.")
    orders = [t for t in result["tools_called"] if t.name == "place_order"]
    assert all(t.input_parameters["restaurant"] != "Slice House" for t in orders)
