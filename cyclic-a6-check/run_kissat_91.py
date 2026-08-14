#!/usr/bin/env python3
"""Resume the 91-case checkpoint with the maintained Windows Kissat port."""

from __future__ import annotations

from argparse import ArgumentParser
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
from time import perf_counter

from cyclic_a6 import parse_kissat_model, validate_coloring


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--solver", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--checkpoint", type=Path, default=Path("artifacts/external_91_cadical.checkpoint.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/results_91_portfolio.json"))
    parser.add_argument("--cases-dir", type=Path, default=Path("artifacts/cases"))
    parser.add_argument("--models-dir", type=Path, default=Path("artifacts/models"))
    args = parser.parse_args()

    solver = args.solver.resolve()
    completed: dict[tuple[int, int], dict[str, object]] = {}
    if args.checkpoint.exists():
        for line in args.checkpoint.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            completed[(record["u"], record["w"])] = record
    cases = list(combinations(range(1, 15), 2))
    args.models_dir.mkdir(parents=True, exist_ok=True)
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    started_all = perf_counter()

    for index, (u, w) in enumerate(cases, 1):
        cached = completed.get((u, w))
        if cached and cached["status"] in {"SAT", "UNSAT"}:
            print(f"[{index:02d}/91] ({u:02d},{w:02d}) cached {cached['status']}", flush=True)
            continue
        case_path = args.cases_dir / f"u{u:02d}_w{w:02d}.cnf"
        command = [str(solver), "--unsat", "-q", "-n", str(case_path.resolve())]
        started = perf_counter()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout)
            runtime = perf_counter() - started
            status = {10: "SAT", 20: "UNSAT"}.get(process.returncode, "ERROR")
            record: dict[str, object] = {
                "center": 0,
                "u": u,
                "w": w,
                "solver": "kissat-win64-release-4.0.4-embedded-4.0.0",
                "status": status,
                "bounded_wall_seconds": runtime,
                "solver_exit_code": process.returncode,
            }
            if status == "SAT":
                model_path = args.models_dir / f"u{u:02d}_w{w:02d}.kissat.model"
                rerun = subprocess.run(
                    [str(solver), "--sat", str(case_path.resolve())],
                    capture_output=True,
                    text=True,
                    timeout=args.timeout,
                )
                model_path.write_text(rerun.stdout, encoding="utf-8")
                if rerun.returncode != 10:
                    record["model_rerun_error"] = {
                        "returncode": rerun.returncode,
                        "stderr": rerun.stderr[-2000:],
                    }
                    record["status"] = "ERROR"
                else:
                    blue = parse_kissat_model(model_path, 15)
                    validation = validate_coloring(15, blue)
                    validation["forced_induced_P3_holds"] = (
                        (0, u) in blue and (0, w) in blue and (u, w) not in blue
                    )
                    record["model_path"] = str(model_path.resolve())
                    record["validation"] = validation
            elif status == "ERROR":
                record["stdout"] = process.stdout[-2000:]
                record["stderr"] = process.stderr[-2000:]
        except subprocess.TimeoutExpired:
            record = {
                "center": 0,
                "u": u,
                "w": w,
                "solver": "kissat-win64-release-4.0.4-embedded-4.0.0",
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
        "kissat_executable": str(solver),
        "kissat_executable_sha256": sha256(solver.read_bytes()).hexdigest(),
        "kissat_release_url": "https://github.com/sfiruch/kissat/releases/tag/4.0.4",
        "kissat_embedded_version": "4.0.0",
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

