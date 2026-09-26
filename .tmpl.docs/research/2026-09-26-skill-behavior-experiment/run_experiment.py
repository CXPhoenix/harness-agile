#!/usr/bin/env python3
"""Experiment harness: baseline vs. patched skills, s3 and s4 scenarios.

Python 3 standard library only. See SPEC.md in this directory for the
full specification this file implements.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

EXP_ROOT = Path(__file__).resolve().parent
FIXTURE_DIR = EXP_ROOT / "fixture"
PROMPTS_DIR = EXP_ROOT / "prompts"
RUNS_DIR = EXP_ROOT / "runs"
RESULTS_CSV = EXP_ROOT / "results.csv"
SUMMARY_JSON = EXP_ROOT / "summary.json"

BASELINE_SKILLS_ROOT = Path(
    "/Users/phoenix/dev/edu-projects/harness-agile-template/.claude/skills"
)
PATCHED_SKILLS_ROOT = Path(
    "/private/tmp/claude-501/-Users-phoenix-dev-edu-projects-harness-agile-template"
    "/10458df1-fb73-44a4-804a-3b27b3c08dbf/scratchpad/audit4/.claude/skills"
)
ROLE_FILE = Path(
    "/Users/phoenix/dev/edu-projects/harness-agile-template/.claude/agents/harness-researcher.md"
)

# scenario -> (prompt file, skill name)
SCENARIOS = {
    "s3": ("s3.txt", "research"),
    "s4": ("s4.txt", "grilling"),
}
CONDITIONS = ("baseline", "patched")

WALL_CLOCK_TIMEOUT_S = 900


def skill_source(condition: str, skill: str) -> Path:
    root = BASELINE_SKILLS_ROOT if condition == "baseline" else PATCHED_SKILLS_ROOT
    return root / skill / "SKILL.md"


def trial_dir(scenario: str, condition: str, n: int) -> Path:
    return RUNS_DIR / scenario / condition / str(n)


def run_git(cwd: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def build_trial_dir(scenario: str, condition: str, n: int, skill: str) -> Path:
    """Step 1: build one trial directory and commit its base state."""
    dest = trial_dir(scenario, condition, n)
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FIXTURE_DIR, dest)

    skill_dest_dir = dest / ".claude" / "skills" / skill
    skill_dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(skill_source(condition, skill), skill_dest_dir / "SKILL.md")

    agents_dest_dir = dest / ".claude" / "agents"
    agents_dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROLE_FILE, agents_dest_dir / "harness-researcher.md")

    run_git(dest, ["init", "-q"])
    run_git(dest, ["add", "-A"])
    run_git(
        dest,
        [
            "-c",
            "user.name=exp",
            "-c",
            "user.email=exp@example.invalid",
            "commit",
            "-q",
            "-m",
            "base",
        ],
    )
    return dest


def build_command(prompt_text: str, claude_bin: str) -> list[str]:
    """Step 2: build the argv for the claude invocation (no shell)."""
    return [
        claude_bin,
        "-p",
        prompt_text,
        "--model",
        "claude-opus-5-5",
        "--effort",
        "high",
        "--output-format",
        "stream-json",
        "--verbose",
        "--disable-slash-commands",
        "--no-session-persistence",
        "--max-budget-usd",
        "3",
        "--allowedTools",
        "Read",
        "Write",
        "Edit",
        "Glob",
        "Grep",
        "WebFetch",
        "WebSearch",
        "Agent",
        "Task",
    ]


def parse_transcript(transcript_path: Path) -> dict:
    """Step 3: derive cost_usd, top_level_spawns, web_calls from transcript.jsonl."""
    cost_usd = 0.0
    top_level_spawns = 0
    web_calls = 0

    if not transcript_path.exists():
        return {
            "cost_usd": cost_usd,
            "top_level_spawns": top_level_spawns,
            "web_calls": web_calls,
        }

    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            obj_type = obj.get("type")

            if obj_type == "result":
                if "total_cost_usd" in obj and obj["total_cost_usd"] is not None:
                    cost_usd = obj["total_cost_usd"]

            if obj_type == "assistant":
                parent_tool_use_id = obj.get("parent_tool_use_id")
                if parent_tool_use_id:
                    continue
                message = obj.get("message", {})
                content = message.get("content", []) if isinstance(message, dict) else []
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_use":
                        continue
                    name = block.get("name")
                    if name in ("Agent", "Task"):
                        top_level_spawns += 1
                    elif name in ("WebFetch", "WebSearch"):
                        web_calls += 1

    return {
        "cost_usd": cost_usd,
        "top_level_spawns": top_level_spawns,
        "web_calls": web_calls,
    }


def git_changed_paths(dest: Path) -> list[str]:
    result = run_git(dest, ["status", "--porcelain", "--untracked-files=all"])
    paths = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        # porcelain format: XY <path> (may contain rename "old -> new")
        path_part = line[3:]
        if " -> " in path_part:
            path_part = path_part.split(" -> ", 1)[1]
        paths.append(path_part)
    return paths


def product_changes(changed_paths: list[str]) -> list[str]:
    result = []
    for p in changed_paths:
        if p.startswith(".claude/") or p in ("transcript.jsonl", "stderr.txt"):
            continue
        if p.endswith(".md"):
            continue
        result.append(p)
    return result


def run_trial(
    scenario: str,
    condition: str,
    n: int,
    skill: str,
    prompt_text: str,
    dry_run: bool,
    claude_bin: str | None,
) -> dict:
    dest = build_trial_dir(scenario, condition, n, skill)
    command = build_command(prompt_text, claude_bin or "claude")

    row = {
        "scenario": scenario,
        "condition": condition,
        "trial": n,
        "status": None,
        "cost_usd": 0.0,
        "top_level_spawns": 0,
        "web_calls": 0,
        "product_changes": 0,
        "changed_paths": [],
    }

    if dry_run:
        print(f"[dry-run] {scenario}/{condition}/{n}: {' '.join(_quote(a) for a in command)}")
        row["status"] = "ok"
        return row

    transcript_path = dest / "transcript.jsonl"
    stderr_path = dest / "stderr.txt"

    status = "ok"
    try:
        with open(transcript_path, "w", encoding="utf-8") as out, open(
            stderr_path, "w", encoding="utf-8"
        ) as err:
            proc = subprocess.run(
                command,
                cwd=dest,
                stdout=out,
                stderr=err,
                timeout=WALL_CLOCK_TIMEOUT_S,
            )
        if proc.returncode != 0:
            status = "error"
    except subprocess.TimeoutExpired:
        status = "timeout"

    metrics = parse_transcript(transcript_path)
    changed_paths = git_changed_paths(dest)
    prod_changes = product_changes(changed_paths)

    row.update(
        {
            "status": status,
            "cost_usd": metrics["cost_usd"],
            "top_level_spawns": metrics["top_level_spawns"],
            "web_calls": metrics["web_calls"],
            "product_changes": len(prod_changes),
            "changed_paths": changed_paths,
        }
    )
    return row


def _quote(arg: str) -> str:
    if " " in arg or "\n" in arg:
        return json.dumps(arg)
    return arg


def write_results_row(row: dict) -> None:
    is_new = not RESULTS_CSV.exists()
    with open(RESULTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(
                [
                    "scenario",
                    "condition",
                    "trial",
                    "status",
                    "cost_usd",
                    "top_level_spawns",
                    "web_calls",
                    "product_changes",
                    "changed_paths",
                ]
            )
        writer.writerow(
            [
                row["scenario"],
                row["condition"],
                row["trial"],
                row["status"],
                row["cost_usd"],
                row["top_level_spawns"],
                row["web_calls"],
                row["product_changes"],
                ";".join(row["changed_paths"]),
            ]
        )


def write_summary(all_rows: list[dict]) -> None:
    summary: dict = {"totals": {"trials": len(all_rows), "cost_usd": 0.0}, "by_scenario_condition": {}}
    for row in all_rows:
        summary["totals"]["cost_usd"] += row["cost_usd"]
        key = f"{row['scenario']}/{row['condition']}"
        bucket = summary["by_scenario_condition"].setdefault(
            key,
            {
                "trials": 0,
                "ok": 0,
                "timeout": 0,
                "error": 0,
                "budget_stop": 0,
                "cost_usd": 0.0,
                "top_level_spawns_sum": 0,
                "web_calls_sum": 0,
                "product_changes_sum": 0,
            },
        )
        bucket["trials"] += 1
        bucket[row["status"]] = bucket.get(row["status"], 0) + 1
        bucket["cost_usd"] += row["cost_usd"]
        bucket["top_level_spawns_sum"] += row["top_level_spawns"]
        bucket["web_calls_sum"] += row["web_calls"]
        bucket["product_changes_sum"] += row["product_changes"]

    with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scenarios", default="s3,s4")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--budget-usd", type=float, default=40.0)
    args = parser.parse_args()

    scenarios = [s.strip() for s in args.scenarios.split(",") if s.strip()]
    for s in scenarios:
        if s not in SCENARIOS:
            print(f"Unknown scenario: {s}", file=sys.stderr)
            return 2

    claude_bin = shutil.which("claude")
    if not args.dry_run and not claude_bin:
        print("claude binary not found on PATH (shutil.which('claude'))", file=sys.stderr)
        return 2

    # Build the interleaved job list: (scenario, condition, trial) for
    # trial=1..N, interleaving conditions within each scenario: b1, p1, b2, p2, ...
    jobs: list[tuple[str, str, int]] = []
    for scenario in scenarios:
        for n in range(1, args.trials + 1):
            for condition in CONDITIONS:
                jobs.append((scenario, condition, n))

    budget_lock = threading.Lock()
    running_cost = {"total": 0.0}
    budget_exhausted = {"flag": False}

    all_rows: list[dict] = []
    rows_lock = threading.Lock()

    def worker(job: tuple[str, str, int]) -> None:
        scenario, condition, n = job
        prompt_file, skill = SCENARIOS[scenario]
        prompt_text = (PROMPTS_DIR / prompt_file).read_text(encoding="utf-8")

        with budget_lock:
            if budget_exhausted["flag"]:
                row = {
                    "scenario": scenario,
                    "condition": condition,
                    "trial": n,
                    "status": "budget_stop",
                    "cost_usd": 0.0,
                    "top_level_spawns": 0,
                    "web_calls": 0,
                    "product_changes": 0,
                    "changed_paths": [],
                }
                with rows_lock:
                    all_rows.append(row)
                    write_results_row(row)
                return

        row = run_trial(scenario, condition, n, skill, prompt_text, args.dry_run, claude_bin)

        with budget_lock:
            running_cost["total"] += row["cost_usd"]
            if running_cost["total"] >= args.budget_usd:
                budget_exhausted["flag"] = True

        with rows_lock:
            all_rows.append(row)
            write_results_row(row)

    if RESULTS_CSV.exists():
        RESULTS_CSV.unlink()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        list(pool.map(worker, jobs))

    write_summary(all_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
