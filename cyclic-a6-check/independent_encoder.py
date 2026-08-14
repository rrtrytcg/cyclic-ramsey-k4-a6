#!/usr/bin/env python3
"""Generate the cyclic K4 versus alternating A6 CNF from first principles."""

from argparse import ArgumentParser
from pathlib import Path

from cyclic_a6 import base_clauses, write_dimacs


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--order", type=int, default=15)
    parser.add_argument("--deduplicate", action="store_true")
    args = parser.parse_args()
    clauses = base_clauses(args.order, deduplicate=args.deduplicate)
    write_dimacs(args.output, args.order * (args.order - 1) // 2, clauses)
    print(f"wrote {len(clauses)} clauses to {args.output}")


if __name__ == "__main__":
    main()

