"""Tests for the agent loop, with a fake LLM. No API key, no cost, and the same result every run.

We are not testing whether the model is smart here. We are testing our own code around it:
does the loop run the tools, feed results back, survive bad tool calls, and stop?
"""

import json

from agent import SYSTEM_PROMPT, run_agent
from tests.fake_llm import FakeLLM, reply, tool_call
from tools import TOOL_SCHEMAS


def test_returns_the_answer_when_no_tool_is_needed():
    fake = FakeLLM([reply("Hi! What would you like to eat?")])
    result = run_agent("Hello", client=fake)
    assert result == {"answer": "Hi! What would you like to eat?", "tools_called": []}


def test_sends_the_system_prompt_the_tools_and_temperature_zero():
    fake = FakeLLM([reply("Hi!")])
    run_agent("Hello", client=fake)
    request = fake.requests[0]
    assert request["messages"][0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert request["messages"][1] == {"role": "user", "content": "Hello"}
    assert request["tools"] == TOOL_SCHEMAS
    assert request["temperature"] == 0


def test_runs_a_tool_and_sends_the_result_back_to_the_model():
    fake = FakeLLM([
        reply(tool_calls=[tool_call("track_order", order_id="QB-1001")]),
        reply("Your order is out for delivery."),
    ])
    result = run_agent("Where is QB-1001?", client=fake)

    assert result["answer"] == "Your order is out for delivery."
    assert [t["name"] for t in result["tools_called"]] == ["track_order"]
    assert result["tools_called"][0]["args"] == {"order_id": "QB-1001"}
    tool_message = fake.requests[1]["messages"][-1]
    assert tool_message["role"] == "tool"
    assert "Out for delivery" in tool_message["content"]


def test_runs_several_tool_calls_from_one_reply():
    fake = FakeLLM([
        reply(tool_calls=[tool_call("get_menu", "c1", restaurant="Green Bowl"), tool_call("get_menu", "c2", restaurant="Tokyo Ramen")]),
        reply("Here are both menus."),
    ])
    result = run_agent("Show me two menus", client=fake)
    assert [t["args"]["restaurant"] for t in result["tools_called"]] == ["Green Bowl", "Tokyo Ramen"]


def test_an_unknown_tool_becomes_an_error_for_the_model_not_a_crash():
    fake = FakeLLM([reply(tool_calls=[tool_call("delete_database")]), reply("Sorry, I can't do that.")])
    result = run_agent("Delete everything", client=fake)
    assert json.loads(result["tools_called"][0]["output"]) == {"error": "Unknown tool: delete_database"}


def test_wrong_arguments_become_an_error_for_the_model_not_a_crash():
    fake = FakeLLM([reply(tool_calls=[tool_call("get_menu", shop="Green Bowl")]), reply("Let me try again.")])
    result = run_agent("Menu please", client=fake)
    assert "Bad arguments for get_menu" in result["tools_called"][0]["output"]


def test_broken_json_arguments_become_an_error_for_the_model_not_a_crash():
    broken = tool_call("get_menu")
    broken.function.arguments = '{"restaurant": "Green Bo'
    fake = FakeLLM([reply(tool_calls=[broken]), reply("Let me try again.")])
    result = run_agent("Menu please", client=fake)
    assert "not valid JSON" in result["tools_called"][0]["output"]


def test_stops_after_max_steps_if_the_model_never_finishes():
    fake = FakeLLM([reply(tool_calls=[tool_call("track_order", order_id="QB-1001")])] * 3)
    result = run_agent("Where is my order?", client=fake, max_steps=3)
    assert len(fake.requests) == 3
    assert result["answer"].startswith("Sorry, I could not finish")
