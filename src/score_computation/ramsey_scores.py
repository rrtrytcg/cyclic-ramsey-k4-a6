from typing import List
from enum import Enum

import numpy as np

from rlgt.graphs.graph import Graph
from .subgraph import count_subgraphs_batch


def __call_cpp_func(big_graphs, small_graph, mode: int):
    big_cnt, big_n = big_graphs.shape
    args = np.zeros(65 * (1 + big_cnt), dtype=np.uint64)
    small_n = small_graph.shape[0]
    args[:small_n] = small_graph
    args[64] = small_n + mode * 2**8 + big_cnt * 2**16
    for i in range(big_cnt):
        args[65 * (i + 1)] = big_n
        args[65 * (i + 1) + 1 : 65 * (i + 1) + 1 + big_n] = big_graphs[i, :]
    return count_subgraphs_batch(args)


class RamseyScoreType(Enum):
    STANDARD = 0
    ORDERED = 1
    CYCLIC = 2


def compute_ramsey_score(
    input_graph_batch: Graph,
    pattern_graph_list: List[Graph],
    ramsey_score_type: RamseyScoreType = RamseyScoreType.STANDARD,
) -> np.ndarray:
    mode = ramsey_score_type.value
    score_batch = np.zeros((input_graph_batch.batch_size), dtype=np.float32)

    if input_graph_batch.bitmask_out.shape[-2] == input_graph_batch.edge_colors:
        zero_bitmask = input_graph_batch.bitmask_out[:, 0, :]
    else:
        order = input_graph_batch.graph_order
        temp = (1 << order) - 1 - (1 << np.arange(order, dtype=np.uint64))
        zero_bitmask = temp - np.sum(input_graph_batch.bitmask_out, axis=1)

    zero_pattern = pattern_graph_list[0].bitmask_out[-1]
    score_batch += __call_cpp_func(zero_bitmask, zero_pattern, mode)

    for color_index in range(1, input_graph_batch.edge_colors):
        current_bitmask = input_graph_batch.bitmask_out[
            :, -input_graph_batch.edge_colors + color_index, :
        ]
        current_pattern = pattern_graph_list[color_index].bitmask_out[-1]

        score_batch += __call_cpp_func(current_bitmask, current_pattern, mode)

    return score_batch
