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

Make the agent worse and push. For example, in `agent.py` remove the line
`- If the customer names a restaurant, skip the search and read that restaurant's menu directly.`
The eval "order a salad by name" fails: the agent searches for the cuisine "falafel", finds nothing, and never orders.
The `agent-evals` job turns red, and `deploy` does not run.
