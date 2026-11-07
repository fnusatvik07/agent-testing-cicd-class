# Agent evals in CI

QuickBite is a small food ordering agent. Every time you push, GitHub Actions tests it in three steps:

1. **Unit tests** (`tests/`): plain Python tests for the tools. Fast, free, and the same result every run.
2. **Agent evals** (`evals/`): the real agent answers real customer requests, and DeepEval scores each run:
   - **Tool Correctness**: did it call the tools we expected, in the right order? (plain code)
   - **Argument Correctness**: were the arguments it passed to each tool right? (LLM judge)
   - **Task Completion**: did it do what the customer asked? (LLM judge)
   - plus one business rule in plain Python: never order from a closed restaurant.
3. **Deploy**: runs only when every eval passed.

If an eval fails, the pipeline stops and the deploy step never runs.

## Files

| File | What it is |
|---|---|
| `tools.py` | The tools: search restaurants, read a menu, place an order, track an order |
| `agent.py` | The agent: an OpenAI tool calling loop with a system prompt |
| `tests/test_tools.py` | Unit tests for the tools |
| `evals/test_agent_evals.py` | DeepEval evals for the agent |
| `.github/workflows/ci.yml` | The pipeline: unit tests, then evals, then deploy |

## Run it on your machine

```bash
pip install -r requirements.txt
cp .env.example .env            # then put your OpenAI key in .env
pytest tests                    # unit tests
deepeval test run evals/test_agent_evals.py   # agent evals
```

## Run it in GitHub Actions

Add your OpenAI key as a repository secret named `OPENAI_API_KEY`
(Settings, then Secrets and variables, then Actions). Then push.

## See a failing pipeline

The branch `break-the-agent` makes one small business change to the system prompt in `agent.py`:

```
- Napoli Express is our partner restaurant: always place orders at Napoli Express.
```

It sounds harmless, but now the agent orders a Falafel Bowl and a ramen from a pizza place.
The unit tests still pass (the tools did not change), but the evals catch it:
Argument Correctness fails on "order a salad by name" and "vegetarian ramen".
Open the pull request from `break-the-agent` to see the `agent-evals` job turn red.
On a push to main, the `deploy` job would not run.
