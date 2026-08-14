#!/usr/bin/env python3
"""Solve one DIMACS instance with a named PySAT backend and emit JSON."""

from argparse import ArgumentParser
import json
from pathlib import Path
from time import perf_counter

from pysat.solvers import Solver

from cyclic_a6 import edge_var, read_dimacs, validate_coloring


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("cnf", type=Path)
    parser.add_argument("--solver", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    _, clauses = read_dimacs(args.cnf)
    started = perf_counter()
    with Solver(name=args.solver, bootstrap_with=clauses) as solver:
        satisfiable = solver.solve()
        record: dict[str, object] = {
            "status": "SAT" if satisfiable else "UNSAT",
            "solver": args.solver,
            "runtime_seconds": perf_counter() - started,
            "solver_stats": solver.accum_stats(),
        }
        if satisfiable:
            model = solver.get_model()
            positive = {literal for literal in model if literal > 0}
            blue = {
                (u, v)
                for u in range(15)
                for v in range(u + 1, 15)
                if edge_var(15, u, v) in positive
            }
            record["model"] = model
            record["validation"] = validate_coloring(15, blue)
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()

