"""Shared pieces for the evals: the dataset, the judge model, and the metrics.

The agent returns plain dicts. Only this file knows about DeepEval, so the agent never depends on our test tools.
"""

import json
import os
from pathlib import Path

from deepeval.metrics import ArgumentCorrectnessMetric, GEval, TaskCompletionMetric, ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, SingleTurnParams, ToolCall

# Pin the judge. If the judge model changes, your scores change, even when the agent did not.
JUDGE_MODEL = os.getenv("EVAL_JUDGE_MODEL", "gpt-5.4")

DATASET = Path(__file__).parent / "dataset.json"


def load_cases() -> list[dict]:
    return json.loads(DATASET.read_text())


def to_test_case(case: dict, result: dict) -> LLMTestCase:
    """Turn one agent run into a DeepEval test case."""
    return LLMTestCase(
        name=case["id"],
        input=case["request"],
        actual_output=result["answer"],
        tools_called=[ToolCall(name=t["name"], input_parameters=t["args"], output=t["output"]) for t in result["tools_called"]],
        expected_tools=[ToolCall(name=name) for name in case["expected_tools"]],
    )


def answer_quality() -> GEval:
    """A judge with our own criteria, written in plain English."""
    return GEval(
        name="Answer Quality",
        criteria=(
            "The reply tells the customer clearly what happened: what was ordered and where, "
            "or the status of their order, or why it could not be done. "
            "Every fact in the reply must match the tool results. "
            "It is one or two short sentences. "
            "It must not ask permission before acting (for example 'Shall I place the order?'), "
            "but suggesting a next step is fine."
        ),
        # Give the judge the evidence. Without the tool calls it cannot know the restaurant names are real.
        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.TOOLS_CALLED],
        model=JUDGE_MODEL,
        threshold=0.7,
    )


def metrics() -> list:
    return [
        ToolCorrectnessMetric(threshold=1.0, should_consider_ordering=True),
        ArgumentCorrectnessMetric(threshold=0.8, model=JUDGE_MODEL),
        TaskCompletionMetric(threshold=0.7, model=JUDGE_MODEL),
        answer_quality(),
    ]


def orders_placed(result: dict) -> list[dict]:
    """Every order the agent actually placed (successful place_order calls only)."""
    return [t["args"] for t in result["tools_called"] if t["name"] == "place_order" and "order_id" in t["output"]]
