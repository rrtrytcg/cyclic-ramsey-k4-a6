#!/usr/bin/env python3
"""Solve all 91 induced-blue-P3 cases centered at vertex 0."""

from __future__ import annotations

from argparse import ArgumentParser
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
from importlib.metadata import version
from itertools import combinations
import json
import multiprocessing
import os
from pathlib import Path
from time import perf_counter

from pysat.solvers import Solver

from cyclic_a6 import edge_var, read_dimacs, validate_coloring


_CLAUSES: list[tuple[int, ...]] = []


def initialize_worker(base_path: str) -> None:
    global _CLAUSES
    _, _CLAUSES = read_dimacs(Path(base_path))


def solve_case(solver_name: str, u: int, w: int) -> dict[str, object]:
    forced_units = [edge_var(15, 0, u), edge_var(15, 0, w), -edge_var(15, u, w)]
    started = perf_counter()
    with Solver(name=solver_name, bootstrap_with=_CLAUSES) as solver:
        for literal in forced_units:
            solver.add_clause([literal])
        satisfiable = solver.solve()
        elapsed = perf_counter() - started
        stats = solver.accum_stats()
        model = solver.get_model() if satisfiable else None

    record: dict[str, object] = {
        "center": 0,
        "u": u,
        "w": w,
        "forced_units": forced_units,
        "status": "SAT" if satisfiable else "UNSAT",
        "runtime_seconds": elapsed,
        "solver_stats": stats,
    }
    if model is not None:
        positive = {literal for literal in model if literal > 0}
        blue = {
            (a, b)
            for a in range(15)
            for b in range(a + 1, 15)
            if edge_var(15, a, b) in positive
        }
        validation = validate_coloring(15, blue)
        validation["forced_induced_P3_holds"] = (
            (0, u) in blue and (0, w) in blue and (min(u, w), max(u, w)) not in blue
        )
        record["model"] = model
        record["validation"] = validation
    return record


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path("artifacts/base/authors_base_raw.cnf"))
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1))
    parser.add_argument("--output", type=Path, default=Path("artifacts/results_91.json"))
    parser.add_argument("--checkpoint", type=Path, default=Path("artifacts/results_91.checkpoint.jsonl"))
    args = parser.parse_args()
    base = args.base.resolve()
    base_hash = sha256(base.read_bytes()).hexdigest()
    cases = list(combinations(range(1, 15), 2))
    records: list[dict[str, object]] = []
    started = perf_counter()

    if args.workers == 1:
        initialize_worker(str(base))
        completed_records = (
            solve_case(args.solver, u, w) for u, w in cases
        )
        for completed, record in enumerate(completed_records, 1):
            records.append(record)
            args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
            with args.checkpoint.open("a", encoding="utf-8") as checkpoint:
                checkpoint.write(json.dumps(record, sort_keys=True) + "\n")
            print(
                f"[{completed:02d}/91] ({record['u']:02d},{record['w']:02d}) "
                f"{record['status']} {record['runtime_seconds']:.3f}s",
                flush=True,
            )
    else:
        with ProcessPoolExecutor(
            max_workers=args.workers,
            initializer=initialize_worker,
            initargs=(str(base),),
        ) as executor:
            futures = {
                executor.submit(solve_case, args.solver, u, w): (u, w)
                for u, w in cases
            }
            for completed, future in enumerate(as_completed(futures), 1):
                record = future.result()
                records.append(record)
                args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
                with args.checkpoint.open("a", encoding="utf-8") as checkpoint:
                    checkpoint.write(json.dumps(record, sort_keys=True) + "\n")
                print(
                    f"[{completed:02d}/91] ({record['u']:02d},{record['w']:02d}) "
                    f"{record['status']} {record['runtime_seconds']:.3f}s",
                    flush=True,
                )

    records.sort(key=lambda item: (item["u"], item["w"]))
    summary = {
        "schema_version": 1,
        "base_cnf": str(base),
        "base_cnf_sha256": base_hash,
        "python_sat_version": version("python-sat"),
        "solver": args.solver,
        "workers": args.workers,
        "case_count": len(records),
        "sat_count": sum(record["status"] == "SAT" for record in records),
        "unsat_count": sum(record["status"] == "UNSAT" for record in records),
        "wall_runtime_seconds": perf_counter() - started,
        "cases": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("case_count", "sat_count", "unsat_count", "wall_runtime_seconds")}, indent=2))
    if len(records) != 91 or summary["sat_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
