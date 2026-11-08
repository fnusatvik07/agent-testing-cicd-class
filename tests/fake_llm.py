"""A fake OpenAI client for tests. It plays back a script of replies, so the agent loop runs with no API key."""

import json
from types import SimpleNamespace


def tool_call(name: str, call_id: str = "call_1", **args) -> SimpleNamespace:
    """One tool call, shaped like the ones the OpenAI API returns."""
    return SimpleNamespace(id=call_id, type="function", function=SimpleNamespace(name=name, arguments=json.dumps(args)))


def reply(content: str | None = None, tool_calls: list | None = None) -> SimpleNamespace:
    """One response from the model: either some text, or a list of tool calls."""
    message = SimpleNamespace(role="assistant", content=content, tool_calls=tool_calls)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeLLM:
    """Use it like OpenAI(): fake.chat.completions.create(...). Every call returns the next scripted reply."""

    def __init__(self, replies: list):
        self.replies = list(replies)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **request):
        self.requests.append({**request, "messages": list(request["messages"])})
        if not self.replies:
            raise AssertionError("The agent called the model more times than the script expected")
        return self.replies.pop(0)
