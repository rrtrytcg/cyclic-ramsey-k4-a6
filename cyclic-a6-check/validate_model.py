#!/usr/bin/env python3
"""Independently validate a Kissat model or graph6 coloring."""

from argparse import ArgumentParser
import json
from pathlib import Path

from cyclic_a6 import parse_graph6, parse_kissat_model, validate_coloring


def main() -> None:
    parser = ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--kissat-output", type=Path)
    source.add_argument("--graph6", type=Path)
    parser.add_argument("--order", type=int, default=15)
    parser.add_argument("--require-valid", action="store_true")
    args = parser.parse_args()

    if args.kissat_output:
        n = args.order
        blue = parse_kissat_model(args.kissat_output, n)
    else:
        n, blue = parse_graph6(args.graph6)
    result = validate_coloring(n, blue)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.require_valid and not (result["no_red_K4"] and result["no_blue_cyclic_A6"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

