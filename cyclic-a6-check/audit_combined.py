#!/usr/bin/env python3
"""Independently reconstruct and audit the selectors-first combined CNF."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

from cyclic_a6 import base_clauses, canonical_clause, edge_var, read_dimacs


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("cnf", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    selector_count = 91
    edge_offset = selector_count
    pairs = list(combinations(range(1, 15), 2))
    expected_base = [
        tuple((1 if lit > 0 else -1) * (abs(lit) + edge_offset) for lit in clause)
        for clause in base_clauses(15, deduplicate=False)
    ]
    expected_implications: list[tuple[int, ...]] = []
    for selector, (u, w) in enumerate(pairs, start=1):
        expected_implications.extend(
            (
                (-selector, edge_var(15, 0, u) + edge_offset),
                (-selector, edge_var(15, 0, w) + edge_offset),
                (-selector, -(edge_var(15, u, w) + edge_offset)),
            )
        )
    expected_at_least_one = [tuple(range(1, selector_count + 1))]
    expected_at_most_one = [(-left, -right) for left, right in combinations(range(1, selector_count + 1), 2)]
    expected = expected_base + expected_implications + expected_at_least_one + expected_at_most_one

    nvars, actual_raw = read_dimacs(args.cnf)
    actual = Counter(canonical_clause(clause) for clause in actual_raw)
    expected_counter = Counter(canonical_clause(clause) for clause in expected)
    result = {
        "cnf": str(args.cnf.resolve()),
        "variables": nvars,
        "actual_raw_clauses": len(actual_raw),
        "expected_raw_clauses": len(expected),
        "base_clauses": len(expected_base),
        "selector_implication_clauses": len(expected_implications),
        "at_least_one_clauses": len(expected_at_least_one),
        "at_most_one_clauses": len(expected_at_most_one),
        "canonical_multiset_equal": actual == expected_counter,
        "actual_only": len(actual.keys() - expected_counter.keys()),
        "expected_only": len(expected_counter.keys() - actual.keys()),
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(text, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    if nvars != 196 or len(actual_raw) != 39859 or actual != expected_counter:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

