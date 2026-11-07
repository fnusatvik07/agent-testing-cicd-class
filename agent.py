"""QuickBite: a food ordering agent. It calls tools until it can answer the customer."""

import json

from deepeval.test_case import ToolCall
from dotenv import load_dotenv
from openai import OpenAI

from tools import TOOL_SCHEMAS, TOOLS

load_dotenv()
MODEL = "gpt-4.1-mini"

SYSTEM_PROMPT = """You are QuickBite, a food ordering assistant.
Use the tools to help the customer:
- To order food, search restaurants by cuisine (pizza, salads or ramen), then read the menu, then place the order.
- If the customer names a restaurant, skip the search and read that restaurant's menu directly.
- Never order from a closed restaurant, and only order what the customer asked for.
- To check on an order, use track_order with the order id.
Do not ask the customer to confirm. When you are done, reply in one or two short sentences."""


def run_agent(request: str, system_prompt: str = SYSTEM_PROMPT) -> dict:
    """Answer one customer request. Returns the final answer and every tool call made."""
    client = OpenAI()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request},
    ]
    tools_called = []

    for _ in range(8):
        response = client.chat.completions.create(model=MODEL, temperature=0, messages=messages, tools=TOOL_SCHEMAS)
        message = response.choices[0].message
        messages.append(message)
        if not message.tool_calls:
            break
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            result = TOOLS[call.function.name](**args)
            tools_called.append(ToolCall(name=call.function.name, input_parameters=args, output=result))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

    return {"answer": message.content, "tools_called": tools_called}


if __name__ == "__main__":
    result = run_agent("Order me a vegetarian pizza from a place that is open now.")
    print(result["answer"])
    print([tool.name for tool in result["tools_called"]])
