"""Turn the last DeepEval run into a short Markdown table.

    python evals/report.py                          # print it
    python evals/report.py >> $GITHUB_STEP_SUMMARY  # show it on the GitHub Actions run page
"""

import json
from pathlib import Path

RUN_FILE = Path(".deepeval/.latest_test_run.json")


def report(run_file: Path = RUN_FILE) -> str:
    if not run_file.exists():
        return "No eval results found. Did the evals run?"
    cases = json.loads(run_file.read_text())["testRunData"]["testCases"]
    lines = ["## Agent eval results", "", "| Case | Metric | Score | Threshold | Result |", "|---|---|---|---|---|"]
    for case in cases:
        for metric in case.get("metricsData", []):
            score = metric.get("score")
            score = "error" if score is None else f"{score:.2f}"
            result = "pass" if metric["success"] else "**FAIL**"
            lines.append(f"| {case['name']} | {metric['name']} | {score} | {metric['threshold']} | {result} |")
    passed = sum(case["success"] for case in cases)
    lines += ["", f"**{passed} of {len(cases)} cases passed.**"]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
