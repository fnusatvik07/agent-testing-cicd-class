"""Quality evals for the QuickBite agent. Run with: deepeval test run evals/

Every case in dataset.json runs the real agent, then DeepEval scores the run:
- Tool Correctness     (plain code): did it call the tools we expected, in the right order?
- Argument Correctness (LLM judge) : were the arguments it passed to each tool right?
- Task Completion      (LLM judge) : did it do what the customer asked?
- Answer Quality       (LLM judge) : our own criteria, written in plain English with GEval
If any metric scores below its threshold, the test fails, and so does CI.
"""

import pytest
from deepeval import assert_test

from agent import run_agent
from evals.harness import load_cases, metrics, orders_placed, to_test_case

CASES = load_cases()


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_agent(case):
    result = run_agent(case["request"])

    # A plain code check first: it is free, exact, and its failure message is easy to read.
    if case["expected_order"]:
        assert orders_placed(result) == [case["expected_order"]], f"Wrong order. Agent said: {result['answer']}"

    assert_test(to_test_case(case, result), metrics())
