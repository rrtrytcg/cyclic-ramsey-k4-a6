#!/usr/bin/env python3

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import unittest

from cyclic_a6 import A6_EDGES, base_clauses, cyclic_embeddings, edge_var, parse_graph6, parse_kissat_model, validate_coloring


ROOT = Path(__file__).resolve().parent


class PipelineTests(unittest.TestCase):
    def test_edge_variables_are_exactly_1_through_105(self) -> None:
        variables = [edge_var(15, u, v) for u in range(15) for v in range(u + 1, 15)]
        self.assertEqual(variables, list(range(1, 106)))

    def test_cyclic_embeddings_do_not_add_reflection(self) -> None:
        rotations = []
        for sequence in cyclic_embeddings(6, 6):
            rotations.append(frozenset(tuple(sorted((sequence[u], sequence[v]))) for u, v in A6_EDGES))
        reflected = frozenset(tuple(sorted(((-u) % 6, (-v) % 6))) for u, v in A6_EDGES)
        self.assertEqual(len(rotations), 6)
        self.assertEqual(len(set(rotations)), 3)
        self.assertNotIn(reflected, set(rotations))

    def test_base_clause_counts(self) -> None:
        raw = base_clauses(15, deduplicate=False)
        self.assertEqual(len(raw), 35490)
        self.assertEqual(len(set(raw)), 16380)

    def test_archived_witness_agrees_in_both_formats(self) -> None:
        output = ROOT.parent / "kissat_output/k_palt_cyc/k04_palt06_cyc_15.txt"
        graph6 = ROOT.parent / "parsed_graphs/k_palt_cyc/k04_palt06_cyc_15.g6"
        model_blue = parse_kissat_model(output, 15)
        order, graph6_blue = parse_graph6(graph6)
        self.assertEqual(order, 15)
        self.assertEqual(model_blue, graph6_blue)
        validation = validate_coloring(15, model_blue)
        self.assertTrue(validation["no_red_K4"])
        self.assertTrue(validation["no_blue_cyclic_A6"])
        self.assertTrue(validation["is_3K5"])

    def test_final_91_result_is_complete(self) -> None:
        result = json.loads((ROOT / "artifacts/results_91_portfolio.json").read_text(encoding="utf-8"))
        self.assertEqual(result["case_count"], 91)
        self.assertEqual(result["sat_count"], 0)
        self.assertEqual(result["unsat_count"], 91)
        self.assertEqual(result["timeout_count"], 0)
        self.assertEqual(result["error_count"], 0)
        self.assertEqual(
            {(case["u"], case["w"]) for case in result["cases"]},
            set(combinations(range(1, 15), 2)),
        )
        self.assertTrue(all(case["status"] == "UNSAT" for case in result["cases"]))


if __name__ == "__main__":
    unittest.main()

