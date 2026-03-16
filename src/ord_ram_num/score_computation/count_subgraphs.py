from . import subgraph
from typing import Literal, Optional

def _test_cython():
    k5 = [30, 29, 27, 23, 15] + [0] * 59
    k3 = [6, 5, 3] + [0] * 61
    last = 5 + 3 * 256

    result = subgraph.count_subgraphs(k5 + k3 + [last])
    print(result)

def _test_cython_batch():
    n_big = 100
    k7 = [0] * 64
    for i in range(7):
        k7[i] = 2**7 - 1 - 2**i
    desc = 7 + 256 * 0 + 65536 * n_big
    k17 = [0] * 64
    for i in range(17):
        k17[i] = 2**17 - 1 - 2**i
    big_desc = 17

    result = subgraph.count_subgraphs_batch(k7 + [desc] + ([big_desc] + k17) * n_big)
    print(result)

type Mode = Literal['distinct', 'increasing', 'cyclic']
type GraphEdges = list[tuple[int, int]]
type RequiredEdge = Optional[tuple[int, int]]

# Returns an ints array of length 64 and the graph size, deduced from edge set.
def _unpack_graph(edges: GraphEdges) -> tuple[list[int], int]:
    n = 0
    adj = [0] * 64
    for u, v in edges:
        n = max(n, u, v)
        adj[u] |= 2 ** v
        adj[v] |= 2 ** u
    return (adj, n + 1)

def _parse_mode(mode: Mode):
    if mode == 'distinct':
        return 0
    elif mode == 'increasing':
        return 1
    elif mode == 'cyclic':
        return 2
    else:
        raise RuntimeError("invalid mode")

def _condense_extra_args(
        mode: Mode,
        req_edge: RequiredEdge = None):
    result = _parse_mode(mode) * 2**16

    if req_edge is not None:
        result += req_edge[0] * 2 ** 24 + req_edge[1] * 2 ** 32
    
    return result

def count_subgraphs(
        big_edges: GraphEdges,
        small_edges: GraphEdges,
        mode: Mode = 'distinct',
        req_edge: Optional[tuple[int, int]] = None) -> int:
    big, big_n = _unpack_graph(big_edges)
    small, small_n = _unpack_graph(small_edges)
    mode = _condense_extra_args(mode=mode, req_edge=req_edge)
    return subgraph.count_subgraphs(big + small + [mode + big_n + small_n * 2**8])

def count_subgraphs_batch(
        big_graphs: list[(GraphEdges, RequiredEdge)],
        small_edges: GraphEdges,
        mode: Mode = 'distinct') -> list[int]:
    
    args, small_n = _unpack_graph(small_edges)
    args += [small_n + _parse_mode(mode) * 2**8 + len(big_graphs) * 2**16]

    for big_edges, req_edge in big_graphs:
        big, big_n = _unpack_graph(big_edges)
        big_desc = big_n
        if req_edge is not None:
            big_desc += req_edge[0] * 2**8 + req_edge[1] * 2**16
        args += [big_desc]
        args += big

    return subgraph.count_subgraphs_batch(args)

def _complete_graph(n):
    edges = []
    for i in range(n):
        for j in range(i):
            edges.append((i, j))
    return edges

def _test_wrapper():
    big_edges = _complete_graph(17)
    small_edges = _complete_graph(7)
    print(count_subgraphs(big_edges=big_edges, small_edges=small_edges))
    print(count_subgraphs(big_edges=big_edges, small_edges=small_edges, mode='increasing'))
    print(count_subgraphs(big_edges=big_edges, small_edges=small_edges, req_edge=(4, 12)))

def _test_wrapper_batch():
    big_edges = _complete_graph(17)
    small_edges = _complete_graph(7)
    print(count_subgraphs_batch(
        big_graphs=[(big_edges, None)] * 100,
        small_edges=small_edges,
        mode='distinct'
    ))

def _test_wrapper_batch_complex():
    # How many 12-cycles contain a particular edge of an 8 x 8 grid?
    big_edges = []
    grid_n = 8
    cycle_n = 12
    for i in range(grid_n):
        for j in range(grid_n):
            u = i + grid_n * j
            if i + 1 != grid_n:
                big_edges.append((u, u + 1))
            if j + 1 != grid_n:
                big_edges.append((u, u + grid_n))
    big_graphs = []
    for edge in big_edges:
        big_graphs.append((big_edges, edge))
    small_edges = [(i, (i + 1) % cycle_n) for i in range(cycle_n)]

    batch = count_subgraphs_batch(big_graphs=big_graphs, small_edges=small_edges, mode='distinct')
    print('batch done')

    individual = [
        count_subgraphs(
            big_edges=big_edges,
            small_edges=small_edges,
            mode='distinct',
            req_edge=edge) for edge in big_edges]
    
    if batch == individual:
        print('OK, results match')
        print(batch)
    else:
        print('failed')

# _test_cython()
# _test_cython_batch()
# _test_wrapper()
# _test_wrapper_batch()
# _test_wrapper_batch_complex()
