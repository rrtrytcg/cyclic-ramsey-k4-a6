#!/usr/bin/env python3
"""Checkpointed 91-case sweep using a proof-capable external SAT solver."""

from __future__ import annotations

from argparse import ArgumentParser
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
from time import perf_counter

from cyclic_a6 import edge_var, parse_kissat_model, read_dimacs, validate_coloring, write_dimacs


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--solver", type=Path, required=True)
    parser.add_argument("--base", type=Path, default=Path("artifacts/base/authors_base_raw.cnf"))
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--checkpoint", type=Path, default=Path("artifacts/external_91.checkpoint.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/results_91_external.json"))
    parser.add_argument("--cases-dir", type=Path, default=Path("artifacts/cases"))
    parser.add_argument("--models-dir", type=Path, default=Path("artifacts/models"))
    parser.add_argument("--no-unsat-config", action="store_true")
    args = parser.parse_args()

    solver = args.solver.resolve()
    base = args.base.resolve()
    nvars, base_clauses = read_dimacs(base)
    completed: dict[tuple[int, int], dict[str, object]] = {}
    if args.checkpoint.exists():
        for line in args.checkpoint.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            completed[(record["u"], record["w"])] = record

    args.cases_dir.mkdir(parents=True, exist_ok=True)
    args.models_dir.mkdir(parents=True, exist_ok=True)
    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    cases = list(combinations(range(1, 15), 2))
    started_all = perf_counter()

    for index, (u, w) in enumerate(cases, 1):
        if (u, w) in completed and completed[(u, w)]["status"] in {"SAT", "UNSAT"}:
            print(f"[{index:02d}/91] ({u:02d},{w:02d}) cached {completed[(u, w)]['status']}", flush=True)
            continue
        units = [edge_var(15, 0, u), edge_var(15, 0, w), -edge_var(15, u, w)]
        case_path = args.cases_dir / f"u{u:02d}_w{w:02d}.cnf"
        model_path = args.models_dir / f"u{u:02d}_w{w:02d}.model"
        write_dimacs(case_path, nvars, base_clauses + [(literal,) for literal in units])
        command = [str(solver)]
        if not args.no_unsat_config:
            command.append("--unsat")
        command.extend(["-q", "-w", str(model_path), str(case_path)])
        started = perf_counter()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout)
            runtime = perf_counter() - started
            status = {10: "SAT", 20: "UNSAT"}.get(process.returncode, "ERROR")
            record: dict[str, object] = {
                "center": 0,
                "u": u,
                "w": w,
                "forced_units": units,
                "status": status,
                "runtime_seconds": runtime,
                "solver_exit_code": process.returncode,
                "case_cnf": str(case_path.resolve()),
                "case_cnf_sha256": sha256(case_path.read_bytes()).hexdigest(),
            }
            if status == "SAT":
                blue = parse_kissat_model(model_path, 15)
                validation = validate_coloring(15, blue)
                validation["forced_induced_P3_holds"] = (
                    (0, u) in blue and (0, w) in blue and (u, w) not in blue
                )
                record["validation"] = validation
            elif status == "ERROR":
                record["stdout"] = process.stdout[-4000:]
                record["stderr"] = process.stderr[-4000:]
        except subprocess.TimeoutExpired:
            runtime = perf_counter() - started
            record = {
                "center": 0,
                "u": u,
                "w": w,
                "forced_units": units,
                "status": "TIMEOUT",
                "runtime_seconds": runtime,
                "case_cnf": str(case_path.resolve()),
                "case_cnf_sha256": sha256(case_path.read_bytes()).hexdigest(),
            }
        completed[(u, w)] = record
        with args.checkpoint.open("a", encoding="utf-8") as checkpoint:
            checkpoint.write(json.dumps(record, sort_keys=True) + "\n")
        print(f"[{index:02d}/91] ({u:02d},{w:02d}) {record['status']} {record['runtime_seconds']:.3f}s", flush=True)

    records = [completed[pair] for pair in cases]
    summary = {
        "schema_version": 1,
        "base_cnf": str(base),
        "base_cnf_sha256": sha256(base.read_bytes()).hexdigest(),
        "solver": str(solver),
        "solver_sha256": sha256(solver.read_bytes()).hexdigest(),
        "timeout_seconds": args.timeout,
        "case_count": len(records),
        "sat_count": sum(r["status"] == "SAT" for r in records),
        "unsat_count": sum(r["status"] == "UNSAT" for r in records),
        "timeout_count": sum(r["status"] == "TIMEOUT" for r in records),
        "error_count": sum(r["status"] == "ERROR" for r in records),
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

