# Testing AI agents and shipping them with CI/CD

A hands-on class. We take a small food ordering agent and give it everything it needs before it ships:
unit tests, contract tests, tests for the agent loop with a fake model, evals with DeepEval,
and a GitHub Actions pipeline that runs all of it on every push and only deploys if everything passes.

## What you will learn

- Why `assert answer == "..."` breaks on agents, and what to do instead.
- How to test the parts of an agent that **are** deterministic: tools, schemas, the agent loop.
- How to make an agent testable with a fake model, so most tests need no API key.
- How to write evals with DeepEval: Tool Correctness, Argument Correctness, Task Completion, and your own GEval criteria.
- How to build an eval dataset, write business rules and safety checks, and debug an eval that is wrong.
- How to write a CI/CD pipeline for an agent: stages, gates, secrets, reports, nightly runs, and deploys.

## The class, notebook by notebook

| # | Notebook | What happens | Time |
|---|----------|--------------|------|
| 1 | [Meet the agent](01_meet_the_agent.ipynb) | We run the agent, see that it never answers the same way twice, and map what can go wrong. | about 15 min |
| 2 | [Unit and contract tests](02_unit_and_contract_tests.ipynb) | We test the tools, find a real bug, and keep the model's view of the tools in sync with the code. | about 15 min |
| 3 | [Testing the agent loop](03_testing_the_agent_loop.ipynb) | We swap the real model for a fake one and test crashes, bad tool calls and endless loops, for free. | about 15 min |
| 4 | [Evals with DeepEval](04_evals_with_deepeval.ipynb) | We score real runs with code metrics and LLM judges, and write our own criteria with GEval. | about 20 min |
| 5 | [Building an eval suite](05_building_an_eval_suite.ipynb) | A dataset, business rules, a prompt injection bug the evals caught, and three bugs that were in the evals. | about 20 min |
| 6 | [The CI/CD pipeline](06_ci_cd_pipeline.ipynb) | We read `ci.yml` piece by piece, run it locally, and watch a pull request turn red. | about 20 min |

Open them in order. Each one builds on the last. Every notebook ends with exercises.

## The pipeline

```
 push or pull request
          |
   +------+------+
   |             |
  lint         tests          free, seconds, no API key
   |             |
   +------+------+
          |
     agent-evals              real agent + DeepEval, about a minute, about $0.09
          |
       deploy                 only on main, only if every eval passed
```

It also runs every night, because the model behind the API can change even when the code does not.

## The testing layers

| Layer | File | Needs an API key? | What it catches |
|---|---|---|---|
| Lint | `ruff.toml` | no | Typos, unused imports, obvious bugs |
| Unit tests | `tests/test_tools.py` | no | Bugs in the tools |
| Contract tests | `tests/test_contracts.py` | no | Tool schemas or prompt drifting away from the code |
| Agent loop tests | `tests/test_agent_loop.py` | no | Crashes on bad tool calls, endless loops |
| Business rule evals | `evals/test_business_rules.py` | yes | Ordering from a closed restaurant, prompt injection |
| Quality evals | `evals/test_agent_evals.py` | yes | Wrong tools, wrong arguments, unfinished tasks, bad answers |

## Files

| File | What it is |
|---|---|
| `tools.py` | The tools: search restaurants, read a menu, place an order, track an order |
| `agent.py` | The agent: an OpenAI tool calling loop with a system prompt |
| `tests/fake_llm.py` | A fake OpenAI client that plays back a script, for tests |
| `evals/dataset.json` | The eval cases. Add a case here, no Python needed |
| `evals/harness.py` | Turns agent runs into DeepEval test cases, and defines the metrics and the judge |
| `evals/report.py` | Turns the last eval run into a Markdown table (used on the GitHub run page) |
| `.github/workflows/ci.yml` | The pipeline |
| `Makefile` | The same commands CI runs, for your laptop |

## Quick start

```bash
git clone https://github.com/fnusatvik07/agent-testing-cicd-class.git
cd agent-testing-cicd-class

python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env        # then put your OpenAI key in .env

make lint test              # free: lint, unit, contract and loop tests
make evals                  # costs about $0.09: runs the real agent and scores it
jupyter lab                 # open the notebooks
```

> **Cost note.** The agent uses `gpt-4.1-mini` and the DeepEval judge uses `gpt-5.4`.
> One full eval run costs about $0.09. Running all six notebooks costs about $0.25.

## Run it in GitHub Actions

1. Push the repo to GitHub.
2. Add your OpenAI key as a repository secret named `OPENAI_API_KEY`
   (**Settings**, then **Secrets and variables**, then **Actions**, or `gh secret set OPENAI_API_KEY`).
3. Push again, or click **Run workflow** on the Actions tab.
4. To make a red pipeline block merges, protect `main` and require the `lint`, `tests` and `agent-evals` checks.

## See a failing pipeline

The branch `break-the-agent` changes one line of the system prompt:

```
- Napoli Express is our partner restaurant: always place orders at Napoli Express.
```

It sounds like a harmless business decision. Open its pull request and look at the checks:
lint passes, the tests pass (the tools did not change), but the evals fail, because the agent now
tries to order a Falafel Bowl and a ramen from a pizza place. The deploy never runs.
