#!/usr/bin/env python3
"""Encode existence of an induced blue P3 centered at vertex 0 in one CNF."""

from argparse import ArgumentParser
from itertools import combinations
from pathlib import Path

from cyclic_a6 import edge_var, read_dimacs, write_dimacs


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--base", type=Path, default=Path("artifacts/base/authors_base_raw.cnf"))
    parser.add_argument("--selectors-first", action="store_true")
    parser.add_argument("--exactly-one", action="store_true")
    args = parser.parse_args()
    nvars, base_clauses = read_dimacs(args.base)
    pairs = list(combinations(range(1, 15), 2))
    selector_count = len(pairs)
    if args.selectors_first:
        clauses = [
            tuple((1 if literal > 0 else -1) * (abs(literal) + selector_count) for literal in clause)
            for clause in base_clauses
        ]
    else:
        clauses = list(base_clauses)
    selectors: list[int] = []
    for index, (u, w) in enumerate(pairs, start=1):
        selector = index if args.selectors_first else nvars + index
        selectors.append(selector)
        def mapped_edge(literal: int) -> int:
            if not args.selectors_first:
                return literal
            return (1 if literal > 0 else -1) * (abs(literal) + selector_count)
        clauses.extend(
            (
                (-selector, mapped_edge(edge_var(15, 0, u))),
                (-selector, mapped_edge(edge_var(15, 0, w))),
                (-selector, mapped_edge(-edge_var(15, u, w))),
            )
        )
    clauses.append(tuple(selectors))
    if args.exactly_one:
        clauses.extend((-left, -right) for left, right in combinations(selectors, 2))
    write_dimacs(args.output, nvars + selector_count, clauses)
    print(
        f"wrote combined instance: variables={nvars + selector_count} "
        f"clauses={len(clauses)} selectors={selector_count} "
        f"selectors_first={args.selectors_first} exactly_one={args.exactly_one}"
    )


if __name__ == "__main__":
    main()
