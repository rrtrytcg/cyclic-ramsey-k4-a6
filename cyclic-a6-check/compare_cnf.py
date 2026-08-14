#!/usr/bin/env python3
"""Canonical clause-set and multiset comparison for two DIMACS files."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path

from cyclic_a6 import canonical_clause, read_dimacs


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    args = parser.parse_args()

    left_vars, left_raw = read_dimacs(args.left)
    right_vars, right_raw = read_dimacs(args.right)
    left = Counter(canonical_clause(clause) for clause in left_raw)
    right = Counter(canonical_clause(clause) for clause in right_raw)
    left_set, right_set = set(left), set(right)

    print(f"left:  vars={left_vars} raw={len(left_raw)} unique={len(left_set)} sha256={digest(args.left)}")
    print(f"right: vars={right_vars} raw={len(right_raw)} unique={len(right_set)} sha256={digest(args.right)}")
    print(f"canonical_set_equal={left_set == right_set}")
    print(f"canonical_multiset_equal={left == right}")
    print(f"left_only={len(left_set - right_set)} right_only={len(right_set - left_set)}")
    if left_vars != right_vars or left_set != right_set:
        for label, difference in (("left_only", left_set - right_set), ("right_only", right_set - left_set)):
            for clause in sorted(difference)[:5]:
                print(f"{label}: {clause}")
        raise SystemExit(1)
    if left != right:
        print("warning: canonical sets agree, but duplicate multiplicities differ")


if __name__ == "__main__":
    main()

