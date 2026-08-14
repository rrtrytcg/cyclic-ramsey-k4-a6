"""Independent definitions for cyclic K4 versus alternating A6 SAT checks."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import Iterable, Iterator, Sequence


A6_EDGES = ((0, 5), (5, 1), (1, 4), (4, 2), (2, 3))


def edge_var(n: int, u: int, v: int) -> int:
    """Return the authors' 1-based DIMACS variable for the unordered edge uv."""
    if u == v:
        raise ValueError("loops have no edge variable")
    if u > v:
        u, v = v, u
    return u * (2 * n - 1 - u) // 2 + (v - u)


def cyclic_embeddings(n: int, k: int) -> Iterator[tuple[int, ...]]:
    """Enumerate orientation-preserving cyclic embeddings, without reflections."""
    for chosen in combinations(range(n), k):
        for shift in range(k):
            yield chosen[shift:] + chosen[:shift]


def canonical_clause(clause: Iterable[int]) -> tuple[int, ...]:
    return tuple(sorted(set(clause), key=lambda lit: (abs(lit), lit < 0)))


def base_clauses(n: int = 15, *, deduplicate: bool = False) -> list[tuple[int, ...]]:
    """Encode no red K4 and no blue cyclic A6 using positive=blue variables."""
    clauses: list[tuple[int, ...]] = []

    # Match the authors' cyclic generator literally: it emits four rotations for K4.
    for sequence in cyclic_embeddings(n, 4):
        clause = tuple(
            edge_var(n, sequence[i], sequence[j])
            for i in range(4)
            for j in range(i + 1, 4)
        )
        clauses.append(canonical_clause(clause))

    for sequence in cyclic_embeddings(n, 6):
        clause = tuple(-edge_var(n, sequence[u], sequence[v]) for u, v in A6_EDGES)
        clauses.append(canonical_clause(clause))

    if deduplicate:
        return sorted(set(clauses))
    return clauses


def write_dimacs(path: Path, nvars: int, clauses: Sequence[Sequence[int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {nvars} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)))
            handle.write(" 0\n")


def read_dimacs(path: Path) -> tuple[int, list[tuple[int, ...]]]:
    nvars = None
    declared = None
    clauses: list[tuple[int, ...]] = []
    pending: list[int] = []
    with path.open("r", encoding="ascii") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p"):
                _, fmt, nvars_text, declared_text = line.split()
                if fmt != "cnf":
                    raise ValueError(f"unsupported DIMACS format {fmt!r}")
                nvars = int(nvars_text)
                declared = int(declared_text)
                continue
            for token in map(int, line.split()):
                if token == 0:
                    clauses.append(tuple(pending))
                    pending.clear()
                else:
                    pending.append(token)
    if pending:
        raise ValueError("unterminated DIMACS clause")
    if nvars is None or declared is None:
        raise ValueError("missing DIMACS header")
    if declared != len(clauses):
        raise ValueError(f"header declares {declared} clauses, parsed {len(clauses)}")
    return nvars, clauses


def parse_kissat_model(path: Path, n: int) -> set[tuple[int, int]]:
    literals: list[int] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            if raw.startswith("v "):
                literals.extend(int(token) for token in raw[2:].split() if token != "0")
    if not literals:
        raise ValueError(f"no model lines found in {path}")
    positive = {lit for lit in literals if lit > 0}
    return {
        (u, v)
        for u in range(n)
        for v in range(u + 1, n)
        if edge_var(n, u, v) in positive
    }


def parse_graph6(path: Path) -> tuple[int, set[tuple[int, int]]]:
    data = path.read_text(encoding="ascii").strip()
    if not data or data.startswith(">>"):
        raise ValueError("only a single short graph6 record is supported")
    n = ord(data[0]) - 63
    if not 0 <= n <= 62:
        raise ValueError("only graph6 orders up to 62 are supported")
    bits = "".join(f"{ord(char) - 63:06b}" for char in data[1:])
    edges: set[tuple[int, int]] = set()
    cursor = 0
    for v in range(1, n):
        for u in range(v):
            if bits[cursor] == "1":
                edges.add((u, v))
            cursor += 1
    return n, edges


def blue_components(n: int, blue: set[tuple[int, int]]) -> list[list[int]]:
    adjacency = [set() for _ in range(n)]
    for u, v in blue:
        adjacency[u].add(v)
        adjacency[v].add(u)
    unseen = set(range(n))
    components: list[list[int]] = []
    while unseen:
        stack = [unseen.pop()]
        component: list[int] = []
        while stack:
            u = stack.pop()
            component.append(u)
            neighbors = adjacency[u] & unseen
            unseen.difference_update(neighbors)
            stack.extend(neighbors)
        components.append(sorted(component))
    return sorted(components, key=lambda part: (-len(part), part))


def validate_coloring(n: int, blue: set[tuple[int, int]]) -> dict[str, object]:
    def is_blue(u: int, v: int) -> bool:
        return (min(u, v), max(u, v)) in blue

    red_k4 = None
    for vertices in combinations(range(n), 4):
        if all(not is_blue(u, v) for u, v in combinations(vertices, 2)):
            red_k4 = list(vertices)
            break

    blue_a6 = None
    for sequence in cyclic_embeddings(n, 6):
        if all(is_blue(sequence[u], sequence[v]) for u, v in A6_EDGES):
            blue_a6 = list(sequence)
            break

    induced_p3 = None
    for center in range(n):
        neighbors = [v for v in range(n) if v != center and is_blue(center, v)]
        for u, w in combinations(neighbors, 2):
            if not is_blue(u, w):
                induced_p3 = [u, center, w]
                break
        if induced_p3 is not None:
            break

    components = blue_components(n, blue)
    clique_components = all(
        all(is_blue(u, v) for u, v in combinations(component, 2))
        for component in components
    )
    return {
        "order": n,
        "blue_edge_count": len(blue),
        "no_red_K4": red_k4 is None,
        "red_K4_witness": red_k4,
        "no_blue_cyclic_A6": blue_a6 is None,
        "blue_cyclic_A6_witness": blue_a6,
        "contains_induced_blue_P3": induced_p3 is not None,
        "induced_blue_P3_witness": induced_p3,
        "blue_components": components,
        "blue_component_sizes": [len(component) for component in components],
        "all_blue_components_are_cliques": clique_components,
        "is_3K5": n == 15 and clique_components and [len(c) for c in components] == [5, 5, 5],
    }

