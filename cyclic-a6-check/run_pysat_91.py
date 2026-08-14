#!/usr/bin/env python3
"""Resume the 91-case checkpoint with a bounded PySAT backend subprocess."""

from __future__ import annotations

from argparse import ArgumentParser
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
from time import perf_counter


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--solver", default="maplesat")
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--checkpoint", type=Path, default=Path("artifacts/external_91_cadical.checkpoint.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/results_91_portfolio.json"))
    parser.add_argument("--cases-dir", type=Path, default=Path("artifacts/cases"))
    args = parser.parse_args()

    completed: dict[tuple[int, int], dict[str, object]] = {}
    if args.checkpoint.exists():
        for line in args.checkpoint.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            completed[(record["u"], record["w"])] = record
    cases = list(combinations(range(1, 15), 2))
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    started_all = perf_counter()

    for index, (u, w) in enumerate(cases, 1):
        cached = completed.get((u, w))
        if cached and cached["status"] in {"SAT", "UNSAT"}:
            print(f"[{index:02d}/91] ({u:02d},{w:02d}) cached {cached['status']}", flush=True)
            continue
        case_path = args.cases_dir / f"u{u:02d}_w{w:02d}.cnf"
        command = [
            str(args.python.resolve()),
            "solve_one_pysat.py",
            str(case_path.resolve()),
            "--solver",
            args.solver,
        ]
        started = perf_counter()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout)
            runtime = perf_counter() - started
            if process.returncode == 0:
                record = json.loads(process.stdout)
                record.update({"center": 0, "u": u, "w": w, "bounded_wall_seconds": runtime})
            else:
                record = {
                    "center": 0,
                    "u": u,
                    "w": w,
                    "solver": args.solver,
                    "status": "ERROR",
                    "bounded_wall_seconds": runtime,
                    "returncode": process.returncode,
                    "stdout": process.stdout[-2000:],
                    "stderr": process.stderr[-2000:],
                }
        except subprocess.TimeoutExpired:
            record = {
                "center": 0,
                "u": u,
                "w": w,
                "solver": args.solver,
                "status": "TIMEOUT",
                "bounded_wall_seconds": perf_counter() - started,
            }
        record["case_cnf"] = str(case_path.resolve())
        record["case_cnf_sha256"] = sha256(case_path.read_bytes()).hexdigest()
        completed[(u, w)] = record
        with args.checkpoint.open("a", encoding="utf-8") as checkpoint:
            checkpoint.write(json.dumps(record, sort_keys=True) + "\n")
        print(
            f"[{index:02d}/91] ({u:02d},{w:02d}) {record['status']} "
            f"{record['bounded_wall_seconds']:.3f}s",
            flush=True,
        )

    records = [completed[pair] for pair in cases]
    summary = {
        "schema_version": 1,
        "case_count": len(records),
        "sat_count": sum(r["status"] == "SAT" for r in records),
        "unsat_count": sum(r["status"] == "UNSAT" for r in records),
        "timeout_count": sum(r["status"] == "TIMEOUT" for r in records),
        "error_count": sum(r["status"] == "ERROR" for r in records),
        "portfolio_last_solver": args.solver,
        "runner_wall_runtime_seconds": perf_counter() - started_all,
        "cases": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("case_count", "sat_count", "unsat_count", "timeout_count", "error_count")}, indent=2))
    if summary["sat_count"] or summary["timeout_count"] or summary["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

