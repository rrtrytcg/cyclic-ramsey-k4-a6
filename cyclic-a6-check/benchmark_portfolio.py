#!/usr/bin/env python3
"""Run bounded PySAT backends on one case to select a solver portfolio."""

from argparse import ArgumentParser
import json
from pathlib import Path
import subprocess
from time import perf_counter


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("cnf", type=Path)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument(
        "--solvers",
        nargs="+",
        default=["cadical195", "glucose4", "lingeling", "maplechrono", "maplesat"],
    )
    args = parser.parse_args()
    records = []
    for solver in args.solvers:
        command = [str(args.python.resolve()), "solve_one_pysat.py", str(args.cnf.resolve()), "--solver", solver]
        started = perf_counter()
        try:
            process = subprocess.run(command, capture_output=True, text=True, timeout=args.timeout)
            if process.returncode == 0:
                record = json.loads(process.stdout)
            else:
                record = {
                    "status": "ERROR",
                    "solver": solver,
                    "returncode": process.returncode,
                    "stdout": process.stdout[-2000:],
                    "stderr": process.stderr[-2000:],
                }
        except subprocess.TimeoutExpired:
            record = {"status": "TIMEOUT", "solver": solver}
        record["bounded_wall_seconds"] = perf_counter() - started
        records.append(record)
        print(json.dumps(record, sort_keys=True), flush=True)
    print(json.dumps(records, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

