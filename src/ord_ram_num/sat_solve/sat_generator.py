import sys
from itertools import combinations


class Graph:
    def __init__(self, order, edges):
        self.order = order
        self.edges = edges


class MonotonePath(Graph):
    def __init__(self, order):
        edges = []
        for i in range(order - 1):
            edges.append((i, i + 1))
        
        super().__init__(order, edges)


class AlternatingPath(Graph):
    def __init__(self, order):
        edges = []
        vertex_sum = order - 1
        current_vertex = 0

        for _ in range(order - 1):
            next_vertex = vertex_sum - current_vertex
            edges.append((current_vertex, next_vertex))

            current_vertex = next_vertex
            vertex_sum = 2 * order - 1 - vertex_sum
        
        super().__init__(order, edges)


class ReverseAlternatingPath(Graph):
    def __init__(self, order):
        edges = []
        vertex_sum = order - 1
        current_vertex = order - 1

        for _ in range(order - 1):
            next_vertex = vertex_sum - current_vertex
            edges.append((current_vertex, next_vertex))

            current_vertex = next_vertex
            vertex_sum = 2 * order - 3 - vertex_sum

        super().__init__(order, edges)


class MonotoneCycle(Graph):
    def __init__(self, order):
        edges = []
        for i in range(order - 1):
            edges.append((i, i + 1))
        
        edges.append((order - 1, 0))

        super().__init__(order, edges)


class StartCentralStar(Graph):
    def __init__(self, order):
        edges = []
        for i in range(1, order):
            edges.append((0, i))
        
        super().__init__(order, edges)


class NestedMatching(Graph):
    def __init__(self, order):
        assert order % 2 == 0

        edges = []
        for i in range(order // 2):
            edges.append((i, order - 1 - i))

        super().__init__(order, edges)


class CompleteGraph(Graph):
    def __init__(self, order):
        edges = []
        for i in range(order - 1):
            for j in range(i + 1, order):
                edges.append((i, j))
        
        super().__init__(order, edges)


def generate_sat_problem(
    order: int,
    pattern_1: Graph,
    pattern_2: Graph,
    rotation: bool = False,
    reflection: bool = False,
):
    variables_num = order * (order - 1) // 2
    clauses_num = 0
    all_clauses = []
    
    for sequence_basis in combinations(range(order), pattern_1.order):
        sequences = [sequence_basis]

        if reflection:
            sequences.append(sequence_basis[::-1])

        if rotation:
            additional_sequences = []
            for i in range(1, pattern_1.order):
                for sequence in sequences:
                    rotated_sequence = sequence[i:] + sequence[:i]
                    additional_sequences.append(rotated_sequence)
            
            sequences += additional_sequences

        for sequence in sequences:
            clause = ""

            for (u, v) in pattern_1.edges:
                smaller = min(sequence[u], sequence[v])
                bigger = max(sequence[u], sequence[v])
                
                edge_index = smaller * (2 * order - 1 - smaller) // 2 + (bigger - smaller)

                clause += f"{edge_index} "
       
            clause += "0"
            all_clauses.append(clause)
            clauses_num += 1
    
    for sequence_basis in combinations(range(order), pattern_2.order):
        sequences = [sequence_basis]

        if reflection:
            sequences.append(sequence_basis[::-1])

        if rotation:
            additional_sequences = []
            for i in range(1, pattern_2.order):
                for sequence in sequences:
                    rotated_sequence = sequence[i:] + sequence[:i]
                    additional_sequences.append(rotated_sequence)
            
            sequences += additional_sequences

        for sequence in sequences:
            clause = ""

            for (u, v) in pattern_2.edges:
                smaller = min(sequence[u], sequence[v])
                bigger = max(sequence[u], sequence[v])

                edge_index = smaller * (2 * order - 1 - smaller) // 2 + (bigger - smaller)

                clause += f"-{edge_index} "
       
            clause += "0"
            all_clauses.append(clause)
            clauses_num += 1

    print(f"p cnf {variables_num} {clauses_num}")
    for clause in all_clauses:
        print(clause)


if __name__ == "__main__":
    pattern = Graph(5, [(0, 3), (0, 4), (1, 3), (1, 4), (2, 4)])

    generate_sat_problem(
        order=int(sys.argv[1]),
        pattern_1=pattern,
        pattern_2=pattern,
        rotation=False,
        reflection=False,
    )