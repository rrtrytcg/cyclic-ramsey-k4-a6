#!/usr/bin/env python3
"""Append one induced-blue-P3 unit-clause triple to the fixed base CNF."""

from argparse import ArgumentParser
from pathlib import Path

from cyclic_a6 import edge_var, read_dimacs, write_dimacs


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("u", type=int)
    parser.add_argument("w", type=int)
    parser.add_argument("output", type=Path)
    parser.add_argument("--base", type=Path, default=Path("artifacts/base/authors_base_raw.cnf"))
    args = parser.parse_args()
    if not (1 <= args.u < args.w <= 14):
        parser.error("require 1 <= u < w <= 14")
    nvars, clauses = read_dimacs(args.base)
    units = [edge_var(15, 0, args.u), edge_var(15, 0, args.w), -edge_var(15, args.u, args.w)]
    clauses.extend((literal,) for literal in units)
    write_dimacs(args.output, nvars, clauses)
    print(f"wrote case ({args.u},{args.w}) with units {units} to {args.output}")


if __name__ == "__main__":
    main()

